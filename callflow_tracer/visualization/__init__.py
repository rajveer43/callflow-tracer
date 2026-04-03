"""Visualization and notebook-facing helpers."""

from .comparison import compare_graphs, export_comparison_html
from .exporter import export_graph, export_html, export_html_3d, export_json
from .flamegraph import generate_flamegraph
from .flamegraph_enhanced import generate_enhanced_html_template

try:
    from .jupyter import (
        callflow_cell_trace,
        callflow_trace,
        display_callgraph,
        init_jupyter,
    )
except Exception:  # pragma: no cover - optional Jupyter dependency

    def init_jupyter():
        """Fallback when IPython is not installed."""
        print("Jupyter integration is unavailable. Install IPython to enable it.")

    def display_callgraph(*args, **kwargs):
        raise RuntimeError("Jupyter integration is unavailable. Install IPython.")

    def callflow_trace(*args, **kwargs):
        raise RuntimeError("Jupyter integration is unavailable. Install IPython.")

    def callflow_cell_trace(*args, **kwargs):
        raise RuntimeError("Jupyter integration is unavailable. Install IPython.")


__all__ = [
    "export_json",
    "export_html",
    "export_html_3d",
    "export_graph",
    "generate_flamegraph",
    "generate_enhanced_html_template",
    "compare_graphs",
    "export_comparison_html",
    "init_jupyter",
    "display_callgraph",
    "callflow_trace",
    "callflow_cell_trace",
]
