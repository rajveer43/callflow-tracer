"""Flask integration for callflow-tracer."""
from __future__ import annotations

import time
from typing import Optional

from ..tracer import CallGraph, get_current_graph

_integration_graph: Optional[CallGraph] = None


def _get_graph() -> CallGraph:
    global _integration_graph
    graph = get_current_graph()
    if graph is not None:
        return graph
    if _integration_graph is None:
        _integration_graph = CallGraph()
    return _integration_graph


def setup_flask_tracing(app, request_node_name: str = "flask.request"):
    """
    Attach tracing to a Flask app.

    Args:
        app: Flask application instance
        request_node_name: Synthetic caller node for HTTP requests
    """

    @app.before_request
    def _cft_before_request():  # type: ignore
        from flask import g, request

        g._cft_start_time = time.time()
        # Best-effort route identification
        endpoint = request.endpoint or "<unknown>"
        g._cft_endpoint = f"flask.{endpoint}" if endpoint else "flask.<unknown>"

    @app.after_request
    def _cft_after_request(response):  # type: ignore
        from flask import g

        start = getattr(g, "_cft_start_time", None)
        endpoint = getattr(g, "_cft_endpoint", "flask.<unknown>")
        if start is not None:
            duration = time.time() - start
            graph = _get_graph()
            graph.record_call(request_node_name, endpoint, duration)
        return response

    return app
