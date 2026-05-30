# DistributedTracer - Quick Reference

## Basic Usage

```python
from callflow_tracer.ai import DistributedTracer

# Simple tracer
tracer = DistributedTracer()
tracer.initialize()

# Use trace scope
with tracer.trace_scope("api_request") as context:
    tracer.record_span("db_query", duration_ms=45.0)
    tracer.record_span("cache_lookup", duration_ms=5.0)

# Analyze trace
analysis = tracer.analyze_distributed_trace(context["trace_id"])
print(f"Critical path: {analysis.critical_path_duration_ms}ms")
print(f"Services: {analysis.service_count}")
print(f"Bottlenecks: {len(analysis.bottlenecks)}")
```

## Custom Configuration

```python
from callflow_tracer.ai.distributed_tracer import TracerConfig, DistributedTracer

config = TracerConfig(
    backend="jaeger",                   # jaeger, zipkin, opentelemetry
    service_name="payment-service",
    endpoint="http://jaeger:6831",
    api_key="secret-key",
    bottleneck_percentile=15,          # Top 15% of spans
    critical_path_threshold_ms=100.0,
    sampling_rate=1.0,
    max_spans_per_trace=10000,
    endpoint_timeout_s=10
)

tracer = DistributedTracer(config=config)
tracer.initialize()
```

## Supported Backends

| Backend | Protocol | Default Endpoint | Install |
|---------|----------|------------------|---------|
| `jaeger` | Jaeger Thrift | `http://localhost:6831` | `pip install jaeger-client` |
| `zipkin` | Zipkin API v2 | `http://localhost:9411` | `pip install py_zipkin` |
| `opentelemetry` | OTLP | `http://localhost:4317` | `pip install opentelemetry-api` |

## API Reference

### DistributedTracer

```python
class DistributedTracer:
    def __init__(config: Optional[TracerConfig] = None, ...)
    def initialize(self) -> None
    
    @contextmanager
    def trace_scope(operation_name: str = "default_operation")
    
    def record_span(
        operation_name: str,
        duration_ms: float,
        parent_span_id: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
        status: str = "ok"  # 'ok' or 'error'
    ) -> str
    
    def analyze_distributed_trace(trace_id: str) -> DistributedTraceAnalysis
```

### TracerConfig

```python
@dataclass
class TracerConfig:
    backend: str = "jaeger"
    service_name: str = "default-service"
    endpoint: Optional[str] = None
    api_key: Optional[str] = None
    
    bottleneck_percentile: int = 10
    critical_path_threshold_ms: float = 100.0
    sampling_rate: float = 1.0
    max_spans_per_trace: int = 10000
    endpoint_timeout_s: int = 5
    
    def get_default_endpoint(self) -> str
    def get_effective_endpoint(self) -> str
```

### DistributedTraceAnalysis

```python
@dataclass
class DistributedTraceAnalysis:
    trace_id: str
    total_duration_ms: float
    service_count: int
    span_count: int
    critical_path_duration_ms: float
    services: Dict[str, Dict[str, Any]]
    bottlenecks: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]
```

## Logging

Enable debug logging to trace analysis execution:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

tracer = DistributedTracer()
tracer.initialize()

# Shows: backend selection, endpoint connection, spans recorded, etc.
```

## Error Handling

```python
from callflow_tracer.ai.distributed_tracer import DistributedTracer, TracerConfig

try:
    config = TracerConfig(backend="unsupported")
    tracer = DistributedTracer(config=config)
except ValueError as e:
    print(f"Invalid configuration: {e}")

try:
    tracer = DistributedTracer()
    tracer.initialize()  # May raise ImportError if library not installed
except ImportError as e:
    print(f"Missing dependency: {e}")

try:
    analysis = tracer.analyze_distributed_trace("invalid-id")
except ValueError as e:
    print(f"Invalid trace ID: {e}")
```

## Custom Backends (Strategy Pattern)

```python
from callflow_tracer.ai.distributed_tracer import (
    TracingBackend, BackendFactory, TracerConfig
)

class CustomBackend(TracingBackend):
    def get_name(self) -> str:
        return "custom"
    
    def initialize(self, config: TracerConfig):
        # Your custom initialization logic
        return custom_tracer_instance

# Register backend
BackendFactory.register("custom", CustomBackend)

# Use it
config = TracerConfig(backend="custom", service_name="my-service")
tracer = DistributedTracer(config=config)
tracer.initialize()
```

## Complete Example

```python
import logging
from callflow_tracer.ai.distributed_tracer import TracerConfig, DistributedTracer

# Setup logging
logging.basicConfig(level=logging.INFO)

# Configure
config = TracerConfig(
    backend="jaeger",
    service_name="order-service",
    endpoint="http://localhost:6831",
    bottleneck_percentile=20,  # Flag top 20% slowest spans
)

# Initialize tracer
tracer = DistributedTracer(config=config)
tracer.initialize()

# Record traces
with tracer.trace_scope("process_order") as context:
    span1 = tracer.record_span("validate_order", duration_ms=10.5)
    span2 = tracer.record_span("check_inventory", duration_ms=50.0)
    span3 = tracer.record_span("charge_payment", duration_ms=100.0)
    span4 = tracer.record_span("send_confirmation", duration_ms=20.0, status="ok")
    
    trace_id = context["trace_id"]

# Analyze
analysis = tracer.analyze_distributed_trace(trace_id)

print(f"Trace ID: {analysis.trace_id}")
print(f"Total Duration: {analysis.total_duration_ms:.2f}ms")
print(f"Services: {analysis.service_count}")
print(f"Spans: {analysis.span_count}")
print(f"Critical Path: {analysis.critical_path_duration_ms:.2f}ms")

if analysis.bottlenecks:
    print("\nBottlenecks:")
    for bn in analysis.bottlenecks:
        print(f"  - {bn['operation']}: {bn['duration_ms']:.2f}ms ({bn['percentage']:.1f}%)")

if analysis.errors:
    print(f"\nErrors: {len(analysis.errors)}")
```

## Performance Tips

1. **Adjust bottleneck threshold** for your use case:
   ```python
   config = TracerConfig(bottleneck_percentile=5)  # Top 5% for stricter detection
   ```

2. **Set sampling rate** for high-volume traces:
   ```python
   config = TracerConfig(sampling_rate=0.1)  # Sample 10% of traces
   ```

3. **Increase timeout** for slow endpoints:
   ```python
   config = TracerConfig(endpoint_timeout_s=15)  # 15 second timeout
   ```

4. **Enable debug logging** to identify slow operations:
   ```python
   logging.getLogger("callflow_tracer.ai.distributed_tracer").setLevel(logging.DEBUG)
   ```

## Architecture

```
DistributedTracer
├── TracerConfig (dataclass - configuration)
├── TracingBackend (ABC - strategy pattern)
│   ├── JaegerBackend (strategy implementation)
│   ├── ZipkinBackend (strategy implementation)
│   └── OpenTelemetryBackend (strategy implementation)
└── BackendFactory (factory pattern - backend creation)

Analysis Methods:
├── _group_spans_by_service() - groups spans by service
├── _identify_bottlenecks() - finds slow operations
├── _compute_critical_path() - calculates longest execution path
└── record_span() - records individual span
```
