"""
core.py
========
XAquatic automation pipeline core module.

Implements:
- flatten_model() : Flatten nested Pydantic models for export.
- schedule_runs() : Generate .xrun/.bat files and metadata.
- call_runs()     : Execute generated batch files using metadata.
- read_runs()     : Read and merge output data per run.
- create_metadata(): Register existing .xrun/.bat files into metadata.
"""

from __future__ import annotations

import subprocess
import time
import json
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from itertools import product
from pathlib import Path
from typing import Any

import pandas as pd

from .dataclasses import XRunConfig
from .io import xrun_reader, xrun_writer
from .store import arr_tree, read_store

# ==== ensure that the jobs folder structure is available ====
def ensure_job_folders(project_dir: Path) -> dict[str, Path]:
    """
    Ensure the XAquatic jobs folder structure exists under a given project directory.

    Returns
    -------
    dict[str, Path]
        Dictionary with absolute paths to created (or existing) folders:
        {
            "jobs": <Path>,
            "meta": <Path>,
            "logs": <Path>,
            "status": <Path>,
        }
    """
    jobs_dir = project_dir / "jobs"
    meta_dir = jobs_dir / "meta"
    logs_dir = jobs_dir / "logs"
    status_dir = jobs_dir / "status"

    for d in (jobs_dir, meta_dir, logs_dir, status_dir):
        d.mkdir(parents=True, exist_ok=True)

    return {
        "jobs": jobs_dir,
        "meta": meta_dir,
        "logs": logs_dir,
        "status": status_dir,
    }

# ==== Flatten model into flat parameter dict ====
def flatten_model(model) -> dict[str, Any]:
    """
    Recursively flatten a nested Pydantic model or dictionary into
    {field_name: value}, ignoring section prefixes.

    Example:
        flatten_model(xrun_obj)
        -> {'SimID': 'Test1', 'PatchApplication': True, 'WindDirection': 270.0, ...}
    """
    flat = {}

    # Get data representation
    if hasattr(model, "model_dump"):
        data = model.model_dump()
    elif isinstance(model, dict):
        data = model
    else:
        return {}

    # Recursive flattening
    for key, val in data.items():
        if hasattr(val, "model_dump") or isinstance(val, dict):
            flat.update(flatten_model(val))
        else:
            flat[key] = val

    return flat

# ==== Helper: write batch file ====
def write_bat_file(bat_path: Path, config: XRunConfig, xrun_filename: str) -> None:
    """Write a .bat launcher file for a given .xrun."""
    with open(bat_path, "w", encoding="utf-8") as f:
        f.write(
            f"""@echo off
setlocal
cd "%~dp0.."
set "python_exe=%CD%/{config.python_exe}"
set "xland_script=%CD%/{config.xland_script}"
set "xland_input=%CD%/{xrun_filename}"
call "%python_exe%" "%xland_script%" "%xland_input%"
endlocal
"""
        )

# ==== Helper: formats time ====
def format_time(sec: float) -> str:
    """Format seconds as mm:ss."""
    m, s = divmod(int(sec), 60)
    return f"{m:02}:{s:02}"

# ==== Helper: executes a single simulation run ====
def execute_run_single(row, jobs_dir, logs_dir, project_dir) -> dict[str, Any]:
    """
    Run a single .bat file once and return its exit status.

    Parameters
    ----------
    row : pandas.Series
        Metadata row containing run_id, bat_file, etc.
    jobs_dir, logs_dir, project_dir : Path
        Base directories for job, log, and project.

    Returns
    -------
    dict[str, Any]
        Status information for the single run, including runtime and log path.
    """
    run_id = row["run_id"]
    bat_file = row["bat_file"]
    bat_path = jobs_dir / bat_file
    log_path = logs_dir / f"{Path(bat_file).stem}.log"

    start_time = datetime.now()
    try:
        with open(log_path, "w", encoding="utf-8") as log:
            subprocess.run(
                [str(bat_path)],
                cwd=project_dir,
                shell=True,
                check=True,
                stdout=log,
                stderr=subprocess.STDOUT,
            )
        status = "success"
    except subprocess.CalledProcessError:
        status = "failed"
    except Exception as e:
        status = f"error: {e}"

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    return {
        "run_id": run_id,
        "bat_file": bat_file,
        "status": status,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "duration_s": round(duration, 2),
        "log_file": str(log_path.relative_to(project_dir)),
    }


def execute_run_with_retries(
    row,
    jobs_dir: Path,
    logs_dir: Path,
    project_dir: Path,
    n_tries: int,
    wait_time: int,
) -> dict[str, Any]:
    """
    Run a single .bat with retry logic and output validation, returning its final
    status dict. Kept top-level so it can be dispatched to a pool worker; the
    sequential path calls it directly.

    A run is only considered validated when the process exits successfully *and* its
    ``arr.dat`` store contains every requested dataset.
    """
    # Randomized pre-launch delay so parallel workers don't all start at once.
    time.sleep(random.uniform(0, wait_time / 10))

    requested = json.loads(row.get("output", "[]"))
    run_dir = Path(row["output_dir"])

    res: dict[str, Any] = {}
    for attempt in range(1, n_tries + 1):
        res = execute_run_single(row, jobs_dir, logs_dir, project_dir)

        # Validate the run produced the requested datasets in its arr.dat store
        stores = list(run_dir.glob("mcs/*/store/arr.dat"))
        if stores:
            avail, stack = set(), [arr_tree(stores[0])]
            while stack:
                node = stack.pop()
                if node["kind"] == "dataset":
                    avail.add(node["path"])
                stack.extend(node["children"])
            all_exist = all(p in avail for p in requested)
        else:
            all_exist = False

        if res["status"] == "success" and all_exist:
            res["attempts"] = attempt
            res["validated"] = True
            break

        if attempt < n_tries:
            print(f"Retrying {row['run_id']} (attempt {attempt}/{n_tries}) after {wait_time}s...")
            time.sleep(wait_time)
            continue
        else:
            res["attempts"] = n_tries
            res["validated"] = False
            res["status"] = "failed (no output)"

    return res


# ==== Schedule and prepare model runs ====
def schedule_runs(
    base_xrun,
    config: XRunConfig,
    param_grid: dict[str, list[Any]] | None = None,
    base_id: str = "run",
    output: list[str] | None = None,
) -> Path:
    """
    Create .xrun and .bat files for single or multiple parameter combinations.
    Always writes a metadata file:
        - jobs/meta/pxr_metafile_<SimID>.csv             (for single run)
        - jobs/meta/pxr_metafile_<SimID>_<base_id>.csv   (for sweeps)

    Parameters
    ----------
    base_xrun : XRunClass
        Base .xrun configuration object.
    config : XRunConfig
        Model run configuration.
    param_grid : dict[str, list[Any]] | None
        Optional parameter sweep definitions.
    base_id : str
        Base string for run identifiers.
    output : list[str] | None
        Dataset paths to extract from each run's arr.dat store, in HDF5 path
        form (e.g. ["StepsRiverNetwork/PEC_SW", "CvasiLemLandscape/r.EP50"]).
        Recorded in the metadata; validated by call_runs and read by read_runs.
    """
    project_dir = Path(config.project_folder)
    if not project_dir.exists():
        raise FileNotFoundError(
            f"The project folder '{project_dir}' does not exist. "
            "Please verify that XAquatic has been initialized correctly and that "
            "the path in XRunConfig.project_folder is valid."
        )

    dirs = ensure_job_folders(project_dir)
    jobs_dir = dirs["jobs"]
    meta_dir = dirs["meta"]

    base_simid = getattr(base_xrun.SimulationInfo, "SimID", "simulation")
    flattened_rows = []

    # === SINGLE RUN MODE ===
    if not param_grid:
        xrun_filename = f"{base_simid}.xrun"
        bat_filename = f"{base_simid}.bat"
        xrun_path = project_dir / xrun_filename
        bat_path = jobs_dir / bat_filename
        output_dir = project_dir / "run" / base_simid

        xrun_writer(base_xrun, xrun_path)
        write_bat_file(bat_path, config, xrun_filename)

        flat_params = flatten_model(base_xrun)

        row = {
            "run_id": "",
            "xrun_file": str(xrun_filename),
            "bat_file": str(bat_filename),
            "output_dir": str(output_dir),
            "mode": "single",
            "output": json.dumps(output or []),
        }
        row.update(flat_params)
        flattened_rows.append(row)

        df_path = meta_dir / f"pxr_metafile_{base_simid}.csv"

    # === GRID (SWEEP) MODE ===
    else:
        keys = list(param_grid.keys())
        combos = list(product(*param_grid.values()))

        for idx, combo in enumerate(combos, start=1):
            run_id = f"{base_id}{idx}"
            updates = dict(zip(keys, combo))

            xrun_copy = base_xrun.model_copy(deep=True)
            for key, value in updates.items():
                parts = key.split(".")
                target = xrun_copy
                for p in parts[:-1]:
                    target = getattr(target, p)
                setattr(target, parts[-1], value)

            if hasattr(xrun_copy, "SimulationInfo"):
                xrun_copy.SimulationInfo.SimID = f"{base_simid}_{run_id}"

            xrun_filename = f"{base_simid}_{run_id}.xrun"
            bat_filename = f"{base_simid}_{run_id}.bat"
            xrun_path = project_dir / xrun_filename
            bat_path = jobs_dir / bat_filename
            output_dir = project_dir / "run" / f"{base_simid}_{run_id}"

            xrun_writer(xrun_copy, xrun_path)
            write_bat_file(bat_path, config, xrun_filename)

            flat_params = flatten_model(xrun_copy)

            row = {
                "run_id": run_id,
                "xrun_file": str(xrun_filename),
                "bat_file": str(bat_filename),
                "output_dir": str(output_dir),
                "mode": "grid",
                "output": json.dumps(output or []),
            }
            for k, v in updates.items():
                short_name = k.split(".")[-1]
                row[f"var_{short_name}"] = v
            row.update(flat_params)
            flattened_rows.append(row)

        df_path = meta_dir / f"pxr_metafile_{base_simid}_{base_id}.csv"

    # === Write metadata ===
    df = pd.DataFrame(flattened_rows)
    df["timestamp"] = datetime.now().isoformat()
    df["base_id"] = None if not param_grid else base_id
    df.to_csv(df_path, index=False)

    print(f"Scheduled {len(df)} run(s). Metadata saved to {df_path}")
    return df_path

# ==== Execute generated runs ====
def call_runs(
    metadata_path: str | Path,
    max_workers: int = 1,
    n_tries: int = 3,
    wait_time: int = 20,
) -> Path:
    """
    Execute .bat files listed in a metadata file, optionally in parallel.
    Implements retry logic, randomized pre-launch delay, and explicit output validation.

    Parameters
    ----------
    metadata_path : str | Path
        Path to metadata CSV generated by schedule_runs().
    max_workers : int
        Number of parallel workers.
    n_tries : int
        Maximum number of retries per run.
    wait_time : int
        Base wait time (s) for randomized pre-launch delay and between retries.

    Returns
    -------
    Path
        Path to status summary CSV file.
    """

    metadata_path = Path(metadata_path)
    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

    # === Resolve project folders (created earlier by schedule_runs) ===
    meta_dir = metadata_path.parent
    jobs_dir = meta_dir.parent
    logs_dir = jobs_dir / "logs"
    status_dir = jobs_dir / "status"
    project_dir = jobs_dir.parent

    # === Load metadata ===
    df = pd.read_csv(metadata_path)
    if df.empty:
        print("No runs found in metadata.")
        return

    simid = metadata_path.stem.replace("pxr_metafile_", "")
    total = len(df)
    print(f"Starting {total} run(s) for {simid} (max_workers={max_workers})...")

    start_all = time.time()
    results: list[dict[str, Any]] = []

    # === MAIN EXECUTION LOOP ===
    done = 0
    if max_workers > 1:
        # Threads are enough: each run's model executes in its own .bat subprocess,
        # and subprocess.run releases the GIL while waiting, so N threads drive N
        # concurrent model processes. The CPU-bound work is in those subprocesses,
        # not in this interpreter.
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_map = {
                executor.submit(
                    execute_run_with_retries,
                    row, jobs_dir, logs_dir, project_dir, n_tries, wait_time,
                ): row
                for _, row in df.iterrows()
            }

            for future in as_completed(future_map):
                res = future.result()
                results.append(res)
                done += 1

                elapsed = time.time() - start_all
                avg = elapsed / done
                eta = avg * (total - done)
                print(
                    f"{res['run_id']:<20} {res['status']:<18} | "
                    f"Elapsed {format_time(elapsed)} | "
                    f"Avg {format_time(avg)} | ETA {format_time(eta)} | "
                    f"{done}/{total} done"
                )
    else:
        # Sequential execution
        for _, row in df.iterrows():
            res = execute_run_with_retries(
                row, jobs_dir, logs_dir, project_dir, n_tries, wait_time
            )
            results.append(res)
            done += 1

            elapsed = time.time() - start_all
            avg = elapsed / done
            eta = avg * (total - done)
            print(
                f"{res['run_id']:<20} {res['status']:<18} | "
                f"Elapsed {format_time(elapsed)} | "
                f"Avg {format_time(avg)} | ETA {format_time(eta)} | "
                f"{done}/{total} done"
            )

    # === Write status summary ===
    status_df = pd.DataFrame(results)
    status_path = status_dir / f"pxr_statusfile_{simid}.csv"
    status_df.to_csv(status_path, index=False)

    success_count = sum(r["validated"] for r in results)
    print(f"\n{success_count}/{total} run(s) completed successfully.")
    print(f"Status file saved: {status_path}")

    # === Failed run summary ===
    failed_runs = [r for r in results if not r["validated"]]
    if failed_runs:
        print("\nThe following runs failed or produced incomplete output:")
        failed_ids = [r["run_id"] for r in failed_runs]
        failed_df = df[df["run_id"].isin(failed_ids)]
        var_cols = [c for c in failed_df.columns if c.startswith("var_")]

        merged = pd.merge(pd.DataFrame(failed_runs), failed_df, on="run_id", how="left")
        if var_cols:
            print(merged[["run_id", "status"] + var_cols].head().to_string(index=False))
        else:
            print(merged[["run_id", "status"]].head().to_string(index=False))

    return status_path


# ==== Collect and merge outputs ====
def read_runs(metadata_path: str | Path) -> dict[str, Any]:
    """
    Read the requested datasets from each run's arr.dat store, grouped by path.

    For every run in the metadata, the store is located at
    ``{output_dir}/mcs/*/store/arr.dat`` and the paths recorded in ``output``
    are read via :func:`read_store` (labeled pandas objects).

    Returns
    -------
    dict
        {
            "meta": <metadata DataFrame>,
            "results": {
                <dataset_path>: <object>,   # single run  -> the labeled object
                                            # multiple runs -> {run_id: object}
                ...
            }
        }
    """
    metadata_path = Path(metadata_path)
    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

    meta = pd.read_csv(metadata_path)
    per_path: dict[str, dict[str, Any]] = {}

    for _, row in meta.iterrows():
        rid = row.get("run_id", "")
        run_id = "" if pd.isna(rid) else str(rid).strip()
        run_dir = Path(row["output_dir"])

        if "output" not in row or pd.isna(row["output"]):
            print(f"No output paths defined for {run_id or 'single run'}")
            continue
        try:
            requested = json.loads(row["output"])
        except json.JSONDecodeError:
            requested = [row["output"]]
        if not requested:
            continue

        stores = sorted(run_dir.glob("mcs/*/store/arr.dat"))
        if not stores:
            print(f"No arr.dat store found for {run_id or 'single run'} under {run_dir}")
            continue

        objs = read_store(stores[0], requested)
        for path, obj in objs.items():
            per_path.setdefault(path, {})[run_id] = obj

    # single run -> bare object; multiple runs -> {run_id: object}
    results: dict[str, Any] = {}
    for path, runs in per_path.items():
        results[path] = runs[""] if (len(runs) == 1 and "" in runs) else runs

    if not results:
        print("No results were read - check output paths or stores.")

    return {"meta": meta, "results": results}



# ==== Create metadata for existing runs ====
def create_metadata(
    xrun_path: str | Path,
    bat_path: str | Path,
    output: list[str] | None = None,
    output_dir: str | Path | None = None,
) -> Path:
    """
    Create a pxr_metafile_<SimID>.csv for existing .xrun/.bat files.
    Includes all flattened model parameters.

    The "register existing artifacts" counterpart to schedule_runs: use it when a
    .xrun/.bat pair already exists on disk and you want to drive it through
    call_runs/read_runs. Mirrors the metadata schedule_runs writes.

    Parameters
    ----------
    xrun_path, bat_path : str | Path
        Existing .xrun and .bat files to register.
    output : list[str] | None
        Dataset paths to extract from the run's arr.dat store, in HDF5 path form
        (e.g. ["StepsRiverNetwork/PEC_SW", "CvasiLemLandscape/r.EP50"]).
        Recorded in the metadata; validated by call_runs and read by read_runs.
    output_dir : str | Path | None
        Run output base folder. Defaults to ``{project}/run/{SimID}`` - the path
        read_runs joins with ``mcs/*/store/arr.dat``.

    Raises
    ------
    ValueError
        If the .xrun file does not contain a valid SimulationInfo.SimID.
    """
    xrun_path = Path(xrun_path)
    bat_path = Path(bat_path)
    project_dir = xrun_path.parent

    # Read the .xrun and verify SimID
    xrun_obj = xrun_reader(xrun_path)

    if not hasattr(xrun_obj, "SimulationInfo") or not getattr(xrun_obj.SimulationInfo, "SimID", None):
        raise ValueError(
            f"The .xrun file '{xrun_path.name}' is missing a valid SimulationInfo.SimID. "
            "Please ensure the file defines a <SimulationInfo><SimID>...</SimID></SimulationInfo> section "
            "before registering it with create_metadata()."
        )

    simid = xrun_obj.SimulationInfo.SimID
    flat_params = flatten_model(xrun_obj)

    if output_dir is None:
        output_dir = project_dir / "run" / simid

    flat_params.update({
        "run_id": simid,
        "xrun_file": xrun_path.name,
        "bat_file": bat_path.name,
        "output_dir": str(output_dir),
        "mode": "manual",
        "output": json.dumps(output or []),
        "timestamp": datetime.now().isoformat(),
        "base_id": None,
    })

    meta_dir = ensure_job_folders(project_dir)["meta"]
    df = pd.DataFrame([flat_params])
    meta_path = meta_dir / f"pxr_metafile_{simid}.csv"
    df.to_csv(meta_path, index=False)

    print(f"Created metadata file: {meta_path}")
    return meta_path
