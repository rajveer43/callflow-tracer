"""SQLAlchemy integration for callflow-tracer."""
from __future__ import annotations

import time
from typing import Optional

from ..tracer import CallGraph, get_current_graph

try:
    from sqlalchemy import event
    from sqlalchemy.engine import Engine
except Exception:  # pragma: no cover - optional dependency
    Engine = object  # type: ignore
    event = None  # type: ignore


def _get_graph() -> CallGraph:
    graph = get_current_graph()
    return graph if graph is not None else CallGraph()


def instrument_sqlalchemy_engine(engine: "Engine", label: str = "sqlalchemy.query") -> None:
    """
    Attach event listeners to a SQLAlchemy Engine to record query timings.

    Args:
        engine: SQLAlchemy Engine instance
        label: Synthetic caller node name for DB queries
    """
    if event is None:
        raise RuntimeError("SQLAlchemy is not installed. Install with extras: callflow-tracer[db]")

    @event.listens_for(engine, "before_cursor_execute")
    def _before_cursor_execute(conn, cursor, statement, parameters, context, executemany):  # noqa: D401
        context._cft_start_time = time.time()

    @event.listens_for(engine, "after_cursor_execute")
    def _after_cursor_execute(conn, cursor, statement, parameters, context, executemany):  # noqa: D401
        start = getattr(context, "_cft_start_time", None)
        if start is None:
            return
        duration = time.time() - start
        graph = _get_graph()
        # Keep callee as the SQL text truncated for readability
        sql_preview = " ".join(str(statement).split())[:120]
        callee = f"sql:{sql_preview}"
        graph.record_call(label, callee, duration)
