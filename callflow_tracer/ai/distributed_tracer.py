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

from typing import Dict, List, Any, Optional, ContextManager
from dataclasses import dataclass, asdict
from datetime import datetime
from contextlib import contextmanager
import json


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


class DistributedTracer:
    """Distributed tracing integration."""
    
    def __init__(self, backend: str = 'jaeger',
                 service_name: str = 'default-service',
                 endpoint: Optional[str] = None,
                 api_key: Optional[str] = None):
        """
        Initialize distributed tracer.
        
        Args:
            backend: Tracing backend ('jaeger', 'zipkin', 'opentelemetry')
            service_name: Service name for traces
            endpoint: Optional custom endpoint
            api_key: Optional API key for authentication
        """
        self.backend = backend
        self.service_name = service_name
        self.endpoint = endpoint or self._get_default_endpoint(backend)
        self.api_key = api_key
        self._tracer = None
        self._current_trace_id: Optional[str] = None
        self._spans: List[DistributedSpan] = []
    
    def _get_default_endpoint(self, backend: str) -> str:
        """Get default endpoint for backend."""
        endpoints = {
            'jaeger': 'http://localhost:6831',
            'zipkin': 'http://localhost:9411',
            'opentelemetry': 'http://localhost:4317'
        }
        return endpoints.get(backend, 'http://localhost:6831')
    
    def initialize(self) -> None:
        """Initialize tracer connection."""
        if self.backend == 'jaeger':
            self._initialize_jaeger()
        elif self.backend == 'zipkin':
            self._initialize_zipkin()
        elif self.backend == 'opentelemetry':
            self._initialize_opentelemetry()
    
    def _initialize_jaeger(self) -> None:
        """Initialize Jaeger tracer."""
        try:
            from jaeger_client import Config
            
            config = Config(
                config={
                    'sampler': {
                        'type': 'const',
                        'param': 1,
                    },
                    'local_agent': {
                        'reporting_host': self.endpoint.split('://')[1].split(':')[0],
                        'reporting_port': int(self.endpoint.split(':')[-1]),
                    },
                    'logging': True,
                },
                service_name=self.service_name,
            )
            self._tracer = config.initialize_tracer()
        except ImportError:
            print("Jaeger client not installed. Install with: pip install jaeger-client")
    
    def _initialize_zipkin(self) -> None:
        """Initialize Zipkin tracer."""
        try:
            from py_zipkin.zipkin import Zipkin
            
            self._tracer = Zipkin(
                service_name=self.service_name,
                transport_handler=self._zipkin_transport,
            )
        except ImportError:
            print("py_zipkin not installed. Install with: pip install py_zipkin")
    
    def _initialize_opentelemetry(self) -> None:
        """Initialize OpenTelemetry tracer."""
        try:
            from opentelemetry import trace
            from opentelemetry.exporter.jaeger.thrift import JaegerExporter
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor
            
            jaeger_exporter = JaegerExporter(
                agent_host_name=self.endpoint.split('://')[1].split(':')[0],
                agent_port=int(self.endpoint.split(':')[-1]),
            )
            
            trace.set_tracer_provider(TracerProvider())
            trace.get_tracer_provider().add_span_processor(
                BatchSpanProcessor(jaeger_exporter)
            )
            
            self._tracer = trace.get_tracer(__name__)
        except ImportError:
            print("OpenTelemetry not installed. Install with: pip install opentelemetry-api opentelemetry-sdk")
    
    @contextmanager
    def trace_scope(self, operation_name: str = 'default_operation'):
        """
        Context manager for tracing a scope.
        
        Args:
            operation_name: Name of the operation
            
        Yields:
            Trace context
        """
        import uuid
        from datetime import datetime
        
        trace_id = str(uuid.uuid4())
        self._current_trace_id = trace_id
        self._spans = []
        
        start_time = datetime.now()
        
        try:
            yield {
                'trace_id': trace_id,
                'operation_name': operation_name,
                'service_name': self.service_name
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
                service_name=self.service_name,
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                duration_ms=duration_ms,
                tags={},
                logs=[],
                status='ok'
            )
            
            self._spans.insert(0, root_span)
            self._current_trace_id = None
    
    def record_span(self, operation_name: str, duration_ms: float,
                   parent_span_id: Optional[str] = None,
                   tags: Optional[Dict[str, Any]] = None,
                   status: str = 'ok') -> str:
        """
        Record a span in the current trace.
        
        Args:
            operation_name: Name of the operation
            duration_ms: Duration in milliseconds
            parent_span_id: Optional parent span ID
            tags: Optional tags
            status: Span status ('ok', 'error')
            
        Returns:
            Span ID
        """
        import uuid
        from datetime import datetime, timedelta
        
        if not self._current_trace_id:
            return ""
        
        span_id = str(uuid.uuid4())
        now = datetime.now()
        
        span = DistributedSpan(
            trace_id=self._current_trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            service_name=self.service_name,
            start_time=now.isoformat(),
            end_time=(now + timedelta(milliseconds=duration_ms)).isoformat(),
            duration_ms=duration_ms,
            tags=tags or {},
            logs=[],
            status=status
        )
        
        self._spans.append(span)
        return span_id
    
    def analyze_distributed_trace(self, trace_id: str) -> Dict[str, Any]:
        """
        Analyze a distributed trace.
        
        Args:
            trace_id: Trace ID to analyze
            
        Returns:
            Analysis results
        """
        if trace_id != self._current_trace_id:
            # Fetch trace from backend
            spans = self._fetch_trace_from_backend(trace_id)
        else:
            spans = self._spans
        
        if not spans:
            return {}
        
        # Compute analysis
        total_duration = max(
            (datetime.fromisoformat(s.end_time) - 
             datetime.fromisoformat(s.start_time)).total_seconds() * 1000
            for s in spans
        )
        
        services = self._group_spans_by_service(spans)
        bottlenecks = self._identify_bottlenecks(spans)
        errors = [s for s in spans if s.status == 'error']
        
        critical_path = self._compute_critical_path(spans)
        
        analysis = DistributedTraceAnalysis(
            trace_id=trace_id,
            total_duration_ms=total_duration,
            service_count=len(services),
            span_count=len(spans),
            critical_path_duration_ms=critical_path,
            services=services,
            bottlenecks=bottlenecks,
            errors=[asdict(e) for e in errors]
        )
        
        return asdict(analysis)
    
    def _fetch_trace_from_backend(self, trace_id: str) -> List[DistributedSpan]:
        """Fetch trace from backend."""
        # Implementation depends on backend
        return []
    
    def _group_spans_by_service(self, spans: List[DistributedSpan]) -> Dict[str, Dict[str, Any]]:
        """Group spans by service."""
        services = {}
        
        for span in spans:
            if span.service_name not in services:
                services[span.service_name] = {
                    'span_count': 0,
                    'total_duration_ms': 0,
                    'operations': {}
                }
            
            service = services[span.service_name]
            service['span_count'] += 1
            service['total_duration_ms'] += span.duration_ms
            
            if span.operation_name not in service['operations']:
                service['operations'][span.operation_name] = {
                    'count': 0,
                    'total_duration_ms': 0
                }
            
            service['operations'][span.operation_name]['count'] += 1
            service['operations'][span.operation_name]['total_duration_ms'] += span.duration_ms
        
        return services
    
    def _identify_bottlenecks(self, spans: List[DistributedSpan]) -> List[Dict[str, Any]]:
        """Identify bottlenecks in trace."""
        bottlenecks = []
        
        # Sort by duration
        sorted_spans = sorted(spans, key=lambda s: s.duration_ms, reverse=True)
        
        # Top 10% are potential bottlenecks
        top_count = max(1, len(sorted_spans) // 10)
        
        for span in sorted_spans[:top_count]:
            bottlenecks.append({
                'operation': span.operation_name,
                'service': span.service_name,
                'duration_ms': span.duration_ms,
                'percentage': (span.duration_ms / sum(s.duration_ms for s in spans)) * 100
            })
        
        return bottlenecks
    
    def _compute_critical_path(self, spans: List[DistributedSpan]) -> float:
        """Compute critical path duration."""
        if not spans:
            return 0.0
        
        # Build dependency graph
        graph = {}
        for span in spans:
            if span.span_id not in graph:
                graph[span.span_id] = {
                    'duration': span.duration_ms,
                    'children': []
                }
            
            if span.parent_span_id:
                if span.parent_span_id not in graph:
                    graph[span.parent_span_id] = {'duration': 0, 'children': []}
                graph[span.parent_span_id]['children'].append(span.span_id)
        
        # Find root span
        root_spans = [s for s in spans if s.parent_span_id is None]
        
        if not root_spans:
            return sum(s.duration_ms for s in spans)
        
        # Compute longest path
        def longest_path(span_id):
            if span_id not in graph:
                return 0
            
            node = graph[span_id]
            if not node['children']:
                return node['duration']
            
            max_child_path = max(longest_path(child) for child in node['children'])
            return node['duration'] + max_child_path
        
        return max(longest_path(s.span_id) for s in root_spans)
    
    def _zipkin_transport(self, encoded_span):
        """Transport handler for Zipkin."""
        import requests
        
        try:
            requests.post(
                f"{self.endpoint}/api/v2/spans",
                data=encoded_span,
                headers={'Content-Type': 'application/x-protobuf'}
            )
        except Exception as e:
            print(f"Error sending span to Zipkin: {e}")
