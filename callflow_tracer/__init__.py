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
 
__version__ = "0.2.3"
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
    export_html_3d,
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

# AI-powered features (optional, requires LLM provider)
try:
    from .ai import (
        summarize_trace,
        query_trace,
        TraceSummarizer,
        QueryEngine,
        LLMProvider,
        OpenAIProvider,
        AnthropicProvider,
        GeminiProvider,
        OllamaProvider,
        analyze_root_cause,
        RootCauseAnalyzer,
        detect_anomalies,
        AnomalyDetector
    )
    _ai_available = True
except ImportError as e:
    # AI features not available (missing dependencies)
    _ai_available = False
    def summarize_trace(*args, **kwargs):
        raise ImportError("AI features require LLM provider packages. Install with: pip install openai anthropic google-generativeai requests")
    def query_trace(*args, **kwargs):
        raise ImportError("AI features require LLM provider packages. Install with: pip install openai anthropic google-generativeai requests")
    def analyze_root_cause(*args, **kwargs):
        raise ImportError("AI features require LLM provider packages. Install with: pip install openai anthropic google-generativeai requests")
    def detect_anomalies(*args, **kwargs):
        raise ImportError("AI features require LLM provider packages. Install with: pip install openai anthropic google-generativeai requests")

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


# Async utilities
try:
    from .async_tracer import atrace, async_trace_scope  # type: ignore
except Exception:  # Optional in environments without async usage
    # Provide dummies to avoid import errors when not installed/used
    def atrace(func):
        return func
    def async_trace_scope(*args, **kwargs):  # type: ignore
        from contextlib import contextmanager
        @contextmanager
        def _noop():
            yield None
        return _noop()

# Make the main functions available at package level
__all__ = [
    # Core tracing functions
    'trace',
    'trace_scope',
    'atrace',
    'async_trace_scope',
    'get_current_graph',
    'clear_trace',
    'CallGraph',
    
    # Export functions
    'export_json',
    'export_html',
    'export_html_3d',
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
    
    # AI features (optional)
    'summarize_trace',
    'query_trace',
    'analyze_root_cause',
    'detect_anomalies',
    
    # Package metadata
    '__version__',
    '__author__',
    '__email__'
]

# Add AI classes to __all__ if available
if _ai_available:
    __all__.extend([
        'TraceSummarizer',
        'QueryEngine',
        'LLMProvider',
        'OpenAIProvider',
        'AnthropicProvider',
        'GeminiProvider',
        'OllamaProvider',
        'RootCauseAnalyzer',
        'AnomalyDetector'
    ])
