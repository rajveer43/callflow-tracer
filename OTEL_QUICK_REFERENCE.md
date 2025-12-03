# OpenTelemetry Export Quick Reference

## Installation

```bash
pip install opentelemetry-sdk opentelemetry-exporter-otlp
```

---

## CLI Quick Start

### Basic Export
```bash
callflow-tracer trace my_script.py --format json -o trace.json
callflow-tracer export trace.json --format otel --service-name my-service
```

### Advanced Export
```bash
callflow-tracer otel trace.json \
  --service-name my-service \
  --environment production \
  --sampling-rate 0.5
```

### With Metrics
```bash
callflow-tracer otel trace.json \
  --include-metrics \
  --metrics-file metrics.json
```

### Generate Config
```bash
callflow-tracer otel --init-config
```

---

## Config File (.callflow_otel.yaml)

```yaml
service_name: my-service
environment: production
sampling_rate: 1.0

exporter:
  type: otlp_grpc
  endpoint: http://localhost:4317

resource_attributes:
  service.version: "1.0.0"
```

---

## Environment Variables

```bash
export CALLFLOW_OTEL_SERVICE_NAME=my-service
export CALLFLOW_OTEL_ENVIRONMENT=production
export CALLFLOW_OTEL_SAMPLING_RATE=0.5
export CALLFLOW_OTEL_EXPORTER_TYPE=otlp_grpc
export CALLFLOW_OTEL_EXPORTER_ENDPOINT=http://localhost:4317
```

---

## Python API

### Basic
```python
from callflow_tracer import trace_scope
from callflow_tracer.opentelemetry_exporter import export_callgraph_to_otel

with trace_scope(None) as graph:
    pass

export_callgraph_to_otel(graph, service_name="my-service")
```

### Advanced
```python
result = export_callgraph_to_otel(
    graph,
    service_name="my-service",
    environment="production",
    sampling_rate=0.5,
    resource_attributes={"service.version": "1.0.0"}
)

print(f"Spans: {result['span_count']}, Exemplars: {result['exemplar_count']}")
```

### With Metrics
```python
from callflow_tracer.opentelemetry_exporter import export_callgraph_with_metrics
from callflow_tracer import MetricsCollector

metrics = MetricsCollector.get_metrics()
export_callgraph_with_metrics(graph, metrics, service_name="my-service")
```

---

## VS Code Commands

| Command | Shortcut |
|---------|----------|
| Export to OTel | Cmd Palette: "CallFlow: Export to OTel" |
| Advanced Export | Cmd Palette: "CallFlow: Export to OTel (Advanced)" |

---

## Sampling Rates

| Rate | Behavior |
|------|----------|
| `1.0` | Export all functions (default) |
| `0.5` | Export functions called ≥2 times |
| `0.1` | Export functions called ≥10 times |
| `0.01` | Export functions called ≥100 times |

---

## Exporter Types

| Type | Endpoint | Use Case |
|------|----------|----------|
| `console` | N/A | Local debugging |
| `otlp_grpc` | `http://localhost:4317` | Production (gRPC) |
| `otlp_http` | `http://localhost:4318` | Production (HTTP) |
| `jaeger` | `http://localhost:6831` | Jaeger backend |

---

## Span Attributes

```
code.function          → Function name
code.namespace         → Module/package
code.lineno            → Line number
callflow.call_count    → Total calls
callflow.total_time    → Total execution time (s)
callflow.avg_time      → Average execution time (s)
callflow.last_arguments → Last call arguments
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "SDK not installed" | `pip install opentelemetry-sdk` |
| Spans not appearing | Check exporter endpoint, verify backend running |
| Too many spans | Use `--sampling-rate 0.1` |
| Missing exemplars | Provide `--metrics-file` with `--include-metrics` |

---

## Examples

### FastAPI Service
```python
from callflow_tracer import trace_scope, custom_metric
from callflow_tracer.opentelemetry_exporter import export_callgraph_to_otel

@custom_metric("api_request", sla_threshold=0.5)
@app.get("/items/{item_id}")
async def get_item(item_id: int):
    return {"item_id": item_id}

with trace_scope(None) as graph:
    pass

export_callgraph_to_otel(graph, service_name="item-api", environment="production")
```

### CI/CD Pipeline
```bash
#!/bin/bash
callflow-tracer trace app.py --format json -o trace.json
callflow-tracer otel trace.json \
  --service-name my-app \
  --environment ci \
  --sampling-rate 0.5
```

### Batch Processing
```bash
for trace in traces/*.json; do
  callflow-tracer otel "$trace" \
    --service-name batch-processor \
    --environment production
done
```

---

## Documentation

- **Full Guide**: `docs/OTEL_ADVANCED_GUIDE.md`
- **CLI Guide**: `docs/CLI_GUIDE.md`
- **Custom Metrics**: `docs/CUSTOM_METRICS_GUIDE.md`
