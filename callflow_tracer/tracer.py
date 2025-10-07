"""
Core tracing functionality for callflow-tracer.

This module provides the main tracing capabilities including the @trace decorator
and trace_scope context manager for capturing function call relationships.
"""

import sys
import time
import threading
from contextlib import contextmanager
from typing import Dict, Set, List, Optional, Any, Callable
from functools import wraps
import json


class CallNode:
    """Represents a function call node in the call graph."""
    
    def __init__(self, name: str, module: str = ""):
        self.name = name
        self.module = module
        self.full_name = f"{module}.{name}" if module else name
        self.call_count = 0
        self.total_time = 0.0
        self.arguments = []
    
    def add_call(self, duration: float, args: tuple = (), kwargs: dict = None):
        """Record a function call with timing and arguments."""
        self.call_count += 1
        self.total_time += duration
        if args or kwargs:
            self.arguments.append({
                'args': str(args)[:100] if args else None,  # Truncate for privacy
                'kwargs': str(kwargs)[:100] if kwargs else None
            })
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'name': self.name,
            'module': self.module,
            'full_name': self.full_name,
            'call_count': self.call_count,
            'total_time': round(self.total_time, 6),
            'avg_time': round(self.total_time / max(self.call_count, 1), 6),
            'arguments': self.arguments[-5:]  # Keep only last 5 calls for privacy
        }


class CallEdge:
    """Represents a call relationship between two functions."""
    
    def __init__(self, caller: str, callee: str):
        self.caller = caller
        self.callee = callee
        self.call_count = 0
        self.total_time = 0.0
    
    def add_call(self, duration: float):
        """Record a call through this edge."""
        self.call_count += 1
        self.total_time += duration
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'caller': self.caller,
            'callee': self.callee,
            'call_count': self.call_count,
            'total_time': round(self.total_time, 6),
            'avg_time': round(self.total_time / max(self.call_count, 1), 6)
        }


class CallGraph:
    """Main call graph data structure."""
    
    def __init__(self):
        self.nodes: Dict[str, CallNode] = {}
        self.edges: Dict[tuple, CallEdge] = {}
        self.call_stack = []
        self.start_time = None
        # Use RLock because tracing callbacks and DB instrumentation may record
        # nested calls within the same thread, requiring re-entrant locking.
        self._lock = threading.RLock()
    
    def add_node(self, name: str, module: str = "") -> CallNode:
        """Add or get a node for the given function."""
        full_name = f"{module}.{name}" if module else name
        if full_name not in self.nodes:
            self.nodes[full_name] = CallNode(name, module)
        return self.nodes[full_name]
    
    def add_edge(self, caller: str, callee: str) -> CallEdge:
        """Add or get an edge between two functions."""
        key = (caller, callee)
        if key not in self.edges:
            self.edges[key] = CallEdge(caller, callee)
        return self.edges[key]
    
    def record_call(self, caller: str, callee: str, duration: float, 
                   args: tuple = (), kwargs: dict = None):
        """Record a function call in the graph."""
        with self._lock:
            # Add nodes
            caller_node = self.add_node(caller.split('.')[-1], '.'.join(caller.split('.')[:-1]))
            callee_node = self.add_node(callee.split('.')[-1], '.'.join(callee.split('.')[:-1]))
            
            # Add edge
            edge = self.add_edge(caller, callee)
            
            # Update statistics
            callee_node.add_call(duration, args, kwargs)
            edge.add_call(duration)
    
    def to_dict(self):
        """Convert the entire graph to a dictionary for JSON serialization."""
        return {
            'nodes': [node.to_dict() for node in self.nodes.values()],
            'edges': [edge.to_dict() for edge in self.edges.values()],
            'metadata': {
                'total_nodes': len(self.nodes),
                'total_edges': len(self.edges),
                'duration': round(time.time() - (self.start_time or time.time()), 6)
            }
        }


class CallTracer:
    """Main tracer class that hooks into Python's execution."""
    
    def __init__(self, graph: CallGraph):
        self.graph = graph
        self.original_trace = None
        self.call_times = {}
        self.enabled = False
    
    def start(self):
        """Start tracing function calls."""
        if self.enabled:
            return
        
        self.enabled = True
        self.original_trace = sys.gettrace()
        sys.settrace(self._trace_calls)
        self.graph.start_time = time.time()
    
    def stop(self):
        """Stop tracing function calls."""
        if not self.enabled:
            return
        
        self.enabled = False
        sys.settrace(self.original_trace)
        self.original_trace = None
    
    def _trace_calls(self, frame, event, arg):
        """Internal trace function called by Python's profiler."""
        if not self.enabled:
            return
        
        if event == 'call':
            # Record call start time
            self.call_times[frame] = time.time()
            
            # Get caller and callee information
            caller_frame = frame.f_back
            if caller_frame:
                caller_name = self._get_function_name(caller_frame)
                callee_name = self._get_function_name(frame)
                
                # Record the call
                self.graph.record_call(caller_name, callee_name, 0.0)
        
        elif event == 'return':
            # Calculate call duration
            if frame in self.call_times:
                duration = time.time() - self.call_times[frame]
                del self.call_times[frame]
                
                # Update the last recorded call with actual duration
                caller_frame = frame.f_back
                if caller_frame:
                    caller_name = self._get_function_name(caller_frame)
                    callee_name = self._get_function_name(frame)
                    
                    # Find and update the edge
                    edge_key = (caller_name, callee_name)
                    if edge_key in self.graph.edges:
                        edge = self.graph.edges[edge_key]
                        # Update the last call's duration
                        edge.total_time += duration
                        edge.call_count = max(edge.call_count, 1)
        
        return self._trace_calls
    
    def _get_function_name(self, frame) -> str:
        """Extract function name from frame."""
        if not frame:
            return "<unknown>"
        
        func_name = frame.f_code.co_name
        module_name = frame.f_globals.get('__name__', '')
        
        if module_name and module_name != '__main__':
            return f"{module_name}.{func_name}"
        return func_name


# Global tracer instance
_global_tracer = None
_global_graph = None


def trace(func: Callable) -> Callable:
    """
    Decorator to trace a specific function.
    
    Usage:
        @trace
        def my_function():
            pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        global _global_tracer, _global_graph
        
        if _global_tracer is None:
            _global_graph = CallGraph()
            _global_tracer = CallTracer(_global_graph)
            _global_tracer.start()
        
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            # Record the call
            caller_name = _get_caller_name()
            callee_name = f"{func.__module__}.{func.__name__}" if func.__module__ != '__main__' else func.__name__
            _global_graph.record_call(caller_name, callee_name, duration, args, kwargs)
    
    return wrapper


@contextmanager
def trace_scope(output_file: Optional[str] = None, include_args: bool = False):
    """
    Context manager to trace all function calls within the scope.
    
    Args:
        output_file: Optional file path to save the trace results
        include_args: Whether to include function arguments in the trace
    
    Usage:
        with trace_scope("my_trace.html"):
            main()
    """
    global _global_tracer, _global_graph
    
    # Create new graph and tracer for this scope
    graph = CallGraph()
    tracer = CallTracer(graph)
    
    # Store previous state
    prev_tracer = _global_tracer
    prev_graph = _global_graph
    
    try:
        # Set up new tracer
        _global_tracer = tracer
        _global_graph = graph
        tracer.start()
        
        yield graph
        
    finally:
        # Stop tracing and restore previous state
        tracer.stop()
        _global_tracer = prev_tracer
        _global_graph = prev_graph
        
        # Export results if output file specified
        if output_file:
            from .exporter import export_graph
            export_graph(graph, output_file)


def _get_caller_name() -> str:
    """Get the name of the calling function."""
    frame = sys._getframe(2)  # Go up 2 frames (past wrapper and trace)
    return _global_tracer._get_function_name(frame) if _global_tracer else "<unknown>"


def get_current_graph() -> Optional[CallGraph]:
    """Get the current active call graph."""
    return _global_graph


def clear_trace():
    """Clear the current trace data."""
    global _global_tracer, _global_graph
    if _global_tracer:
        _global_tracer.stop()
    _global_tracer = None
    _global_graph = None
