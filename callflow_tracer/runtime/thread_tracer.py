"""Multi-thread call graph tracer.

Wraps the core CallTracer so each thread gets its own call stack while
sharing a single merged CallGraph. Uses threading.local() for per-thread
call stacks and a shared lock-protected graph for aggregation.

Template Method Pattern: ThreadedCallTracer inherits CallTracer and overrides
the stack management methods to use thread-local storage.

DSA used:
  - Thread-local stack (list) for O(1) push/pop per thread
  - Lock-protected shared adjacency dict for O(1) edge merging
"""

from __future__ import annotations

import sys
import threading
import time
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

from callflow_tracer.core.tracer import CallGraph, CallNode, CallEdge, TraceOptions


class ThreadedCallGraph(CallGraph):
    """CallGraph with an explicit write lock for concurrent threads."""

    def __init__(self, trace_options: Optional[TraceOptions] = None) -> None:
        super().__init__(trace_options)
        self._write_lock = threading.Lock()

    def record_call(
        self,
        caller: str,
        callee: str,
        duration: float,
        args: list,
        kwargs: dict,
        skip_reason: Optional[str] = None,
    ) -> None:
        with self._write_lock:
            super().record_call(caller, callee, duration, args, kwargs, skip_reason)


class _ThreadState(threading.local):
    def __init__(self) -> None:
        super().__init__()
        self.call_stack: List[str] = []
        self.depth: int = 0


class ThreadedCallTracer:
    """Instruments multiple threads and merges into one ThreadedCallGraph.

    Usage::

        tracer = ThreadedCallTracer()
        tracer.start()
        # spin up threads — each one is automatically traced
        tracer.stop()
        graph = tracer.graph
    """

    _MAX_DEPTH = 200

    def __init__(self, trace_options: Optional[TraceOptions] = None) -> None:
        self._options = trace_options or TraceOptions()
        self._graph = ThreadedCallGraph(trace_options)
        self._state = _ThreadState()
        self._enabled = False
        self._original_profile = None

    @property
    def graph(self) -> ThreadedCallGraph:
        return self._graph

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        if self._enabled:
            return
        self._enabled = True
        self._original_profile = sys.getprofile()
        # threading.settrace sets the profile for all *new* threads
        threading.setprofile(self._profile_handler)
        sys.setprofile(self._profile_handler)

    def stop(self) -> None:
        if not self._enabled:
            return
        self._enabled = False
        sys.setprofile(self._original_profile)
        threading.setprofile(None)

    def __enter__(self) -> "ThreadedCallTracer":
        self.start()
        return self

    def __exit__(self, *_: object) -> None:
        self.stop()

    # ------------------------------------------------------------------
    # Profile handler
    # ------------------------------------------------------------------

    def _profile_handler(self, frame: Any, event: str, arg: Any) -> None:
        if not self._enabled:
            return
        state = self._state  # thread-local

        module = frame.f_globals.get("__name__", "")
        funcname = frame.f_code.co_name
        full_name = f"{module}.{funcname}" if module else funcname

        # Skip internals
        _skip = {"callflow_tracer", "threading", "_thread", "importlib"}
        if any(module.startswith(s) for s in _skip):
            return

        if event == "call":
            if state.depth >= self._MAX_DEPTH:
                return
            state.call_stack.append((full_name, time.perf_counter()))
            state.depth += 1

        elif event == "return" and state.call_stack:
            if state.depth > 0:
                state.depth -= 1
            callee, start = state.call_stack.pop()
            duration = time.perf_counter() - start
            caller = state.call_stack[-1][0] if state.call_stack else "<root>"
            self._graph.record_call(
                caller=caller,
                callee=callee,
                duration=duration,
                args=[],
                kwargs={},
                skip_reason=None,
            )
