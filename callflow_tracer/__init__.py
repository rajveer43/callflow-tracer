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
 
__version__ = "0.2.4"
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
    export_graph,
    export_html_3d
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

# Async tracing support
from .async_tracer import (
    trace_async,
    trace_scope_async,
    gather_traced,
    get_async_stats,
    AsyncCallGraph
)

# Comparison mode
from .comparison import (
    compare_graphs,
    export_comparison_html
)

# Memory leak detection
from .memory_leak_detector import (
    MemoryLeakDetector,
    detect_leaks,
    track_allocations,
    find_reference_cycles,
    get_memory_growth,
    get_top_memory_consumers,
    MemorySnapshot,
    ObjectTracker
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
    
    # Async tracing functions
    'trace_async',
    'trace_scope_async',
    'gather_traced',
    'get_async_stats',
    'AsyncCallGraph',
    
    # Export functions
    'export_json',
    'export_html',
    'export_html_3d',
    'export_graph',
    
    # Visualization functions
    'display_callgraph',
    'generate_flamegraph',
    
    # Comparison functions
    'compare_graphs',
    'export_comparison_html',
    
    # Memory leak detection
    'MemoryLeakDetector',
    'detect_leaks',
    'track_allocations',
    'find_reference_cycles',
    'get_memory_growth',
    'get_top_memory_consumers',
    'MemorySnapshot',
    'ObjectTracker',
    
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
