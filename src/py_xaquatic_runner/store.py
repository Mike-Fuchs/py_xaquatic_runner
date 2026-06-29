"""
X3df output store (``arr.dat``) reading.

XAquatic writes its results to a self-describing HDF5 store (``arr.dat``): bare
ndarrays whose axis meaning lives in each dataset's attributes (``scales``,
``dim{N}_offset``, ``dim{N}_element_names``, ``unit``). This module reads that
store directly — the contractual source of truth — instead of parsing the
curated reporting CSVs.

Two functions:
    arr_tree(store_path)          -> nested dict describing the whole store
    read_store(store_path, paths) -> labeled pandas object(s) for the listed paths

Discovery → extraction workflow::

    tree = pxr.arr_tree("arr.dat")                 # see what paths exist
    out  = pxr.read_store("arr.dat", [             # extract a chosen list
        "Weather/TEMPERATURE_AVG",
        "StepsRiverNetwork/PEC_SW",
        "CvasiLemLandscape/r.EP50",
    ])
    out["StepsRiverNetwork/PEC_SW"]                # DataFrame: time × reach

Paths are the native HDF5 paths (``/`` separator, segment names verbatim — note
they may contain dots/spaces/brackets, e.g. ``CvasiLemLandscape/BM.EP50``). The
path a node reports in ``arr_tree`` is exactly the path ``read_store`` consumes.
"""

from datetime import datetime
from pathlib import Path
from typing import Any

import h5py
import numpy as np
import pandas as pd

# scale tag -> pandas offset alias for synthesising a regular time index
_TIME_FREQ = {"time/hour": "h", "time/day": "D"}


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _decode(x):
    """HDF5/numpy scalar -> native python (bytes->str, np scalar->python)."""
    if isinstance(x, bytes):
        return x.decode("utf-8", "replace")
    if isinstance(x, np.generic):
        return x.item()
    return x


def _parse_offset(raw):
    """Parse a ``dim{N}_offset`` attr ('2002-01-01 01:00:00' or '2002-01-01')."""
    s = _decode(raw)
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return datetime.fromisoformat(s)


def _axis_index(f, ds, i, n):
    """Resolve a pandas Index for axis ``i`` of dataset ``ds`` (length ``n``).

    time/* -> regular DatetimeIndex from dim{i}_offset; spatial/other ->
    dereference dim{i}_element_names; fallback -> integer RangeIndex.
    """
    a = ds.attrs
    scales = a.get("scales")
    scale = _decode(scales[i]) if scales is not None and i < len(scales) else ""

    if scale in _TIME_FREQ:
        off_key = f"dim{i}_offset"
        if off_key in a:
            start = _parse_offset(a[off_key])
            return pd.date_range(start=start, periods=n, freq=_TIME_FREQ[scale])
        return pd.RangeIndex(n)

    en_key = f"dim{i}_element_names"
    if en_key in a:
        try:
            target = f[a[en_key]]
            return pd.Index([_decode(v) for v in target[...]])
        except Exception:  # noqa: BLE001 — deref is best-effort
            return pd.RangeIndex(n)

    return pd.RangeIndex(n)


def _dataset_meta(ds):
    """Self-describing metadata for a dataset (carried on the result's .attrs)."""
    unit = str(_decode(ds.attrs["unit"])) if "unit" in ds.attrs else None
    scales = [_decode(s) for s in ds.attrs.get("scales", [])] or None
    return {"path": ds.name.lstrip("/"), "unit": unit, "scales": scales}


def _read_one(f, path):
    """Read a single dataset as a labeled pandas object (or scalar / raw ndarray).

    0-D -> python scalar; 1-D -> Series; 2-D -> DataFrame (coordinates resolved
    from attrs). Rank > 2 is returned as the raw ndarray (no 2-D labeling
    possible). The unit/scales/path travel on ``.attrs`` of Series/DataFrame.
    """
    if path not in f or not isinstance(f[path], h5py.Dataset):
        raise KeyError(f"No dataset at '{path}' in store")
    ds = f[path]
    meta = _dataset_meta(ds)

    if ds.ndim == 0:
        return _decode(ds[()])

    if ds.ndim == 1:
        idx = _axis_index(f, ds, 0, ds.shape[0])
        s = pd.Series([_decode(v) for v in ds[...]], index=idx,
                      name=path.rsplit("/", 1)[-1])
        s.attrs.update(meta)
        return s

    if ds.ndim == 2:
        idx = _axis_index(f, ds, 0, ds.shape[0])
        cols = _axis_index(f, ds, 1, ds.shape[1])
        df = pd.DataFrame(ds[...], index=idx, columns=cols)
        df.attrs.update(meta)
        return df

    return ds[...]  # rank > 2: raw array, cannot be labeled as a table


# ---------------------------------------------------------------------------
# public API
# ---------------------------------------------------------------------------
def arr_tree(store_path: str | Path) -> dict:
    """Describe the structure of an X3df store as a nested tree.

    Metadata only — reads no array data, so it is cheap regardless of dataset
    size. Each node is a dict ``{name, path, kind, shape, dtype, scales, unit,
    children}``; groups have ``shape=dtype=None``. ``path`` is the value to pass
    to :func:`read_store`.

    Parameters
    ----------
    store_path : str | Path
        Path to the ``arr.dat`` HDF5 store.

    Returns
    -------
    dict
        Root node whose ``children`` hold the full tree.
    """
    root = {"name": "", "path": "", "kind": "group", "shape": None,
            "dtype": None, "scales": None, "unit": None, "children": []}
    index = {"": root}

    with h5py.File(Path(store_path), "r") as f:
        def ensure_group(path):
            node = index.get(path)
            if node is not None:
                return node
            parent_path, _, name = path.rpartition("/")
            parent = ensure_group(parent_path) if path else root
            node = {"name": name, "path": path, "kind": "group", "shape": None,
                    "dtype": None, "scales": None, "unit": None, "children": []}
            index[path] = node
            parent["children"].append(node)
            return node

        def visit(name, obj):
            if isinstance(obj, h5py.Group):
                ensure_group(name)
                return
            parent_path = name.rpartition("/")[0]
            parent = ensure_group(parent_path) if parent_path else root
            scales = obj.attrs.get("scales")
            scales = [_decode(s) for s in scales] if scales is not None else None
            unit = str(_decode(obj.attrs["unit"])) if "unit" in obj.attrs else None
            parent["children"].append({
                "name": name.rpartition("/")[2], "path": name, "kind": "dataset",
                "shape": list(obj.shape), "dtype": str(obj.dtype),
                "scales": scales, "unit": unit, "children": [],
            })

        f.visititems(visit)

    return root


def read_store(store_path: str | Path, paths: str | list[str]) -> Any:
    """Extract one or more datasets from an X3df store as labeled pandas objects.

    Opens the store once and reads every requested path. Coordinates are
    resolved from each dataset's own attrs (time axes from ``dim{N}_offset``,
    spatial axes by dereferencing ``dim{N}_element_names``); ``unit``/``scales``
    are attached to the result's ``.attrs``.

    Parameters
    ----------
    store_path : str | Path
        Path to the ``arr.dat`` HDF5 store.
    paths : str | list[str]
        A dataset path, or a list of them (as reported by :func:`arr_tree`).

    Returns
    -------
    object | dict
        If ``paths`` is a list: ``{path: result}``. If ``paths`` is a single
        string: the result directly. Each result is a python scalar (0-D),
        ``pandas.Series`` (1-D), ``pandas.DataFrame`` (2-D), or a raw
        ``numpy.ndarray`` (rank > 2).
    """
    single = isinstance(paths, str)
    path_list = [paths] if single else list(paths)

    with h5py.File(Path(store_path), "r") as f:
        out = {p: _read_one(f, p) for p in path_list}

    return out[paths] if single else out
