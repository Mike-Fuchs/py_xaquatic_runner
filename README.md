# py_xaquatic_runner

Runner and IO utilities for [XAQUATIC](https://www.xaquatic.com) catchment models.

A general-purpose, reusable Python library for XAQUATIC model input/output,
validation, scheduling, and execution. It contains no project-specific
orchestration logic, so it can be used by any XAQUATIC-based workflow.

## Capabilities

- **xrun I/O** — read/write `.xrun` XML model configs, fully validated with
  Pydantic v2 (`xrun_reader` / `xrun_writer`). Supports XAQUATIC v1.3–v1.6
  with version detection.
- **xCropProtection (xCP) I/O** — read/write xCP XML to/from a flat,
  one-row-per-application DataFrame (`xcp_reader` / `xcp_writer`).
- **Flat-dict round-trip** — flatten an xrun object to dotted-key dict and back
  (`xrun_to_flat_dict` / `flat_dict_to_xrun`), enabling JSON storage of configs.
- **Scheduling & execution** — generate and run `.xrun`/`.bat` files, single-run
  or parameter sweeps (`schedule_runs` / `call_runs`).
- **Output reading** — read datasets from a run's HDF5 output store
  (`read_runs`), with low-level readers `arr_tree` (metadata-only walk) and
  `read_store` (named datasets) in `store.py`.

> Model execution is currently Windows-only (`.bat` files via `subprocess`).

## Installation

```bash
pip install git+https://github.com/Mike-Fuchs/py_xaquatic_runner.git
```

Or from a local checkout:

```bash
pip install .
```

Requires Python >= 3.10. Dependencies: `pydantic`, `pandas`, `pydantic-xml`,
`lxml`, `h5py`.

## Usage

```python
import py_xaquatic_runner as pxr

# Read / write model config
xrun_obj = pxr.xrun_reader("model.xrun")
pxr.xrun_writer(xrun_obj, "output.xrun")

# Round-trip an xrun config through a flat dict (JSON-storable)
flat = pxr.xrun_to_flat_dict(xrun_obj)
xrun_obj = pxr.flat_dict_to_xrun(flat)

# Schedule and execute runs, then read outputs
pxr.schedule_runs(...)
pxr.call_runs(...)
results = pxr.read_runs(...)
```

## License

See [LICENSE](LICENSE).
