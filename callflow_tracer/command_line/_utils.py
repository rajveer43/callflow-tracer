"""Shared utilities for all CLI subcommand modules."""

import json
import os
import sys
import webbrowser
from pathlib import Path

from ..core.tracer import CallGraph


def execute_script(script_path: str, script_args: list[str]) -> None:
    """Execute a Python script with given arguments inside the current process."""
    original_argv = sys.argv
    sys.argv = [script_path] + script_args
    try:
        script_globals = {"__name__": "__main__", "__file__": script_path}
        with open(script_path, "r") as f:
            code = compile(f.read(), script_path, "exec")
            exec(code, script_globals)  # noqa: S102
    finally:
        sys.argv = original_argv


def open_browser(filepath: str) -> None:
    """Open a file in the default web browser."""
    abs_path = os.path.abspath(filepath)
    webbrowser.open(f"file://{abs_path}")


def load_graph_from_json(filepath: str) -> CallGraph:
    """Load a CallGraph from a JSON trace file."""
    with open(filepath, "r") as f:
        trace_data = json.load(f)
    return CallGraph.from_dict(trace_data)
