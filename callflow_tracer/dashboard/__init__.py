"""callflow_tracer.dashboard — live WebSocket streaming dashboard.

Quick start::

    from callflow_tracer.dashboard import DashboardServer, DashboardRenderer
    from callflow_tracer.llm import get_llm_registry
    from callflow_tracer.runtime import SamplingProfiler

    renderer = DashboardRenderer(
        call_graph=tracer.call_graph,
        llm_registry=get_llm_registry(),
        sampler=SamplingProfiler(),
    )
    server = DashboardServer(renderer, port=7474)
    server.start()
    print(f"Open http://localhost:7474 in your browser")
    # ... run your workload ...
    server.stop()

Requires: pip install websockets
"""

from .renderer import DashboardRenderer
from .server import DashboardServer

__all__ = ["DashboardRenderer", "DashboardServer"]
