"""
Async/Await tracing support for callflow-tracer.

This module provides async-aware tracing capabilities including decorators
and context managers for tracing asynchronous function calls.
"""

import asyncio
import time
import sys
from contextlib import asynccontextmanager
from typing import Optional, Callable, Any
from functools import wraps

from .tracer import CallGraph, CallNode, CallEdge, _global_graph, _global_tracer


class AsyncCallNode(CallNode):
    """Extended CallNode with async-specific metadata."""
    
    def __init__(self, name: str, module: str = ""):
        super().__init__(name, module)
        self.is_async = True
        self.concurrent_calls = 0
        self.max_concurrent = 0
        self.await_time = 0.0  # Time spent waiting on awaits
    
    def to_dict(self):
        """Convert to dictionary with async metadata."""
        base_dict = super().to_dict()
        base_dict.update({
            'is_async': self.is_async,
            'concurrent_calls': self.concurrent_calls,
            'max_concurrent': self.max_concurrent,
            'await_time': round(self.await_time, 6),
            'active_time': round(self.total_time - self.await_time, 6)
        })
        return base_dict


class AsyncCallGraph(CallGraph):
    """Extended CallGraph with async tracking capabilities."""
    
    def __init__(self):
        super().__init__()
        self.async_nodes = {}  # Track async-specific nodes
        self.concurrent_tasks = {}  # Track concurrent execution
        self.task_timeline = []  # Timeline of task execution
    
    def add_async_node(self, name: str, module: str = "") -> AsyncCallNode:
        """Add or get an async node."""
        full_name = f"{module}.{name}" if module else name
        if full_name not in self.async_nodes:
            node = AsyncCallNode(name, module)
            self.async_nodes[full_name] = node
            self.nodes[full_name] = node  # Also add to regular nodes
        return self.async_nodes[full_name]
    
    def record_async_call(self, caller: str, callee: str, duration: float,
                         await_time: float = 0.0, args: tuple = (), kwargs: dict = None):
        """Record an async function call with await time."""
        # Use parent's record_call
        self.record_call(caller, callee, duration, args, kwargs)
        
        # Update async-specific data
        callee_parts = callee.split('.')
        callee_name = callee_parts[-1]
        callee_module = '.'.join(callee_parts[:-1]) if len(callee_parts) > 1 else ''
        
        node = self.add_async_node(callee_name, callee_module)
        node.await_time += await_time
    
    def track_concurrent_start(self, task_name: str):
        """Track when a concurrent task starts."""
        if task_name not in self.concurrent_tasks:
            self.concurrent_tasks[task_name] = {'count': 0, 'max': 0}
        
        self.concurrent_tasks[task_name]['count'] += 1
        if self.concurrent_tasks[task_name]['count'] > self.concurrent_tasks[task_name]['max']:
            self.concurrent_tasks[task_name]['max'] = self.concurrent_tasks[task_name]['count']
        
        self.task_timeline.append({
            'time': time.time() - (self.start_time or time.time()),
            'task': task_name,
            'event': 'start'
        })
    
    def track_concurrent_end(self, task_name: str):
        """Track when a concurrent task ends."""
        if task_name in self.concurrent_tasks:
            self.concurrent_tasks[task_name]['count'] -= 1
        
        self.task_timeline.append({
            'time': time.time() - (self.start_time or time.time()),
            'task': task_name,
            'event': 'end'
        })
    
    def to_dict(self):
        """Convert graph to dict with async metadata."""
        base_dict = super().to_dict()
        base_dict['metadata']['async_info'] = {
            'total_async_functions': len(self.async_nodes),
            'concurrent_tasks': self.concurrent_tasks,
            'task_timeline': self.task_timeline[:100]  # Limit timeline size
        }
        return base_dict


def trace_async(func: Callable) -> Callable:
    """
    Decorator to trace async functions.
    
    Usage:
        @trace_async
        async def my_async_function():
            await asyncio.sleep(1)
            return "result"
    """
    if not asyncio.iscoroutinefunction(func):
        raise TypeError(f"{func.__name__} is not an async function. Use @trace for sync functions.")
    
    @wraps(func)
    async def wrapper(*args, **kwargs):
        global _global_graph
        
        # Get or create graph
        if _global_graph is None:
            from .tracer import CallGraph
            _global_graph = AsyncCallGraph()
        
        # Upgrade to AsyncCallGraph if needed
        if not isinstance(_global_graph, AsyncCallGraph):
            # Can't upgrade existing graph, use it as-is
            graph = _global_graph
        else:
            graph = _global_graph
        
        # Get function names
        caller_name = _get_async_caller_name()
        callee_name = f"{func.__module__}.{func.__name__}" if func.__module__ != '__main__' else func.__name__
        
        # Track concurrent execution
        if isinstance(graph, AsyncCallGraph):
            graph.track_concurrent_start(callee_name)
        
        start_time = time.time()
        await_start = None
        total_await_time = 0.0
        
        try:
            # Execute the async function
            result = await func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            
            # Record the call
            if isinstance(graph, AsyncCallGraph):
                graph.record_async_call(caller_name, callee_name, duration, 
                                       total_await_time, args, kwargs)
                graph.track_concurrent_end(callee_name)
            else:
                graph.record_call(caller_name, callee_name, duration, args, kwargs)
    
    return wrapper


@asynccontextmanager
async def trace_scope_async(output_file: Optional[str] = None, include_args: bool = False):
    """
    Async context manager to trace all function calls within the scope.
    
    Args:
        output_file: Optional file path to save the trace results
        include_args: Whether to include function arguments in the trace
    
    Usage:
        async with trace_scope_async("my_trace.html"):
            await my_async_function()
    """
    global _global_graph, _global_tracer
    
    # Create new async graph
    graph = AsyncCallGraph()
    
    # Store previous state
    prev_graph = _global_graph
    prev_tracer = _global_tracer
    
    try:
        # Set up new graph
        _global_graph = graph
        graph.start_time = time.time()
        
        yield graph
        
    finally:
        # Restore previous state
        _global_graph = prev_graph
        _global_tracer = prev_tracer
        
        # Export results if output file specified
        if output_file:
            from .exporter import export_graph
            export_graph(graph, output_file)


def _get_async_caller_name() -> str:
    """Get the name of the calling async function."""
    try:
        frame = sys._getframe(3)  # Go up frames to find caller
        func_name = frame.f_code.co_name
        module_name = frame.f_globals.get('__name__', '')
        
        if module_name and module_name != '__main__':
            return f"{module_name}.{func_name}"
        return func_name
    except:
        return "<unknown>"


async def gather_traced(*awaitables, return_exceptions: bool = False):
    """
    Traced version of asyncio.gather that tracks concurrent execution.
    
    Usage:
        results = await gather_traced(
            async_func1(),
            async_func2(),
            async_func3()
        )
    """
    global _global_graph
    
    if isinstance(_global_graph, AsyncCallGraph):
        # Track that we're gathering multiple tasks
        _global_graph.task_timeline.append({
            'time': time.time() - (_global_graph.start_time or time.time()),
            'task': 'gather',
            'event': 'start',
            'count': len(awaitables)
        })
    
    start_time = time.time()
    
    try:
        results = await asyncio.gather(*awaitables, return_exceptions=return_exceptions)
        return results
    finally:
        duration = time.time() - start_time
        
        if isinstance(_global_graph, AsyncCallGraph):
            _global_graph.task_timeline.append({
                'time': time.time() - (_global_graph.start_time or time.time()),
                'task': 'gather',
                'event': 'end',
                'duration': duration,
                'count': len(awaitables)
            })


def get_async_stats(graph: AsyncCallGraph) -> dict:
    """
    Get async-specific statistics from the graph.
    
    Returns:
        Dictionary with async execution statistics
    """
    if not isinstance(graph, AsyncCallGraph):
        return {}
    
    total_async_time = sum(node.total_time for node in graph.async_nodes.values())
    total_await_time = sum(node.await_time for node in graph.async_nodes.values())
    total_active_time = total_async_time - total_await_time
    
    max_concurrent = max(
        (task['max'] for task in graph.concurrent_tasks.values()),
        default=0
    )
    
    return {
        'total_async_functions': len(graph.async_nodes),
        'total_async_time': round(total_async_time, 6),
        'total_await_time': round(total_await_time, 6),
        'total_active_time': round(total_active_time, 6),
        'efficiency': round((total_active_time / total_async_time * 100) if total_async_time > 0 else 0, 2),
        'max_concurrent_tasks': max_concurrent,
        'concurrent_tasks': graph.concurrent_tasks,
        'timeline_events': len(graph.task_timeline)
    }
