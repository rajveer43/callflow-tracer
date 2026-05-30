"""callflow_tracer.runtime — low-overhead profiling and multi-thread tracing.

Quick start::

    # Statistical sampler
    from callflow_tracer.runtime import SamplingProfiler
    with SamplingProfiler(interval_ms=5) as profiler:
        run_workload()
    for path in profiler.top_hot_paths(10):
        print(path)

    # Chrome timeline export
    from callflow_tracer.runtime import ChromeTimelineExporter
    ChromeTimelineExporter().export(call_graph, "trace.json")

    # Multi-thread tracing
    from callflow_tracer.runtime import ThreadedCallTracer
    with ThreadedCallTracer() as tracer:
        run_multi_threaded_workload()
    graph = tracer.graph
"""

from .sampler import HotPath, SamplingProfiler, StackSample
from .thread_tracer import ThreadedCallTracer, ThreadedCallGraph
from .timeline import ChromeTimelineExporter, TraceEvent

__all__ = [
    "SamplingProfiler",
    "HotPath",
    "StackSample",
    "ThreadedCallTracer",
    "ThreadedCallGraph",
    "ChromeTimelineExporter",
    "TraceEvent",
]
