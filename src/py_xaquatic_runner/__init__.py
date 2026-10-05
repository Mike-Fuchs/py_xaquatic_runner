"""
py_xaquatic_runner
==================
Unified entrypoint for XAquatic model pipeline automation.

Usage:
    import py_xaquatic_runner as pxr
    
    xrun_obj = pxr.xrun_reader("model.xrun")
    pxr.xrun_writer(xrun_obj, "output.xrun")
"""

__version__ = "0.2.0"

from .io import xrun_reader, xrun_writer, xcp_reader, xcp_writer, xrun_to_flat_dict, flat_dict_to_xrun
from .dataclasses import XRunConfig, XRunClass_13, XRunClass_14, XRunClass_15
from .core import flatten_model, schedule_runs, call_runs, read_runs
from .store import arr_tree, read_store

__all__ = [
    "xrun_reader", "xrun_writer", "xcp_reader", "xcp_writer",
    "XRunConfig", "XRunClass_13", "XRunClass_14", "XRunClass_15",
    "flatten_model", "schedule_runs", "call_runs", "read_runs"
]

# Phase 1 functions (to be implemented):
# from .io import xrun_to_flat_dict, flat_dict_to_xrun

__all__ = [
    # IO
    "xrun_reader",
    "xrun_writer",
    "xcp_reader",
    # "xcp_writer",        # Phase 1
    "xrun_to_flat_dict",
    "flat_dict_to_xrun",
    
    # Data structures
    "XRunConfig",
    "XRunClass_13",
    "XRunClass_14",
    "XRunClass_15",
    
    # Core logic
    "flatten_model",
    "schedule_runs",
    "call_runs",
    "read_runs",

    # X3df output store (arr.dat)
    "arr_tree",
    "read_store",
]