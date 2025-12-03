# Advanced OpenTelemetry Integration Guide

CallFlow Tracer v0.3.2+ provides **advanced OpenTelemetry export** with exemplars, sampling, and configuration management. This guide covers all features.

---

## Quick Start

### 1. Basic Export (CLI)

```bash
# Generate a trace
callflow-tracer trace my_script.py --format json -o trace.json

# Export to OTel (simple mode)
callflow-tracer export trace.json --format otel --service-name my-service
```

### 2. Advanced Export (CLI)

```bash
# Export with sampling, exemplars, and config
callflow-tracer otel trace.json \
  --service-name my-service \
  --environment production \
  --sampling-rate 0.5 \
  --include-metrics \
  --metrics-file metrics.json
```

### 3. VS Code Extension

- **Basic**: Command Palette → "CallFlow: Export to OTel"
- **Advanced**: Command Palette → "CallFlow: Export to OTel (Advanced)"

---

## Configuration Files

### Create Example Config

```bash
callflow-tracer otel --init-config
```

This creates `.callflow_otel.yaml`:

```yaml
service_name: callflow-tracer
environment: production
sampling_rate: 1.0
include_metrics: false

exporter:
  type: console  # console, otlp_grpc, otlp_http, jaeger
  endpoint: http://localhost:4317
  headers: {}

resource_attributes:
  service.version: "1.0.0"

batch_processor:
  max_queue_size: 2048
  max_export_batch_size: 512
  schedule_delay_millis: 5000
```

### Load Config File

```bash
# Auto-detect .callflow_otel.yaml
callflow-tracer otel trace.json

# Explicit config path
callflow-tracer otel trace.json --config ./config/otel.yaml
```

### Environment Variables

Override config with env vars:

```bash
export CALLFLOW_OTEL_SERVICE_NAME=my-service
export CALLFLOW_OTEL_ENVIRONMENT=staging
export CALLFLOW_OTEL_SAMPLING_RATE=0.5
export CALLFLOW_OTEL_EXPORTER_TYPE=otlp_grpc
export CALLFLOW_OTEL_EXPORTER_ENDPOINT=http://otel-collector:4317

callflow-tracer otel trace.json
```

---

## Advanced Features

### 1. Exemplars (Linking Metrics to Traces)

Exemplars connect high-value metrics to specific trace spans.

#### From Custom Metrics

```python
from callflow_tracer import trace_scope, custom_metric, MetricsCollector
from callflow_tracer.opentelemetry_exporter import export_callgraph_with_metrics

@custom_metric("process_order", sla_threshold=1.0)
def process_order(order_id):
    # Process order...
    return result

with trace_scope("trace.json"):
    for order_id in [1, 2, 3]:
        process_order(order_id)

# Export with metrics as exemplars
metrics = MetricsCollector.get_metrics()
export_callgraph_with_metrics(
    callgraph,
    metrics,
    service_name="order-service"
)
```

#### CLI with Metrics File

```bash
# Export metrics from custom_metric tracking
python -c "
from callflow_tracer import MetricsCollector
import json
metrics = MetricsCollector.get_metrics()
with open('metrics.json', 'w') as f:
    json.dump(metrics, f)
"

# Link metrics to trace spans
callflow-tracer otel trace.json \
  --include-metrics \
  --metrics-file metrics.json
```

### 2. Sampling

Reduce overhead by sampling low-call-count functions.

```bash
# Sample only functions called >= 10 times (sampling_rate=0.1)
callflow-tracer otel trace.json --sampling-rate 0.1

# Sample only functions called >= 100 times (sampling_rate=0.01)
callflow-tracer otel trace.json --sampling-rate 0.01

# Export all functions (sampling_rate=1.0, default)
callflow-tracer otel trace.json --sampling-rate 1.0
```

### 3. Resource Attributes

Attach metadata to all spans.

**YAML Config:**

```yaml
resource_attributes:
  service.version: "1.2.3"
  deployment.environment: production
  service.namespace: my-org
  service.instance.id: host-1
  host.name: prod-server-01
```

**Python API:**

```python
from callflow_tracer.opentelemetry_exporter import export_callgraph_to_otel

result = export_callgraph_to_otel(
    callgraph,
    service_name="my-service",
    resource_attributes={
        "service.version": "1.2.3",
        "deployment.environment": "production",
        "host.name": "prod-01",
    }
)
```

### 4. Environments

Tag spans with deployment environment.

```bash
# Production
callflow-tracer otel trace.json --environment production

# Staging
callflow-tracer otel trace.json --environment staging

# Development
callflow-tracer otel trace.json --environment development
```

---

## Python API

### Basic Export

```python
from callflow_tracer import trace_scope
from callflow_tracer.opentelemetry_exporter import export_callgraph_to_otel

with trace_scope(None) as graph:
    # Your code here
    pass

# Export to OTel
result = export_callgraph_to_otel(
    graph,
    service_name="my-service",
    environment="production"
)

print(f"Exported {result['span_count']} spans")
```

### Advanced Export with Exemplars

```python
from callflow_tracer.opentelemetry_exporter import (
    export_callgraph_to_otel,
    CallFlowExemplar
)

# Create exemplars linking metrics to spans
exemplars = [
    CallFlowExemplar(
        trace_id="abc123",
        span_id="def456",
        value=0.234,
        metric_name="process_order",
        attributes={"order_id": "12345"}
    ),
]

result = export_callgraph_to_otel(
    graph,
    service_name="order-service",
    exemplars=exemplars,
    sampling_rate=0.5,
    environment="production"
)

print(f"Exemplars linked: {result['exemplar_count']}")
```

### With Custom Metrics

```python
from callflow_tracer.opentelemetry_exporter import export_callgraph_with_metrics
from callflow_tracer import MetricsCollector

metrics = MetricsCollector.get_metrics()

result = export_callgraph_with_metrics(
    graph,
    metrics,
    service_name="my-service",
    resource_attributes={"service.version": "1.0.0"}
)
```

---

## Span Attributes

Each span includes semantic attributes:

| Attribute | Type | Description |
|-----------|------|-------------|
| `code.function` | string | Function name |
| `code.namespace` | string | Module/namespace |
| `code.lineno` | int | Line number |
| `callflow.call_count` | int | Total calls |
| `callflow.total_time` | float | Total execution time (s) |
| `callflow.avg_time` | float | Average execution time (s) |
| `callflow.last_arguments` | string | Last call arguments |

---

## OTel Backends

### Console (Default)

```bash
callflow-tracer otel trace.json
# Prints spans to console
```

### OTLP/gRPC

**Config:**

```yaml
exporter:
  type: otlp_grpc
  endpoint: http://localhost:4317
```

**CLI:**

```bash
export CALLFLOW_OTEL_EXPORTER_TYPE=otlp_grpc
export CALLFLOW_OTEL_EXPORTER_ENDPOINT=http://otel-collector:4317
callflow-tracer otel trace.json
```

### Jaeger

**Config:**

```yaml
exporter:
  type: jaeger
  endpoint: http://localhost:6831
```

### Tempo

**Config:**

```yaml
exporter:
  type: otlp_grpc
  endpoint: http://tempo:4317
```

---

## VS Code Extension

### Settings

Add to `.vscode/settings.json`:

```json
{
  "callflowTracer.otelServiceName": "my-service",
  "callflowTracer.otelEnvironment": "production",
  "callflowTracer.otelSamplingRate": 0.5
}
```

### Commands

1. **Export to OTel (Basic)**
   - Command: `callflow-tracer.exportToOtel`
   - Uses settings for service name
   - Quick one-click export

2. **Export to OTel (Advanced)**
   - Command: `callflow-tracer.exportToOtelAdvanced`
   - Prompts for service name, environment, sampling rate
   - Full control over export options

### Workflow

1. Trace your code: "CallFlow: Trace Current File"
2. View visualization: "CallFlow: Show Visualization"
3. Export to OTel: "CallFlow: Export to OTel (Advanced)"
4. Select options in prompts
5. Spans sent to configured OTel backend

---

## Best Practices

### 1. Use Sampling in Production

```bash
# Reduce overhead: sample 10% of functions
callflow-tracer otel trace.json --sampling-rate 0.1
```

### 2. Link Metrics to Traces

```bash
# Capture business metrics and link to spans
callflow-tracer otel trace.json \
  --include-metrics \
  --metrics-file metrics.json
```

### 3. Environment Tagging

```bash
# Always tag with environment
callflow-tracer otel trace.json \
  --environment production \
  --service-name api-gateway
```

### 4. Config File for Consistency

```bash
# Use .callflow_otel.yaml for team consistency
callflow-tracer otel trace.json --config .callflow_otel.yaml
```

### 5. Batch Processing

Configure batch processor for efficiency:

```yaml
batch_processor:
  max_queue_size: 4096
  max_export_batch_size: 1024
  schedule_delay_millis: 10000  # 10s
```

---

## Troubleshooting

### "OpenTelemetry SDK is not installed"

```bash
pip install opentelemetry-sdk opentelemetry-exporter-otlp
```

### Spans not appearing in backend

1. Check exporter endpoint:
   ```bash
   export CALLFLOW_OTEL_EXPORTER_ENDPOINT=http://your-collector:4317
   ```

2. Verify backend is running:
   ```bash
   curl http://your-collector:4317/v1/traces
   ```

3. Check config file:
   ```bash
   callflow-tracer otel trace.json --config .callflow_otel.yaml
   ```

### Too many spans

Use sampling to reduce:

```bash
callflow-tracer otel trace.json --sampling-rate 0.1
```

### Missing exemplars

Ensure metrics file is provided:

```bash
callflow-tracer otel trace.json \
  --include-metrics \
  --metrics-file metrics.json
```

---

## Examples

### Example 1: FastAPI Service

```python
from fastapi import FastAPI
from callflow_tracer import trace_scope, custom_metric
from callflow_tracer.opentelemetry_exporter import export_callgraph_to_otel

app = FastAPI()

@custom_metric("api_request", sla_threshold=0.5)
@app.get("/items/{item_id}")
async def get_item(item_id: int):
    return {"item_id": item_id}

if __name__ == "__main__":
    with trace_scope(None) as graph:
        # Simulate requests
        pass
    
    export_callgraph_to_otel(
        graph,
        service_name="item-api",
        environment="production"
    )
```

### Example 2: Batch Processing

```bash
# Process multiple traces
for trace in traces/*.json; do
  callflow-tracer otel "$trace" \
    --service-name batch-processor \
    --environment production
done
```

### Example 3: CI/CD Integration

```bash
# In your CI pipeline
callflow-tracer trace my_app.py --format json -o trace.json
callflow-tracer otel trace.json \
  --service-name my-app \
  --environment ci \
  --sampling-rate 0.5
```

---

## API Reference

### `export_callgraph_to_otel()`

```python
def export_callgraph_to_otel(
    callgraph,
    service_name: str = "callflow-tracer",
    resource_attributes: Optional[Dict[str, Any]] = None,
    use_existing_tracer_provider: bool = True,
    exemplars: Optional[List[CallFlowExemplar]] = None,
    sampling_rate: float = 1.0,
    include_metrics: bool = False,
    environment: str = "production",
) -> Dict[str, Any]:
    """Export CallGraph to OTel spans with advanced features."""
```

### `export_callgraph_with_metrics()`

```python
def export_callgraph_with_metrics(
    callgraph,
    metrics_data: Dict[str, Any],
    service_name: str = "callflow-tracer",
    resource_attributes: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Export CallGraph and link custom metrics as exemplars."""
```

### `OTelConfig`

```python
class OTelConfig:
    def __init__(self, config_path: Optional[str] = None)
    def load_from_file(self, path: str) -> None
    def load_from_env(self) -> None
    def get(self, key: str, default: Any = None) -> Any
    def to_dict(self) -> Dict[str, Any]
    def save_to_file(self, path: str, format: str = "yaml") -> None
```

---

## See Also

- [OpenTelemetry Documentation](https://opentelemetry.io/)
- [Custom Metrics Guide](CUSTOM_METRICS_GUIDE.md)
- [CLI Guide](CLI_GUIDE.md)
