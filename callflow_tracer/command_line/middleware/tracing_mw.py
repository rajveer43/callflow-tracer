"""
Tracing middleware — the bridge between the CLI layer and the agent runtime.

This is the most important middleware for the agent runtime evolution:
  - It listens for TRACE_RECORDED events from commands that produce call graphs.
  - It emits those graphs upstream via the EventBus so the agent runtime can
    ingest them as tool-call trace data without polling or file I/O.

DSA note:
  - ExecutionStack: a list used as LIFO stack tracking nested command invocations.
    push on entry (process start), pop on exit (after call_next returns).
    Stack depth > 1 indicates a command triggered another command (REPL / pipelines).
    This is the foundation for undo/redo: replay the stack in reverse.

Current behaviour: lightweight — captures command name, timing, exit code into
ctx.extra["tracing.*"] for downstream inspection. The heavier call-graph
capture happens inside the command itself (via core/tracer.trace_scope).
"""

from __future__ import annotations

import time

from ..events.bus import EventBus
from ..events.types import CLIEvent, EventType
from ..interfaces.command import CommandContext, CommandResult
from ..interfaces.middleware import Middleware, NextHandler

# Module-level execution stack — tracks nested invocations for undo/REPL.
# DSA: list used as LIFO stack (append = push, pop = pop). O(1) both ends.
_execution_stack: list[str] = []


def get_execution_stack() -> list[str]:
    """Return a snapshot of the current execution stack (outermost first)."""
    return list(_execution_stack)


class TracingMiddleware(Middleware):
    """
    Execution stack manager and trace event bridge.

    On COMMAND_SUCCEEDED it emits a TRACE_RECORDED event if the command
    produced structured output in result.data["graph"]. This lets the agent
    runtime subscribe to CLI-captured call graphs without any coupling
    between the command and the agent layer.
    """

    def __init__(self, bus: EventBus) -> None:
        self._bus = bus

    def process(self, ctx: CommandContext, call_next: NextHandler) -> CommandResult:
        name = ctx.args.command if hasattr(ctx.args, "command") else "unknown"

        # Push onto execution stack (LIFO)
        _execution_stack.append(name)
        ctx.extra["tracing.stack_depth"] = len(_execution_stack)
        ctx.extra["tracing.start_ms"] = time.monotonic() * 1000

        try:
            result = call_next(ctx)
        finally:
            # Always pop — even if call_next raises (middleware must not leak)
            if _execution_stack and _execution_stack[-1] == name:
                _execution_stack.pop()

        # If the command produced a call graph, emit it as a TRACE_RECORDED event.
        # The agent runtime subscribes to this event to ingest graphs.
        if result.ok and "graph" in result.data:
            self._bus.emit(CLIEvent(
                EventType.TRACE_RECORDED,
                command_name=name,
                payload={
                    "graph": result.data["graph"],
                    "command": name,
                    "duration_ms": result.duration_ms,
                },
            ))

        return result
