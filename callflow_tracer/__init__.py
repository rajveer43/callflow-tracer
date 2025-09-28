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
 
__version__ = "0.2.2"
__author__ = "Rajveer Rathod"
__email__ = "rathodrajveer1311@gmail.com"

# Check if we're in a Jupyter environment
try:
    from IPython import get_ipython
    if get_ipython() is not None:
        from .jupyter import init_jupyter, display_callgraph, CallNode, CallEdge
        init_jupyter()
except (ImportError, AttributeError):
    pass

# Core tracing functions
from .tracer import (
    trace,
    trace_scope,
    get_current_graph,
    clear_trace,
    CallGraph,
    CallNode,
    CallEdge
)

# Visualization functions
from .exporter import (
    export_json,
    export_html,
    export_graph
)
from .flamegraph import generate_flamegraph

# Jupyter integration (automatically initialized if in Jupyter)
try:
    from .jupyter import display_callgraph
except ImportError:
    # IPython not available, define a dummy function
    def display_callgraph(*args, **kwargs):
        print("Jupyter integration not available. Install IPython to use display_callgraph.")

from .profiling import (
    profile_function,
    profile_section,
    get_memory_usage,
    PerformanceStats
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
    'get_current_graph',
    'clear_trace',
    'CallGraph',
    
    # Export functions
    'export_json',
    'export_html',
    'export_graph',
    
    # Visualization functions
    'display_callgraph',
    'generate_flamegraph',
    
    # Convenience functions
    'trace_and_export',
    
    # Profiling
    'profile_function',
    'profile_section',
    'get_memory_usage',
    
    # Package metadata
    '__version__',
    '__author__',
    '__email__'
]
