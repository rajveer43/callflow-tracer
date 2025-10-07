"""psycopg2 integration for callflow-tracer."""
from __future__ import annotations

import time
from typing import Any, Callable

from ..tracer import CallGraph, get_current_graph

try:
    import psycopg2  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    psycopg2 = None  # type: ignore


def _get_graph() -> CallGraph:
    graph = get_current_graph()
    return graph if graph is not None else CallGraph()


def instrument_psycopg2(label: str = "psycopg2.query") -> None:
    """
    Monkey-patch psycopg2.connect to wrap returned connections and trace queries.
    """
    if psycopg2 is None:
        raise RuntimeError("psycopg2 is not installed. Install with extras: callflow-tracer[db]")

    original_connect = psycopg2.connect  # type: ignore

    def wrapped_connect(*args, **kwargs):  # type: ignore
        conn = original_connect(*args, **kwargs)
        return wrap_connection(conn, label=label)

    psycopg2.connect = wrapped_connect  # type: ignore


def wrap_connection(conn: Any, label: str = "psycopg2.query") -> Any:
    """Return a proxy connection whose cursor() produces wrapped cursors.

    psycopg2 connection methods like `cursor` are implemented in C and are
    read-only attributes, so we cannot assign to `conn.cursor`. Instead, we
    return a lightweight proxy that delegates all attributes to the original
    connection, but overrides `cursor()` to wrap the resulting cursor.
    """

    class TracedConnection:
        def __init__(self, inner_conn: Any, trace_label: str) -> None:
            self._inner_conn = inner_conn
            self._trace_label = trace_label

        def cursor(self, *args, **kwargs):  # type: ignore
            cursor = self._inner_conn.cursor(*args, **kwargs)
            return _wrap_cursor(cursor, label=self._trace_label)

        # Common connection methods delegated explicitly for performance/clarity
        def close(self) -> None:
            return self._inner_conn.close()

        def commit(self) -> None:
            return self._inner_conn.commit()

        def rollback(self) -> None:
            return self._inner_conn.rollback()

        def __enter__(self):
            self._inner_conn.__enter__()
            return self

        def __exit__(self, exc_type, exc, tb):
            return self._inner_conn.__exit__(exc_type, exc, tb)

        def __getattr__(self, name: str):
            # Delegate any other attribute access to the real connection
            return getattr(self._inner_conn, name)

    return TracedConnection(conn, label)


def _wrap_cursor(cursor: Any, label: str) -> Any:
    original_execute = cursor.execute
    original_executemany = getattr(cursor, "executemany", None)

    def timed_execute(sql, params=None):  # type: ignore
        start = time.time()
        try:
            return original_execute(sql, params)
        finally:
            duration = time.time() - start
            sql_preview = " ".join(str(sql).split())[:120]
            callee = f"sql:{sql_preview}"
            _get_graph().record_call(label, callee, duration)

    def timed_executemany(sql, seq_of_params):  # type: ignore
        start = time.time()
        try:
            return original_executemany(sql, seq_of_params)
        finally:
            duration = time.time() - start
            sql_preview = " ".join(str(sql).split())[:120]
            callee = f"sql:{sql_preview}"
            _get_graph().record_call(label, callee, duration)

    cursor.execute = timed_execute  # type: ignore
    if original_executemany:
        cursor.executemany = timed_executemany  # type: ignore

    return cursor
