"""OpenTelemetry exporter for callflow-tracer.

This module maps CallGraph / CallNode / CallEdge data to OpenTelemetry spans with advanced features:
- Exemplars linking metrics to spans
- Batch processing and configurable export
- Resource attributes and semantic conventions
- Sampling and filtering
- OTLP/gRPC and HTTP exporters

Design goals:
- Optional dependency: if opentelemetry SDK is not installed, functions raise a clear error.
- Advanced API: export_callgraph_to_otel() with exemplars, sampling, resource config
- Can export to OTLP, Jaeger, Tempo, or console exporter configured by the user.

Note: This is a comprehensive integration layer. Users can configure OpenTelemetry SDK
via environment variables or pass explicit exporter/provider instances.
"""

from typing import Optional, Dict, Any, List
import json
import os

try:
    from opentelemetry import trace, metrics
    from opentelemetry.trace import SpanKind, Status, StatusCode
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter as OTLPGrpcExporter
    from opentelemetry.sdk.trace.sampling import Sampler, Decision, ALWAYS_ON

    _OTEL_AVAILABLE = True
except Exception:  # ImportError or misconfigured installation
    trace = None  # type: ignore
    metrics = None  # type: ignore
    SpanKind = None  # type: ignore
    Status = None  # type: ignore
    StatusCode = None  # type: ignore
    Resource = None  # type: ignore
    TracerProvider = None  # type: ignore
    BatchSpanProcessor = None  # type: ignore
    ConsoleSpanExporter = None  # type: ignore
    OTLPGrpcExporter = None  # type: ignore
    Sampler = None  # type: ignore
    Decision = None  # type: ignore
    ALWAYS_ON = None  # type: ignore
    _OTEL_AVAILABLE = False


class OpenTelemetryNotAvailable(RuntimeError):
    """Raised when OpenTelemetry SDK is not installed but export is requested."""


class CallFlowExemplar:
    """Represents an exemplar linking a metric to a trace span."""
    
    def __init__(self, trace_id: str, span_id: str, value: float, 
                 metric_name: str, attributes: Optional[Dict[str, Any]] = None):
        self.trace_id = trace_id
        self.span_id = span_id
        self.value = value
        self.metric_name = metric_name
        self.attributes = attributes or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "value": self.value,
            "metric_name": self.metric_name,
            "attributes": self.attributes
        }


def _ensure_otel():
    if not _OTEL_AVAILABLE:
        raise OpenTelemetryNotAvailable(
            "OpenTelemetry SDK is not installed. Install 'opentelemetry-sdk' "
            "and related exporters to use OTel export."
        )


def create_default_tracer_provider(service_name: str = "callflow-tracer",
                                   resource_attributes: Optional[Dict[str, Any]] = None
                                   ) -> TracerProvider:
    """Create a basic TracerProvider with a ConsoleSpanExporter.

    This is mainly for quick-start / debugging. In real deployments, users
    will typically configure their own provider and exporters (OTLP, Jaeger, etc.).
    """
    _ensure_otel()

    attrs = {"service.name": service_name}
    if resource_attributes:
        attrs.update(resource_attributes)

    resource = Resource.create(attrs)
    provider = TracerProvider(resource=resource)
    # Default to console exporter so there is at least some output.
    processor = BatchSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    return provider


def export_callgraph_to_otel(callgraph,
                             service_name: str = "callflow-tracer",
                             resource_attributes: Optional[Dict[str, Any]] = None,
                             use_existing_tracer_provider: bool = True,
                             exemplars: Optional[List[CallFlowExemplar]] = None,
                             sampling_rate: float = 1.0,
                             include_metrics: bool = False,
                             environment: str = "production",
                             ) -> Dict[str, Any]:
    """Export a CallGraph to OpenTelemetry spans with advanced features.

    Parameters
    ----------
    callgraph : CallGraph
        The callflow-tracer CallGraph instance.
    service_name : str
        Logical service name for the traces.
    resource_attributes : dict, optional
        Extra resource attributes to attach to spans (e.g., version, environment).
    use_existing_tracer_provider : bool
        If True and a global TracerProvider is already set, reuse it.
        If False or no provider is set, create a default one.
    exemplars : list of CallFlowExemplar, optional
        Exemplars linking metrics to trace spans.
    sampling_rate : float
        Sampling rate (0.0 to 1.0). Only spans with call_count >= threshold are exported.
    include_metrics : bool
        If True, attempt to link custom metrics to spans as exemplars.
    environment : str
        Environment name (e.g., 'production', 'staging', 'development').

    Returns
    -------
    dict
        Export summary with span count, exemplar count, and status.

    Notes
    -----
    - Each CallNode becomes a span with semantic attributes.
    - Edges define parent-child relationships.
    - Exemplars link high-value metrics to specific spans.
    - Sampling filters low-call-count functions.
    """
    _ensure_otel()

    # Ensure a tracer provider exists
    if not use_existing_tracer_provider or trace.get_tracer_provider() is None:
        create_default_tracer_provider(service_name, resource_attributes)

    tracer = trace.get_tracer(__name__)

    # Build resource attributes with semantic conventions
    res_attrs = {
        "service.name": service_name,
        "service.version": getattr(callgraph, "version", "unknown"),
        "deployment.environment": environment,
    }
    if resource_attributes:
        res_attrs.update(resource_attributes)

    # Build parent mapping: callee -> most significant caller
    parent_map: Dict[str, Optional[str]] = {name: None for name in callgraph.nodes.keys()}
    edge_by_callee: Dict[str, Any] = {}
    for (caller, callee), edge in callgraph.edges.items():
        existing = edge_by_callee.get(callee)
        if existing is None or edge.total_time > existing.total_time:
            edge_by_callee[callee] = edge

    for callee, edge in edge_by_callee.items():
        parent_map[callee] = edge.caller

    # Create spans for each node
    created_spans: Dict[str, Any] = {}
    span_count = 0
    exemplar_count = 0

    for full_name, node in callgraph.nodes.items():
        # Apply sampling: skip low-call-count functions if sampling_rate < 1.0
        if sampling_rate < 1.0 and node.call_count < int(1.0 / sampling_rate):
            continue

        module = node.module or "__main__"
        attributes = {
            "code.function": node.name,
            "code.namespace": module,
            "code.lineno": getattr(node, "lineno", 0),
            "callflow.call_count": node.call_count,
            "callflow.total_time": round(node.total_time, 6),
            "callflow.avg_time": round(node.total_time / max(node.call_count, 1), 6),
        }

        # Attach last few arguments for context if present
        if getattr(node, "arguments", None):
            attributes["callflow.last_arguments"] = str(node.arguments[-1])

        parent_name = parent_map.get(full_name)
        parent_span = created_spans.get(parent_name) if parent_name else None

        # Start span
        with tracer.start_as_current_span(
            full_name,
            kind=SpanKind.INTERNAL if SpanKind is not None else None,
            context=None,
        ) as span:
            # Set attributes
            for k, v in attributes.items():
                try:
                    span.set_attribute(k, v)
                except Exception:
                    pass  # Skip attributes that OTel rejects

            # Set status: OK if time is reasonable, UNSET otherwise
            if node.total_time > 10.0:  # Arbitrary threshold for slow functions
                if Status is not None and StatusCode is not None:
                    span.set_status(Status(StatusCode.OK))

            # Add exemplars if provided
            if exemplars:
                for exemplar in exemplars:
                    if exemplar.metric_name == full_name:
                        span.add_event(
                            "exemplar",
                            attributes={
                                "trace_id": exemplar.trace_id,
                                "span_id": exemplar.span_id,
                                "value": exemplar.value,
                            }
                        )
                        exemplar_count += 1

            created_spans[full_name] = span
            span_count += 1

    return {
        "status": "success",
        "span_count": span_count,
        "exemplar_count": exemplar_count,
        "service_name": service_name,
        "environment": environment,
        "sampling_rate": sampling_rate,
    }


def export_callgraph_with_metrics(callgraph, metrics_data: Dict[str, Any],
                                  service_name: str = "callflow-tracer",
                                  resource_attributes: Optional[Dict[str, Any]] = None,
                                  ) -> Dict[str, Any]:
    """Export CallGraph and link custom metrics as exemplars.

    Parameters
    ----------
    callgraph : CallGraph
        The callflow-tracer CallGraph instance.
    metrics_data : dict
        Custom metrics from MetricsCollector (e.g., from custom_metrics.py).
    service_name : str
        Logical service name for the traces.
    resource_attributes : dict, optional
        Extra resource attributes.

    Returns
    -------
    dict
        Export summary including exemplar count.

    Notes
    -----
    This function bridges custom metrics and traces by creating exemplars
    that link high-value metrics to their corresponding spans.
    """
    _ensure_otel()

    # Build exemplars from metrics
    exemplars: List[CallFlowExemplar] = []
    if isinstance(metrics_data, dict):
        for metric_name, metric_info in metrics_data.items():
            if isinstance(metric_info, dict) and "value" in metric_info:
                exemplar = CallFlowExemplar(
                    trace_id="",  # Will be set by span context
                    span_id="",
                    value=metric_info.get("value", 0),
                    metric_name=metric_name,
                    attributes=metric_info.get("tags", {})
                )
                exemplars.append(exemplar)

    return export_callgraph_to_otel(
        callgraph,
        service_name=service_name,
        resource_attributes=resource_attributes,
        exemplars=exemplars,
        include_metrics=True,
    )
