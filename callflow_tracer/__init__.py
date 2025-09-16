"""
CallFlow Tracer - A lightweight Python library for tracing function call relationships.

This library provides simple decorators and context managers to trace function calls
and visualize them as interactive graphs.

Example usage:
    from callflow_tracer import trace, trace_scope
    
    @trace
    def my_function():
        return "Hello, World!"
    
    with trace_scope("output.html"):
        my_function()
"""

__version__ = "0.1.0"
__author__ = "CallFlow Tracer Team"
__email__ = "contact@callflow-tracer.dev"

# Main API exports
from .tracer import (
    trace,
    trace_scope,
    get_current_graph,
    clear_trace,
    CallGraph,
    CallNode,
    CallEdge
)

from .exporter import (
    export_json,
    export_html,
    export_graph
)

# Convenience function for one-liner usage
def trace_and_export(output_file: str, include_args: bool = False):
    """
    Convenience function that combines trace_scope with automatic export.
    
    Args:
        output_file: Path to save the trace results (JSON or HTML)
        include_args: Whether to include function arguments in the trace
    
    Example:
        from callflow_tracer import trace_and_export
        
        with trace_and_export("my_trace.html"):
            main()
    """
    return trace_scope(output_file, include_args)

# Make the main functions available at package level
__all__ = [
    # Core tracing functions
    'trace',
    'trace_scope', 
    'trace_and_export',
    
    # Graph management
    'get_current_graph',
    'clear_trace',
    
    # Export functions
    'export_json',
    'export_html', 
    'export_graph',
    
    # Data structures
    'CallGraph',
    'CallNode',
    'CallEdge',
    
    # Package metadata
    '__version__',
    '__author__',
    '__email__'
]
