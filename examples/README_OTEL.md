# OpenTelemetry Export Examples

This directory contains examples demonstrating OpenTelemetry export functionality in CallFlow Tracer.

## Files

### `example_otel_export.py`

Complete working example showing:
- Basic trace capture with custom metrics
- Simple OTel export
- Advanced export with exemplars
- Sampling configuration
- Metrics bridging
- Config file usage
- HTML visualization

**Run the example:**

```bash
python examples/example_otel_export.py
```

**Output:**
- `trace_output.json` - Captured trace data
- `trace_visualization.html` - Interactive visualization
- Console output showing export results

### What the Example Does

1. **Captures trace** with custom metrics on 3 functions
2. **Collects metrics** from MetricsCollector
3. **Exports basic OTel** - Simple export to console
4. **Exports with exemplars** - Links metrics to spans
5. **Exports with metrics bridging** - Automatic metric-to-exemplar linking
6. **Exports with sampling** - Reduces span count
7. **Loads config** - Demonstrates OTelConfig usage
8. **Exports HTML** - Creates interactive visualization

## Prerequisites

```bash
# Install CallFlow Tracer
pip install -e .

# Install OpenTelemetry SDK (optional, for OTel export)
pip install opentelemetry-sdk opentelemetry-exporter-otlp
```

## Running the Example

### Basic Run

```bash
cd examples
python example_otel_export.py
```

### With Environment Variables

```bash
export CALLFLOW_OTEL_SERVICE_NAME=my-service
export CALLFLOW_OTEL_ENVIRONMENT=production
python example_otel_export.py
```

### With Config File

```bash
# Create config file
callflow-tracer otel --init-config

# Run example
python example_otel_export.py
```

## Example Output

```
============================================================
CallFlow Tracer - OpenTelemetry Export Example
============================================================

[1] Capturing trace with custom metrics...
   Fibonacci(5) = 5
   Processed data: [2, 4, 6, 8, 10]
   Fetched user: {'id': 123, 'name': 'User 123'}
   ✓ Trace captured to trace_output.json

[2] Collecting custom metrics...
   ✓ Collected 3 metrics
     - fibonacci: 0.001234
     - process_data: 0.050123
     - fetch_user: 0.050456

[3] Exporting to OpenTelemetry (basic)...
   ✓ Export successful!
     - Spans exported: 5
     - Service: example-service
     - Environment: development

[4] Exporting with exemplars (advanced)...
   ✓ Export with exemplars successful!
     - Spans exported: 5
     - Exemplars linked: 3

[5] Exporting with metrics bridging...
   ✓ Metrics bridging successful!
     - Spans exported: 5
     - Exemplars linked: 3

[6] Exporting with sampling (0.5)...
   ✓ Sampling export successful!
     - Spans exported (sampled): 3

[7] Using OTel configuration...
   ✓ Config loaded!
     - Service name: callflow-tracer
     - Environment: production
     - Exporter type: console

[8] Exporting HTML visualization...
   ✓ HTML visualization exported to trace_visualization.html

============================================================
Example completed!
============================================================
```

## Testing

Run the test suite:

```bash
# Run all OTel tests
python -m pytest tests/test_otel_export.py -v

# Run specific test
python -m pytest tests/test_otel_export.py::TestOTelExport::test_export_basic -v

# Run with coverage
python -m pytest tests/test_otel_export.py --cov=callflow_tracer.opentelemetry_exporter
```

## CLI Usage

After running the example, use the CLI to export:

```bash
# Basic export
callflow-tracer export trace_output.json --format otel --service-name example

# Advanced export
callflow-tracer otel trace_output.json \
  --service-name example \
  --environment production \
  --sampling-rate 0.5

# With config file
callflow-tracer otel trace_output.json --config .callflow_otel.yaml
```

## VS Code Extension

1. Open the example file in VS Code
2. Run "CallFlow: Trace Current File"
3. View visualization with "CallFlow: Show Visualization"
4. Export with "CallFlow: Export to OTel (Advanced)"
5. Select options in prompts

## Next Steps

1. **Explore the code** - Read `example_otel_export.py` to understand the API
2. **Run tests** - Execute `test_otel_export.py` to verify functionality
3. **Create config** - Run `callflow-tracer otel --init-config` to generate `.callflow_otel.yaml`
4. **Read docs** - Check `docs/OTEL_ADVANCED_GUIDE.md` for detailed documentation
5. **Integrate** - Use the API in your own code

## Troubleshooting

### "OpenTelemetry SDK is not installed"

```bash
pip install opentelemetry-sdk opentelemetry-exporter-otlp
```

### Spans not appearing in backend

1. Check exporter endpoint in config
2. Verify backend is running
3. Check console output for errors

### Too many spans

Use sampling:

```python
export_callgraph_to_otel(graph, sampling_rate=0.1)
```

## Documentation

- **Full Guide**: `docs/OTEL_ADVANCED_GUIDE.md`
- **Quick Reference**: `OTEL_QUICK_REFERENCE.md`
- **CLI Guide**: `docs/CLI_GUIDE.md`

## Support

For issues or questions:
1. Check the documentation
2. Review the example code
3. Run the tests
4. Check the troubleshooting section
