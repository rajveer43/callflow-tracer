"""
Core tracing functionality for callflow-tracer.

This module provides the main tracing capabilities including the @trace decorator
and trace_scope context manager for capturing function call relationships.
"""

import random
import sys
import time
import threading
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

# Thread-local storage so that concurrent threads each have an independent
# active graph/tracer without clobbering each other.
_thread_local = threading.local()


@dataclass(frozen=True)
class TraceOptions:
    """Configuration for trace collection."""

    include_args: bool = False
    sampling_rate: float = 1.0
    include_modules: Optional[Tuple[str, ...]] = None
    exclude_modules: Optional[Tuple[str, ...]] = None
    min_duration_ms: float = 0.0


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
            self.arguments.append(
                {
                    "args": str(args)[:100] if args else None,  # Truncate for privacy
                    "kwargs": str(kwargs)[:100] if kwargs else None,
                }
            )

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "module": self.module,
            "full_name": self.full_name,
            "call_count": self.call_count,
            "total_time": round(self.total_time, 6),
            "avg_time": round(self.total_time / max(self.call_count, 1), 6),
            "arguments": self.arguments[-5:],  # Keep only last 5 calls for privacy
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
            "caller": self.caller,
            "callee": self.callee,
            "call_count": self.call_count,
            "total_time": round(self.total_time, 6),
            "avg_time": round(self.total_time / max(self.call_count, 1), 6),
        }


class CallGraph:
    """Main call graph data structure."""

    def __init__(self, trace_options: Optional[TraceOptions] = None):
        self.nodes: Dict[str, CallNode] = {}
        self.edges: Dict[tuple, CallEdge] = {}
        self.start_time = None
        self._lock = threading.Lock()
        self.trace_options = trace_options or TraceOptions()
        self.trace_stats = {
            "total_calls": 0,
            "recorded_calls": 0,
            "skipped_sampling": 0,
            "skipped_filtering": 0,
            "skipped_duration": 0,
        }

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

    def record_call(
        self,
        caller: str,
        callee: str,
        duration: float,
        args: tuple = (),
        kwargs: dict = None,
        skip_reason: Optional[str] = None,
    ):
        """Record a function call in the graph.

        skip_reason: if set, only the counter is updated (call is filtered).
        """
        with self._lock:
            self.trace_stats["total_calls"] += 1

            if skip_reason is not None:
                self.trace_stats[skip_reason] += 1
                return

            self.trace_stats["recorded_calls"] += 1

            # Add nodes
            caller_node = self.add_node(
                caller.split(".")[-1], ".".join(caller.split(".")[:-1])
            )
            callee_node = self.add_node(
                callee.split(".")[-1], ".".join(callee.split(".")[:-1])
            )

            # Add edge
            edge = self.add_edge(caller, callee)

            # Update statistics
            callee_node.add_call(duration, args, kwargs)
            edge.add_call(duration)

    def should_record_call(
        self, caller: str, callee: str, duration: float
    ) -> Optional[str]:
        """Return a skip reason if the call should not be recorded."""
        options = self.trace_options

        caller_module = caller.rsplit(".", 1)[0] if "." in caller else caller
        callee_module = callee.rsplit(".", 1)[0] if "." in callee else callee

        if options.include_modules:
            if not any(
                _module_matches(module, options.include_modules)
                for module in (caller_module, callee_module)
            ):
                return "skipped_filtering"

        if options.exclude_modules and any(
            _module_matches(module, options.exclude_modules)
            for module in (caller_module, callee_module)
        ):
            return "skipped_filtering"

        if options.min_duration_ms > 0 and duration * 1000 < options.min_duration_ms:
            return "skipped_duration"

        if options.sampling_rate < 1.0 and random.random() > options.sampling_rate:
            return "skipped_sampling"

        return None

    def to_dict(self):
        """Convert the entire graph to a dictionary for JSON serialization."""
        node_times = sum(n.total_time for n in self.nodes.values())
        return {
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "edges": [edge.to_dict() for edge in self.edges.values()],
            "metadata": {
                "total_nodes": len(self.nodes),
                "total_edges": len(self.edges),
                "trace_options": _trace_options_to_dict(self.trace_options),
                "trace_stats": self.trace_stats,
                # wall-clock duration of the trace session (may include I/O)
                "duration": round(time.time() - (self.start_time or time.time()), 6),
                # sum of all measured call times — use this for comparisons
                "total_call_time": round(node_times, 6),
            },
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CallGraph":
        """Reconstruct a CallGraph from a previously serialized dictionary.

        This enables programmatic post-hoc analysis without re-running the
        traced program, and powers the funnel ``--data`` option and CLI
        ``compare`` / ``explain`` commands.
        """
        meta = data.get("metadata", {})
        raw_options = meta.get("trace_options", {})

        # TraceOptions expects tuples for include/exclude_modules
        include_modules = raw_options.get("include_modules")
        exclude_modules = raw_options.get("exclude_modules")
        options = TraceOptions(
            include_args=raw_options.get("include_args", False),
            sampling_rate=raw_options.get("sampling_rate", 1.0),
            include_modules=tuple(include_modules) if include_modules else None,
            exclude_modules=tuple(exclude_modules) if exclude_modules else None,
            min_duration_ms=raw_options.get("min_duration_ms", 0.0),
        )

        graph = cls(options)
        graph.trace_stats = dict(meta.get("trace_stats", graph.trace_stats))

        for n in data.get("nodes", []):
            node = graph.add_node(n.get("name", ""), n.get("module", ""))
            node.call_count = int(n.get("call_count", 0))
            node.total_time = float(n.get("total_time", 0.0))

        for e in data.get("edges", []):
            edge = graph.add_edge(e.get("caller", ""), e.get("callee", ""))
            edge.call_count = int(e.get("call_count", 0))
            edge.total_time = float(e.get("total_time", 0.0))

        return graph


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

        try:
            if event == "call":
                # Get caller and callee information
                caller_frame = frame.f_back
                if caller_frame:
                    caller_name = self._get_function_name(caller_frame)
                    callee_name = self._get_function_name(frame)

                    # Skip internal callflow-tracer functions
                    if (
                        "callflow_tracer" in callee_name
                        or "callflow_tracer" in caller_name
                    ):
                        return self._trace_calls

                    self.call_times[frame] = (
                        time.time(),
                        caller_name,
                        callee_name,
                    )

            elif event == "return":
                # Calculate call duration
                if frame in self.call_times:
                    start_time, caller_name, callee_name = self.call_times[frame]
                    del self.call_times[frame]
                    duration = time.time() - start_time

                    _record_traced_call(
                        self.graph,
                        caller_name,
                        callee_name,
                        duration,
                        (),
                        {},
                    )

        except Exception as e:
            # Don't let tracing errors break the program
            pass

        return self._trace_calls

    def _get_function_name(self, frame) -> str:
        """Extract function name from frame."""
        if not frame:
            return "<unknown>"

        func_name = frame.f_code.co_name
        module_name = frame.f_globals.get("__name__", "")

        if module_name and module_name != "__main__":
            return f"{module_name}.{func_name}"
        return func_name


# Module-level globals — kept for backward-compatibility and for async_tracer
# which must access them by module reference.  Prefer get_current_graph() in
# new code.  Per-thread state is stored in _thread_local; the module-level
# variables serve as a fallback for the main thread and for async code that
# hasn't migrated to contextvars yet.
_global_tracer = None
_global_graph = None


def _get_thread_graph() -> Optional["CallGraph"]:
    """Return the graph active on the current thread (or the module global)."""
    local_graph = getattr(_thread_local, "graph", None)
    if local_graph is not None:
        return local_graph
    return _global_graph


def _get_thread_tracer() -> Optional["CallTracer"]:
    """Return the tracer active on the current thread (or the module global)."""
    local_tracer = getattr(_thread_local, "tracer", None)
    if local_tracer is not None:
        return local_tracer
    return _global_tracer


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
        active_graph = _get_thread_graph()

        callee_name = (
            f"{func.__module__}.{func.__name__}"
            if func.__module__ != "__main__"
            else func.__name__
        )

        if active_graph is not None:
            # Inside a trace_scope — just time and record the call
            start_time = time.time()
            try:
                return func(*args, **kwargs)
            finally:
                duration = time.time() - start_time
                caller_name = _get_caller_name()
                _record_traced_call(
                    active_graph, caller_name, callee_name, duration, args, kwargs
                )
        else:
            # Outside any trace_scope — create a temporary, self-contained
            # scope so we don't leave sys.settrace running forever.
            tmp_graph = CallGraph()
            tmp_tracer = CallTracer(tmp_graph)
            _thread_local.graph = tmp_graph
            _thread_local.tracer = tmp_tracer
            tmp_tracer.start()
            start_time = time.time()
            try:
                return func(*args, **kwargs)
            finally:
                duration = time.time() - start_time
                tmp_tracer.stop()          # always stop — no more leak
                _thread_local.graph = None
                _thread_local.tracer = None
                caller_name = _get_caller_name()
                _record_traced_call(
                    tmp_graph, caller_name, callee_name, duration, args, kwargs
                )

    return wrapper


@contextmanager
def trace_scope(
    output_file: Optional[str] = None,
    include_args: bool = False,
    sampling_rate: float = 1.0,
    include_modules: Optional[List[str]] = None,
    exclude_modules: Optional[List[str]] = None,
    min_duration_ms: float = 0.0,
):
    """
    Context manager to trace all function calls within the scope.

    Args:
        output_file: Optional file path to save the trace results.
        include_args: Whether to include function arguments in the trace.
        sampling_rate: Fraction of calls to keep in the graph (0.0-1.0).
        include_modules: Optional module prefixes to keep.
        exclude_modules: Optional module prefixes to skip.
        min_duration_ms: Skip calls that execute faster than this threshold.

    Usage:
        with trace_scope("my_trace.html"):
            main()
    """
    global _global_tracer, _global_graph

    # Create new graph and tracer for this scope
    options = TraceOptions(
        include_args=include_args,
        sampling_rate=sampling_rate,
        include_modules=tuple(include_modules) if include_modules else None,
        exclude_modules=tuple(exclude_modules) if exclude_modules else None,
        min_duration_ms=min_duration_ms,
    )
    graph = CallGraph(options)
    tracer = CallTracer(graph)

    # Store previous state — prefer thread-local, fall back to module globals
    prev_graph = getattr(_thread_local, "graph", None) or _global_graph
    prev_tracer = getattr(_thread_local, "tracer", None) or _global_tracer

    try:
        # Set active scope on both thread-local AND module globals so that
        # async_tracer (which reads module globals) also sees the new graph.
        _thread_local.graph = graph
        _thread_local.tracer = tracer
        _global_graph = graph
        _global_tracer = tracer
        tracer.start()

        yield graph

    finally:
        # Stop tracing and restore previous state
        tracer.stop()
        _thread_local.graph = prev_graph
        _thread_local.tracer = prev_tracer
        _global_graph = prev_graph
        _global_tracer = prev_tracer

        # Export results if output file specified
        if output_file:
            from ..visualization.exporter import export_graph

            export_graph(graph, output_file)


def _get_caller_name() -> str:
    """Get the name of the calling function.

    Walks up the call stack dynamically, skipping all frames that belong to
    callflow_tracer itself, so the result is always the real user caller
    regardless of decorator nesting depth.
    """
    try:
        frame = sys._getframe(1)
        while frame is not None:
            module_name = frame.f_globals.get("__name__", "")
            if "callflow_tracer" not in module_name:
                func_name = frame.f_code.co_name
                if module_name and module_name != "__main__":
                    return f"{module_name}.{func_name}"
                return func_name
            frame = frame.f_back
    except Exception:
        pass
    return "<unknown>"


def get_current_graph() -> Optional[CallGraph]:
    """Get the current active call graph for this thread."""
    return _get_thread_graph()


def clear_trace():
    """Clear the current trace data for this thread."""
    global _global_tracer, _global_graph
    tracer = _get_thread_tracer()
    if tracer:
        tracer.stop()
    _thread_local.graph = None
    _thread_local.tracer = None
    _global_tracer = None
    _global_graph = None


def _module_matches(module_name: str, patterns: Sequence[str]) -> bool:
    """Return True when a module matches any prefix pattern."""
    if not module_name:
        return False

    for pattern in patterns:
        if not pattern:
            continue
        if module_name == pattern or module_name.startswith(f"{pattern}."):
            return True
    return False


def _trace_options_to_dict(options: TraceOptions) -> Dict[str, Any]:
    """Convert trace options to a JSON-friendly dict."""
    data = asdict(options)
    if data.get("include_modules") is not None:
        data["include_modules"] = list(data["include_modules"])
    if data.get("exclude_modules") is not None:
        data["exclude_modules"] = list(data["exclude_modules"])
    return data


def _record_traced_call(
    graph: CallGraph,
    caller_name: str,
    callee_name: str,
    duration: float,
    args: tuple,
    kwargs: dict,
) -> bool:
    """Apply trace options and record the call if it should be kept.

    All stat updates are delegated into graph.record_call which holds the
    lock, so there are no out-of-lock counter mutations.
    """
    skip_reason = graph.should_record_call(caller_name, callee_name, duration)
    # record_call handles total_calls + optional skip counter atomically
    graph.record_call(caller_name, callee_name, duration, args, kwargs, skip_reason=skip_reason)
    return skip_reason is None
