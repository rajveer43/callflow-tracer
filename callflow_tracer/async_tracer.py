"""
Async tracing utilities for callflow-tracer.

Provides:
- @atrace for async functions
- async_trace_scope for tracing within an async context
"""

import time
import inspect
from typing import Any, Callable, Optional, Awaitable
from functools import wraps
from contextlib import asynccontextmanager

from .tracer import CallGraph, CallTracer, get_current_graph


def _ensure_tracer() -> tuple[CallTracer, CallGraph]:
    """Ensure there is an active tracer/graph, creating one if needed."""
    graph = get_current_graph()
    if graph is None:
        graph = CallGraph()
        tracer = CallTracer(graph)
        tracer.start()
        return tracer, graph
    # When a graph exists, assume a tracer is already started via trace_scope
    # or decorator entry.
    # In case it's not, start a local tracer to avoid no-ops.
    tracer = CallTracer(graph)
    if not tracer.enabled:
        tracer.start()
    return tracer, graph


def _get_caller_name() -> str:
    """Best-effort caller name using inspect for async contexts."""
    try:
        stack = inspect.stack()
        # Skip current function and wrapper
        for frame_info in stack[2:]:
            module = inspect.getmodule(frame_info.frame)
            mod_name = module.__name__ if module and module.__name__ != "__main__" else ""
            func_name = frame_info.function
            if mod_name:
                return f"{mod_name}.{func_name}"
            return func_name
    except Exception:
        pass
    return "<unknown>"


def atrace(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
    """Decorator to trace async functions."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        tracer, graph = _ensure_tracer()
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            caller_name = _get_caller_name()
            callee_name = (
                f"{func.__module__}.{func.__name__}"
                if func.__module__ != "__main__"
                else func.__name__
            )
            graph.record_call(caller_name, callee_name, duration, args, kwargs)

    return wrapper


@asynccontextmanager
async def async_trace_scope(output_file: Optional[str] = None):
    """
    Async context manager to trace all calls within an async scope.

    Usage:
        async with async_trace_scope("trace.html"):
            await main()
    """
    graph = CallGraph()
    tracer = CallTracer(graph)

    try:
        tracer.start()
        yield graph
    finally:
        tracer.stop()
        if output_file:
            from .exporter import export_graph

            export_graph(graph, output_file)
