# OpenTelemetry Export - Complete Index

Quick navigation for all OpenTelemetry export documentation and examples.

---

## 📚 Documentation

### Getting Started
- **[OTEL_QUICK_REFERENCE.md](OTEL_QUICK_REFERENCE.md)** - One-page cheat sheet
- **[OTEL_IMPLEMENTATION_SUMMARY.md](OTEL_IMPLEMENTATION_SUMMARY.md)** - Feature overview & statistics

### Comprehensive Guides
- **[docs/OTEL_ADVANCED_GUIDE.md](docs/OTEL_ADVANCED_GUIDE.md)** - Complete feature guide (400+ lines)
- **[OTEL_TESTING_GUIDE.md](OTEL_TESTING_GUIDE.md)** - Testing workflow & CI/CD

### Examples
- **[examples/README_OTEL.md](examples/README_OTEL.md)** - Example documentation

---

## 🔧 Code Files

### Core Modules
- **`callflow_tracer/opentelemetry_exporter.py`** - OTel export functions
- **`callflow_tracer/otel_config.py`** - Configuration management
- **`callflow_tracer/cli.py`** - CLI integration (modified)
- **`vscode-extension/extension.js`** - VS Code integration (modified)

### Examples
- **`examples/example_otel_export.py`** - Complete working example (350+ lines)

### Tests
- **`tests/test_otel_export.py`** - Unit tests (400+ lines, 40+ tests)
- **`test_otel_integration.py`** - Integration test script (300+ lines)

---

## 🚀 Quick Start

### 1. Run Example
```bash
python examples/example_otel_export.py
```

### 2. Run Tests
```bash
python test_otel_integration.py
```

### 3. Use CLI
```bash
callflow-tracer otel trace.json --service-name my-service
```

### 4. Use Python API
```python
from callflow_tracer.opentelemetry_exporter import export_callgraph_to_otel
result = export_callgraph_to_otel(graph, service_name="my-service")
```

### 5. Use VS Code
Command Palette → "CallFlow: Export to OTel (Advanced)"

---

## 📖 Feature Overview

### Core Features
- ✅ **Exemplars** - Link metrics to spans
- ✅ **Sampling** - Reduce overhead (0.0–1.0)
- ✅ **Resource Attributes** - Attach metadata
- ✅ **Config Files** - YAML/JSON support
- ✅ **Environment Variables** - Override config
- ✅ **Multiple Exporters** - Console, OTLP, Jaeger
- ✅ **Semantic Conventions** - OTel standards
- ✅ **Batch Processing** - Efficient export

### Integration Points
- ✅ **CLI** - `callflow-tracer otel` command
- ✅ **Python API** - Direct function calls
- ✅ **VS Code** - UI commands
- ✅ **Config Files** - `.callflow_otel.yaml`
- ✅ **Environment** - `CALLFLOW_OTEL_*` vars

---

## 📋 CLI Commands

### Generate Config
```bash
callflow-tracer otel --init-config
```

### Basic Export
```bash
callflow-tracer otel trace.json --service-name my-service
```

### Advanced Export
```bash
callflow-tracer otel trace.json \
  --service-name my-service \
  --environment production \
  --sampling-rate 0.5 \
  --include-metrics \
  --metrics-file metrics.json \
  --config .callflow_otel.yaml
```

---

## 🐍 Python API

### Basic Export
```python
from callflow_tracer.opentelemetry_exporter import export_callgraph_to_otel

result = export_callgraph_to_otel(graph, service_name="my-service")
```

### Advanced Export
```python
result = export_callgraph_to_otel(
    graph,
    service_name="my-service",
    sampling_rate=0.5,
    environment="production",
    resource_attributes={"service.version": "1.0.0"}
)
```

### With Metrics
```python
from callflow_tracer.opentelemetry_exporter import export_callgraph_with_metrics

result = export_callgraph_with_metrics(
    graph,
    metrics,
    service_name="my-service"
)
```

### With Exemplars
```python
from callflow_tracer.opentelemetry_exporter import CallFlowExemplar

exemplars = [
    CallFlowExemplar(
        trace_id="trace-123",
        span_id="span-456",
        value=0.234,
        metric_name="process_order"
    )
]

result = export_callgraph_to_otel(
    graph,
    service_name="my-service",
    exemplars=exemplars
)
```

---

## ⚙️ Configuration

### Config File (.callflow_otel.yaml)
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

### Environment Variables
```bash
export CALLFLOW_OTEL_SERVICE_NAME=my-service
export CALLFLOW_OTEL_ENVIRONMENT=production
export CALLFLOW_OTEL_SAMPLING_RATE=0.5
export CALLFLOW_OTEL_EXPORTER_TYPE=otlp_grpc
export CALLFLOW_OTEL_EXPORTER_ENDPOINT=http://localhost:4317
```

---

## 🧪 Testing

### Run Example
```bash
python examples/example_otel_export.py
```

### Run Integration Tests
```bash
python test_otel_integration.py
```

### Run Unit Tests
```bash
pytest tests/test_otel_export.py -v
```

### Test Coverage
- Trace capture
- OTel export
- Exemplars
- Sampling
- Configuration
- Metrics bridging
- CLI integration
- 40+ unit tests

---

## 📊 Sampling Rates

| Rate | Behavior | Use Case |
|------|----------|----------|
| `1.0` | Export all | Development |
| `0.5` | ≥2 calls | Staging |
| `0.1` | ≥10 calls | Production |
| `0.01` | ≥100 calls | High-volume |

---

## 🔌 Supported Exporters

| Type | Endpoint | Use Case |
|------|----------|----------|
| `console` | N/A | Local debugging |
| `otlp_grpc` | `http://localhost:4317` | Production (gRPC) |
| `otlp_http` | `http://localhost:4318` | Production (HTTP) |
| `jaeger` | `http://localhost:6831` | Jaeger backend |

---

## 📈 Statistics

| Metric | Value |
|--------|-------|
| Files created | 9 |
| Files modified | 3 |
| Lines of code | 2,500+ |
| Lines of docs | 1,500+ |
| Unit tests | 40+ |
| CLI commands | 1 |
| VS Code commands | 2 |
| Exporters | 4 |
| Config options | 15+ |

---

## 🔍 Troubleshooting

### "OpenTelemetry SDK is not installed"
```bash
pip install opentelemetry-sdk opentelemetry-exporter-otlp
```

### Spans not appearing
1. Check exporter endpoint
2. Verify backend running
3. Check config file

### Too many spans
```bash
callflow-tracer otel trace.json --sampling-rate 0.1
```

See **[OTEL_TESTING_GUIDE.md](OTEL_TESTING_GUIDE.md)** for more troubleshooting.

---

## 📚 Documentation Map

```
OpenTelemetry Export
├── Quick Start
│   ├── OTEL_QUICK_REFERENCE.md
│   └── examples/README_OTEL.md
├── Comprehensive Guides
│   ├── docs/OTEL_ADVANCED_GUIDE.md
│   └── OTEL_TESTING_GUIDE.md
├── Implementation
│   ├── OTEL_IMPLEMENTATION_SUMMARY.md
│   └── OTEL_INDEX.md (this file)
├── Examples
│   └── examples/example_otel_export.py
├── Tests
│   ├── tests/test_otel_export.py
│   └── test_otel_integration.py
└── Code
    ├── callflow_tracer/opentelemetry_exporter.py
    ├── callflow_tracer/otel_config.py
    ├── callflow_tracer/cli.py (modified)
    └── vscode-extension/extension.js (modified)
```

---

## 🎯 Next Steps

1. **Read** - Start with [OTEL_QUICK_REFERENCE.md](OTEL_QUICK_REFERENCE.md)
2. **Run** - Execute `python examples/example_otel_export.py`
3. **Test** - Run `python test_otel_integration.py`
4. **Learn** - Read [docs/OTEL_ADVANCED_GUIDE.md](docs/OTEL_ADVANCED_GUIDE.md)
5. **Integrate** - Use in your code

---

## 📞 Support

For help:
1. Check relevant documentation
2. Review examples
3. Run tests
4. Check troubleshooting sections

---

## ✅ Checklist

- [ ] Read OTEL_QUICK_REFERENCE.md
- [ ] Run example_otel_export.py
- [ ] Run test_otel_integration.py
- [ ] Review OTEL_ADVANCED_GUIDE.md
- [ ] Try CLI commands
- [ ] Try Python API
- [ ] Try VS Code extension
- [ ] Create config file
- [ ] Test with your code

---

## 📝 Version

- **Version**: 0.3.2+
- **Status**: Production Ready
- **Last Updated**: 2025

---

**Happy tracing! 🚀**
