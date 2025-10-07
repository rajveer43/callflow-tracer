"""Django integration for callflow-tracer."""
from __future__ import annotations

import time
from typing import Optional, Callable, Any

from ..tracer import CallGraph, get_current_graph
try:
    from django.db import connection  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    connection = None  # type: ignore


class DjangoTracingMiddleware:
    """
    Add to MIDDLEWARE in Django settings:
        'callflow_tracer.integrations.django_integration.DjangoTracingMiddleware'
    """

    def __init__(self, get_response: Callable[[Any], Any]):
        self.get_response = get_response
        self.request_node_name = "django.request"
        self._graph: Optional[CallGraph] = None

    def _get_graph(self) -> CallGraph:
        if self._graph is None:
            graph = get_current_graph()
            self._graph = graph if graph is not None else CallGraph()
        return self._graph

    def __call__(self, request):
        # Support sync path
        start = time.time()
        try:
            response = self.get_response(request)
            return response
        finally:
            # If response is awaitable (async), don't record here; handled in async path
            if not hasattr(response, "__await__"):
                duration = time.time() - start
                target = self._get_view_name(request)
                self._get_graph().record_call(self.request_node_name, target, duration)

    async def __acall__(self, request):  # type: ignore
        # Django treats async middleware via awaitable response
        start = time.time()
        response = await self.get_response(request)  # type: ignore
        duration = time.time() - start
        target = self._get_view_name(request)
        self._get_graph().record_call(self.request_node_name, target, duration)
        return response

    # Django >=3.1 will call async __call__ if get_response is async. We expose both.
    __call__._is_coroutine = False  # type: ignore

    def _get_view_name(self, request) -> str:
        # Attempt to fetch resolved view
        resolver_match = getattr(request, "resolver_match", None)
        if resolver_match and resolver_match.func:
            view = resolver_match.func
            name = getattr(view, "__name__", "<unknown>")
            mod = getattr(view, "__module__", "")
            return f"{mod}.{name}" if mod and mod != "__main__" else name
        # Fallback to path
        return f"django.route:{getattr(request, 'path', '<unknown>')}"
