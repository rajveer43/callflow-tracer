"""FastAPI/Starlette integration for callflow-tracer."""
from __future__ import annotations

import time
from typing import Callable, Optional

try:
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.requests import Request
    from starlette.responses import Response
except Exception:  # pragma: no cover - optional dependency
    BaseHTTPMiddleware = object  # type: ignore
    Request = object  # type: ignore
    Response = object  # type: ignore

from ..tracer import CallGraph, get_current_graph


class CallFlowMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, request_node_name: str = "fastapi.request"):
        super().__init__(app)
        self.request_node_name = request_node_name
        self._graph: Optional[CallGraph] = None

    def _get_graph(self) -> CallGraph:
        if self._graph is None:
            graph = get_current_graph()
            self._graph = graph if graph is not None else CallGraph()
        return self._graph

    async def dispatch(self, request: Request, call_next: Callable[[Request], Response]) -> Response:  # type: ignore
        start = time.time()
        try:
            response = await call_next(request)
            return response
        finally:
            duration = time.time() - start
            endpoint = getattr(request.scope, "endpoint", None)
            if endpoint:
                name = getattr(endpoint, "__name__", "<unknown>")
                mod = getattr(endpoint, "__module__", "")
                target = f"{mod}.{name}" if mod and mod != "__main__" else name
            else:
                # Fallback to route path
                path = request.url.path
                target = f"fastapi.route:{path}"
            self._get_graph().record_call(self.request_node_name, target, duration)


def setup_fastapi_tracing(app, request_node_name: str = "fastapi.request"):
    """Attach CallFlowMiddleware to a FastAPI or Starlette app."""
    app.add_middleware(CallFlowMiddleware, request_node_name=request_node_name)
    return app
