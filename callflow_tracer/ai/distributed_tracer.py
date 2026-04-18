"""
Distributed tracing integration module for CallFlow Tracer.

Connects with distributed tracing systems like Jaeger, Zipkin, and OpenTelemetry.
Enables cross-service analysis and correlation of traces across microservices.

Example:
    from callflow_tracer.ai import DistributedTracer

    tracer = DistributedTracer(
        backend='jaeger',
        service_name='my-service'
    )

    with tracer.trace_scope() as graph:
        my_microservice_call()

    analysis = tracer.analyze_distributed_trace(trace_id)
"""

import logging
import uuid
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, ContextManager
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from contextlib import contextmanager

logger = logging.getLogger(__name__)


@dataclass
class DistributedSpan:
    """A span in distributed trace."""

    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    service_name: str
    start_time: str
    end_time: str
    duration_ms: float
    tags: Dict[str, Any]
    logs: List[Dict[str, Any]]
    status: str  # 'ok', 'error'


@dataclass
class DistributedTraceAnalysis:
    """Analysis of distributed trace."""

    trace_id: str
    total_duration_ms: float
    service_count: int
    span_count: int
    critical_path_duration_ms: float
    services: Dict[str, Dict[str, Any]]
    bottlenecks: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]


@dataclass
class TracerConfig:
    """Configuration for distributed tracer behavior and thresholds."""

    # Backend configuration
    backend: str = "jaeger"
    """Tracing backend ('jaeger', 'zipkin', 'opentelemetry')."""

    service_name: str = "default-service"
    """Service name for this tracer."""

    endpoint: Optional[str] = None
    """Optional custom endpoint. Defaults based on backend."""

    api_key: Optional[str] = None
    """Optional API key for authentication."""

    # Analysis thresholds
    bottleneck_percentile: int = 10
    """Top N% of spans by duration are flagged as bottlenecks."""

    critical_path_threshold_ms: float = 100.0
    """Spans with duration > threshold are highlighted in critical path."""

    # Sampling and limits
    sampling_rate: float = 1.0
    """Sampling rate (0.0 to 1.0). 1.0 = sample all traces."""

    max_spans_per_trace: int = 10000
    """Maximum spans to store per trace to prevent memory issues."""

    # Connection settings
    endpoint_timeout_s: int = 5
    """Timeout for endpoint connections in seconds."""

    def get_default_endpoint(self) -> str:
        """Get default endpoint for the configured backend."""
        endpoints = {
            "jaeger": "http://localhost:6831",
            "zipkin": "http://localhost:9411",
            "opentelemetry": "http://localhost:4317",
        }
        return endpoints.get(self.backend, "http://localhost:6831")

    def get_effective_endpoint(self) -> str:
        """Get the endpoint to use (custom or default)."""
        return self.endpoint or self.get_default_endpoint()


# ============================================================================
# Backend Strategy Pattern Implementation
# ============================================================================


class TracingBackend(ABC):
    """Abstract base class for tracing backends."""

    @abstractmethod
    def initialize(self, config: "TracerConfig") -> Any:
        """
        Initialize the backend with given configuration.

        Args:
            config: TracerConfig instance

        Returns:
            Initialized tracer object

        Raises:
            ImportError: If required library is not installed
            ValueError: If configuration is invalid
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get the name of the backend."""
        pass


class JaegerBackend(TracingBackend):
    """Jaeger distributed tracing backend."""

    def get_name(self) -> str:
        """Get backend name."""
        return "jaeger"

    def initialize(self, config: TracerConfig) -> Any:
        """Initialize Jaeger tracer."""
        try:
            from jaeger_client import Config

            endpoint = config.get_effective_endpoint()
            host, port = DistributedTracer._parse_endpoint(endpoint)

            logger.debug(f"Initializing Jaeger: {host}:{port}")

            jaeger_config = Config(
                config={
                    "sampler": {
                        "type": "const",
                        "param": 1,
                    },
                    "local_agent": {
                        "reporting_host": host,
                        "reporting_port": port,
                    },
                    "logging": True,
                },
                service_name=config.service_name,
            )
            return jaeger_config.initialize_tracer()

        except ImportError as e:
            msg = "Jaeger client not installed. Install with: pip install jaeger-client"
            logger.error(msg)
            raise ImportError(msg) from e
        except Exception as e:
            logger.error(f"Failed to initialize Jaeger: {e}", exc_info=True)
            raise


class ZipkinBackend(TracingBackend):
    """Zipkin distributed tracing backend."""

    def __init__(self, transport_handler):
        """Initialize with transport handler."""
        self.transport_handler = transport_handler

    def get_name(self) -> str:
        """Get backend name."""
        return "zipkin"

    def initialize(self, config: TracerConfig) -> Any:
        """Initialize Zipkin tracer."""
        try:
            from py_zipkin.zipkin import Zipkin

            logger.debug(f"Initializing Zipkin: {config.get_effective_endpoint()}")

            return Zipkin(
                service_name=config.service_name,
                transport_handler=self.transport_handler,
            )

        except ImportError as e:
            msg = "py_zipkin not installed. Install with: pip install py_zipkin"
            logger.error(msg)
            raise ImportError(msg) from e
        except Exception as e:
            logger.error(f"Failed to initialize Zipkin: {e}", exc_info=True)
            raise


class OpenTelemetryBackend(TracingBackend):
    """OpenTelemetry distributed tracing backend."""

    def get_name(self) -> str:
        """Get backend name."""
        return "opentelemetry"

    def initialize(self, config: TracerConfig) -> Any:
        """Initialize OpenTelemetry tracer."""
        try:
            from opentelemetry import trace
            from opentelemetry.exporter.jaeger.thrift import JaegerExporter
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor

            endpoint = config.get_effective_endpoint()
            host, port = DistributedTracer._parse_endpoint(endpoint)

            logger.debug(f"Initializing OpenTelemetry: {host}:{port}")

            jaeger_exporter = JaegerExporter(
                agent_host_name=host,
                agent_port=port,
            )

            trace.set_tracer_provider(TracerProvider())
            trace.get_tracer_provider().add_span_processor(
                BatchSpanProcessor(jaeger_exporter)
            )

            return trace.get_tracer(__name__)

        except ImportError as e:
            msg = "OpenTelemetry not installed. Install with: pip install opentelemetry-api opentelemetry-sdk"
            logger.error(msg)
            raise ImportError(msg) from e
        except Exception as e:
            logger.error(f"Failed to initialize OpenTelemetry: {e}", exc_info=True)
            raise


class BackendFactory:
    """Factory for creating tracing backend instances."""

    _backends: Dict[str, type] = {}

    @classmethod
    def register(cls, name: str, backend_class: type) -> None:
        """
        Register a backend implementation.

        Args:
            name: Backend name
            backend_class: Backend class
        """
        cls._backends[name] = backend_class
        logger.debug(f"Registered backend: {name}")

    @classmethod
    def create(cls, name: str, *args, **kwargs) -> TracingBackend:
        """
        Create a backend instance.

        Args:
            name: Backend name
            *args: Positional arguments for backend constructor
            **kwargs: Keyword arguments for backend constructor

        Returns:
            Initialized backend instance

        Raises:
            ValueError: If backend not registered
        """
        if name not in cls._backends:
            msg = f"Unknown backend: {name}. Registered: {list(cls._backends.keys())}"
            logger.error(msg)
            raise ValueError(msg)

        backend_class = cls._backends[name]
        logger.debug(f"Creating backend instance: {name}")
        return backend_class(*args, **kwargs)


# Register built-in backends
BackendFactory.register("jaeger", JaegerBackend)
BackendFactory.register("opentelemetry", OpenTelemetryBackend)


class DistributedTracer:
    """Distributed tracing integration with configurable backends."""

    def __init__(
        self,
        config: Optional[TracerConfig] = None,
        backend: Optional[str] = None,
        service_name: Optional[str] = None,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """
        Initialize distributed tracer.

        Args:
            config: TracerConfig object. Takes precedence over individual parameters.
            backend: Tracing backend ('jaeger', 'zipkin', 'opentelemetry').
                     Ignored if config provided.
            service_name: Service name for traces. Ignored if config provided.
            endpoint: Optional custom endpoint. Ignored if config provided.
            api_key: Optional API key for authentication. Ignored if config provided.

        Raises:
            ValueError: If backend is not supported
        """
        # Use config or build from individual parameters
        if config is not None:
            self.config = config
        else:
            self.config = TracerConfig(
                backend=backend or "jaeger",
                service_name=service_name or "default-service",
                endpoint=endpoint,
                api_key=api_key,
            )

        # Validate backend
        supported_backends = {"jaeger", "zipkin", "opentelemetry"}
        if self.config.backend not in supported_backends:
            msg = (
                f"Unsupported backend '{self.config.backend}'. "
                f"Supported: {supported_backends}"
            )
            logger.error(msg)
            raise ValueError(msg)

        self._tracer = None
        self._current_trace_id: Optional[str] = None
        self._spans: List[DistributedSpan] = []
        self._backend: Optional[TracingBackend] = None

        logger.debug(
            f"Initialized DistributedTracer with backend={self.config.backend}, "
            f"service_name={self.config.service_name}"
        )

    def initialize(self) -> None:
        """
        Initialize tracer connection with configured backend using Strategy pattern.

        Raises:
            ImportError: If required backend library is not installed
            ValueError: If backend is not recognized or connection fails
        """
        logger.info(f"Initializing {self.config.backend} tracer")

        try:
            # Use factory to create appropriate backend
            if self.config.backend == "zipkin":
                self._backend = BackendFactory.create(
                    "zipkin", transport_handler=self._zipkin_transport
                )
            else:
                self._backend = BackendFactory.create(self.config.backend)

            # Initialize the backend
            self._tracer = self._backend.initialize(self.config)
            logger.info(f"{self.config.backend} tracer initialized successfully")

        except (ImportError, ValueError):
            logger.error(f"Failed to initialize {self.config.backend} tracer")
            raise
        except Exception:
            logger.exception("Unexpected error initializing tracer")
            raise

    @staticmethod
    def _parse_endpoint(endpoint: str) -> tuple:
        """
        Parse endpoint URL into (host, port).

        Args:
            endpoint: Endpoint URL (e.g., "http://localhost:6831")

        Returns:
            Tuple of (host, port)

        Raises:
            ValueError: If endpoint format is invalid
        """
        if not endpoint or not isinstance(endpoint, str):
            raise ValueError(f"Invalid endpoint: {endpoint}")

        try:
            # Remove protocol
            parts = endpoint.split("://")
            if len(parts) > 1:
                endpoint = parts[1]

            # Split host and port
            host_port = endpoint.split(":")
            if len(host_port) < 2:
                raise ValueError(f"Endpoint missing port: {endpoint}")

            host = host_port[0]
            port = int(host_port[-1])

            if not host or port <= 0 or port > 65535:
                raise ValueError(f"Invalid host or port: {host}:{port}")

            return host, port

        except (ValueError, IndexError) as e:
            msg = f"Failed to parse endpoint '{endpoint}': {e}"
            logger.error(msg)
            raise ValueError(msg) from e

    @contextmanager
    def trace_scope(self, operation_name: str = "default_operation"):
        """
        Context manager for tracing a scope.

        Args:
            operation_name: Name of the operation

        Yields:
            Trace context with trace_id and service info

        Example:
            with tracer.trace_scope("api_call") as context:
                # Your code here
                pass  # Automatically records timing
        """
        if not operation_name or not isinstance(operation_name, str):
            logger.warning(f"Invalid operation_name: {operation_name}, using default")
            operation_name = "default_operation"

        trace_id = str(uuid.uuid4())
        self._current_trace_id = trace_id
        self._spans = []

        start_time = datetime.now()
        logger.debug(f"Started trace scope: {trace_id} ({operation_name})")

        try:
            yield {
                "trace_id": trace_id,
                "operation_name": operation_name,
                "service_name": self.config.service_name,
            }
        finally:
            end_time = datetime.now()
            duration_ms = (end_time - start_time).total_seconds() * 1000

            # Record root span
            root_span = DistributedSpan(
                trace_id=trace_id,
                span_id=str(uuid.uuid4()),
                parent_span_id=None,
                operation_name=operation_name,
                service_name=self.config.service_name,
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                duration_ms=duration_ms,
                tags={},
                logs=[],
                status="ok",
            )

            self._spans.insert(0, root_span)
            self._current_trace_id = None
            logger.debug(f"Completed trace scope: {trace_id} (duration: {duration_ms:.2f}ms)")

    def record_span(
        self,
        operation_name: str,
        duration_ms: float,
        parent_span_id: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
        status: str = "ok",
    ) -> str:
        """
        Record a span in the current trace.

        Args:
            operation_name: Name of the operation
            duration_ms: Duration in milliseconds
            parent_span_id: Optional parent span ID
            tags: Optional tags for span
            status: Span status ('ok' or 'error')

        Returns:
            Span ID (empty string if no active trace)

        Raises:
            ValueError: If operation_name is invalid or duration_ms is negative
        """
        # Validate inputs
        if not self._current_trace_id:
            logger.debug("No active trace scope for recording span")
            return ""

        if not operation_name or not isinstance(operation_name, str):
            msg = f"Invalid operation_name: {operation_name}"
            logger.error(msg)
            raise ValueError(msg)

        if duration_ms < 0:
            msg = f"Invalid duration_ms: {duration_ms} (must be >= 0)"
            logger.error(msg)
            raise ValueError(msg)

        if status not in ("ok", "error"):
            logger.warning(f"Invalid span status: {status}, defaulting to 'ok'")
            status = "ok"

        span_id = str(uuid.uuid4())
        now = datetime.now()

        span = DistributedSpan(
            trace_id=self._current_trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            service_name=self.config.service_name,
            start_time=now.isoformat(),
            end_time=(now + timedelta(milliseconds=duration_ms)).isoformat(),
            duration_ms=duration_ms,
            tags=tags or {},
            logs=[],
            status=status,
        )

        self._spans.append(span)
        logger.debug(
            f"Recorded span: {span_id} ({operation_name}) "
            f"duration={duration_ms:.2f}ms status={status}"
        )

        return span_id

    def analyze_distributed_trace(self, trace_id: str) -> DistributedTraceAnalysis:
        """
        Analyze a distributed trace.

        Args:
            trace_id: Trace ID to analyze

        Returns:
            DistributedTraceAnalysis dataclass with complete analysis

        Raises:
            ValueError: If trace_id is invalid or trace not found
        """
        # Validate trace ID
        if not trace_id or not isinstance(trace_id, str):
            msg = f"Invalid trace_id: {trace_id}"
            logger.error(msg)
            raise ValueError(msg)

        logger.info(f"Analyzing trace: {trace_id}")

        # Fetch spans from cache or backend
        if trace_id != self._current_trace_id:
            logger.debug(f"Fetching trace from backend: {trace_id}")
            spans = self._fetch_trace_from_backend(trace_id)
        else:
            logger.debug(f"Using cached spans for trace: {trace_id}")
            spans = self._spans

        if not spans:
            logger.warning(f"No spans found for trace: {trace_id}")
            # Return empty analysis
            return DistributedTraceAnalysis(
                trace_id=trace_id,
                total_duration_ms=0.0,
                service_count=0,
                span_count=0,
                critical_path_duration_ms=0.0,
                services={},
                bottlenecks=[],
                errors=[],
            )

        try:
            # Compute total duration
            total_duration = max(
                (
                    datetime.fromisoformat(s.end_time)
                    - datetime.fromisoformat(s.start_time)
                ).total_seconds()
                * 1000
                for s in spans
            )
            logger.debug(f"Total trace duration: {total_duration:.2f}ms")

            # Run analysis components
            services = self._group_spans_by_service(spans)
            bottlenecks = self._identify_bottlenecks(spans)
            errors = [s for s in spans if s.status == "error"]
            critical_path = self._compute_critical_path(spans)

            logger.info(
                f"Trace analysis complete: {len(services)} services, "
                f"{len(bottlenecks)} bottlenecks, {len(errors)} errors"
            )

            analysis = DistributedTraceAnalysis(
                trace_id=trace_id,
                total_duration_ms=total_duration,
                service_count=len(services),
                span_count=len(spans),
                critical_path_duration_ms=critical_path,
                services=services,
                bottlenecks=bottlenecks,
                errors=[asdict(e) for e in errors],
            )

            return analysis

        except Exception:
            logger.exception(f"Error analyzing trace: {trace_id}")
            raise

    def _fetch_trace_from_backend(self, trace_id: str) -> List[DistributedSpan]:
        """Fetch trace from backend."""
        # Implementation depends on backend
        return []

    def _group_spans_by_service(
        self, spans: List[DistributedSpan]
    ) -> Dict[str, Dict[str, Any]]:
        """Group spans by service."""
        services = {}

        for span in spans:
            if span.service_name not in services:
                services[span.service_name] = {
                    "span_count": 0,
                    "total_duration_ms": 0,
                    "operations": {},
                }

            service = services[span.service_name]
            service["span_count"] += 1
            service["total_duration_ms"] += span.duration_ms

            if span.operation_name not in service["operations"]:
                service["operations"][span.operation_name] = {
                    "count": 0,
                    "total_duration_ms": 0,
                }

            service["operations"][span.operation_name]["count"] += 1
            service["operations"][span.operation_name][
                "total_duration_ms"
            ] += span.duration_ms

        return services

    def _identify_bottlenecks(
        self, spans: List[DistributedSpan]
    ) -> List[Dict[str, Any]]:
        """
        Identify bottlenecks in trace using configured percentile threshold.

        Args:
            spans: List of spans to analyze

        Returns:
            List of bottleneck information dicts, sorted by duration
        """
        if not spans:
            return []

        bottlenecks = []

        # Sort by duration descending
        sorted_spans = sorted(spans, key=lambda s: s.duration_ms, reverse=True)

        # Calculate top N% based on config
        top_count = max(1, len(sorted_spans) // self.config.bottleneck_percentile)
        total_duration = sum(s.duration_ms for s in spans)

        logger.debug(
            f"Identifying bottlenecks: top {self.config.bottleneck_percentile}% "
            f"of {len(sorted_spans)} spans = {top_count} spans"
        )

        for span in sorted_spans[:top_count]:
            percentage = (
                (span.duration_ms / total_duration) * 100 if total_duration > 0 else 0
            )
            bottleneck = {
                "operation": span.operation_name,
                "service": span.service_name,
                "duration_ms": span.duration_ms,
                "percentage": percentage,
            }
            bottlenecks.append(bottleneck)
            logger.debug(
                f"Bottleneck: {span.operation_name} "
                f"({span.duration_ms:.2f}ms, {percentage:.1f}%)"
            )

        return bottlenecks

    def _compute_critical_path(self, spans: List[DistributedSpan]) -> float:
        """Compute critical path duration."""
        if not spans:
            return 0.0

        # Build dependency graph
        graph = {}
        for span in spans:
            if span.span_id not in graph:
                graph[span.span_id] = {"duration": span.duration_ms, "children": []}

            if span.parent_span_id:
                if span.parent_span_id not in graph:
                    graph[span.parent_span_id] = {"duration": 0, "children": []}
                graph[span.parent_span_id]["children"].append(span.span_id)

        # Find root span
        root_spans = [s for s in spans if s.parent_span_id is None]

        if not root_spans:
            return sum(s.duration_ms for s in spans)

        # Compute longest path
        def longest_path(span_id):
            if span_id not in graph:
                return 0

            node = graph[span_id]
            if not node["children"]:
                return node["duration"]

            max_child_path = max(longest_path(child) for child in node["children"])
            return node["duration"] + max_child_path

        return max(longest_path(s.span_id) for s in root_spans)

    def _zipkin_transport(self, encoded_span):
        """
        Transport handler for sending spans to Zipkin.

        Args:
            encoded_span: Encoded span data to send

        Raises:
            Exception: If transport fails
        """
        try:
            import requests
        except ImportError as e:
            msg = "requests library not installed. Install with: pip install requests"
            logger.error(msg)
            raise ImportError(msg) from e

        try:
            endpoint = self.config.get_effective_endpoint()
            response = requests.post(
                f"{endpoint}/api/v2/spans",
                data=encoded_span,
                headers={"Content-Type": "application/x-protobuf"},
                timeout=self.config.endpoint_timeout_s,
            )
            response.raise_for_status()
            logger.debug("Span sent to Zipkin successfully")

        except requests.RequestException as e:
            msg = f"Error sending span to Zipkin: {e}"
            logger.error(msg, exc_info=True)
            raise
        except Exception:
            logger.exception("Unexpected error in Zipkin transport")
            raise
