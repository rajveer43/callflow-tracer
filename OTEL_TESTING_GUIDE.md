# OpenTelemetry Testing Guide

This guide covers testing the advanced OpenTelemetry export functionality.

---

## Test Files Created

### 1. `examples/example_otel_export.py`

**Purpose**: Complete working example demonstrating all OTel features.

**What it tests**:
- Basic trace capture with custom metrics
- Simple OTel export
- Advanced export with exemplars
- Sampling configuration
- Metrics bridging
- Config file usage
- HTML visualization

**Run it**:
```bash
python examples/example_otel_export.py
```

**Expected output**:
- `trace_output.json` - Captured trace data
- `trace_visualization.html` - Interactive visualization
- Console output showing 8 export scenarios

---

### 2. `tests/test_otel_export.py`

**Purpose**: Unit tests for OTel export functionality.

**Test classes**:
- `TestCallFlowExemplar` - Exemplar creation and serialization
- `TestOTelExport` - Basic and advanced export functions
- `TestOTelConfig` - Configuration management
- `TestOTelIntegration` - Full workflow integration

**Run tests**:
```bash
# All OTel tests
python -m pytest tests/test_otel_export.py -v

# Specific test class
python -m pytest tests/test_otel_export.py::TestOTelExport -v

# Specific test
python -m pytest tests/test_otel_export.py::TestOTelExport::test_export_basic -v

# With coverage
python -m pytest tests/test_otel_export.py --cov=callflow_tracer.opentelemetry_exporter
```

**Test coverage**:
- ✓ Exemplar creation and serialization
- ✓ Basic OTel export
- ✓ Export with environment tags
- ✓ Export with sampling
- ✓ Export with exemplars
- ✓ Export with resource attributes
- ✓ Export with metrics bridging
- ✓ Config loading and merging
- ✓ Environment variable overrides
- ✓ Config file save/load
- ✓ Full integration workflow

---

### 3. `test_otel_integration.py`

**Purpose**: Quick integration test script to verify OTel export works end-to-end.

**What it tests**:
1. Trace capture
2. OTel export
3. Exemplar creation and linking
4. Sampling functionality
5. Configuration management
6. Metrics bridging
7. CLI integration

**Run it**:
```bash
python test_otel_integration.py
```

**Expected output**:
```
======================================================================
  OpenTelemetry Integration Test Suite
======================================================================

Test 1: Trace Capture
  ✓ PASS: Trace capture
         Captured 5 nodes

Test 2: OTel Export
  ✓ PASS: OTel export
         Exported 5 spans

Test 3: Exemplars
  ✓ PASS: Exemplar creation
  ✓ PASS: Exemplar linking
         Linked 1 exemplars

Test 4: Sampling
  ✓ PASS: Sampling
         Sampling rate: 0.5

Test 5: Configuration
  ✓ PASS: Default config
  ✓ PASS: Nested config access
         Exporter type: console
  ✓ PASS: Environment override

Test 6: Metrics Bridging
  ✓ PASS: Metrics bridging
         Linked 1 metrics as exemplars

Test 7: CLI Integration
  ✓ PASS: CLI help

======================================================================
  Test Summary
======================================================================
  ✓ Trace Capture
  ✓ OTel Export
  ✓ Exemplars
  ✓ Sampling
  ✓ Configuration
  ✓ Metrics Bridging
  ✓ CLI Integration

  Total: 7/7 tests passed

  🎉 All tests passed!
```

---

## Testing Workflow

### Step 1: Run the Example

```bash
cd callflow-tracer
python examples/example_otel_export.py
```

This generates:
- `trace_output.json` - Trace data
- `trace_visualization.html` - Visualization

### Step 2: Run Integration Tests

```bash
python test_otel_integration.py
```

This verifies all major features work correctly.

### Step 3: Run Unit Tests

```bash
python -m pytest tests/test_otel_export.py -v
```

This tests individual components in detail.

### Step 4: Test CLI Commands

```bash
# Generate config file
callflow-tracer otel --init-config

# Export with config
callflow-tracer otel trace_output.json --config .callflow_otel.yaml

# Export with sampling
callflow-tracer otel trace_output.json --sampling-rate 0.5

# Export with metrics
callflow-tracer otel trace_output.json --include-metrics --metrics-file metrics.json
```

### Step 5: Test VS Code Extension

1. Open `examples/example_otel_export.py` in VS Code
2. Run "CallFlow: Trace Current File"
3. View visualization with "CallFlow: Show Visualization"
4. Export with "CallFlow: Export to OTel (Advanced)"
5. Select options in prompts

---

## Test Coverage Matrix

| Feature | Example | Unit Test | Integration |
|---------|---------|-----------|-------------|
| Trace Capture | ✓ | ✓ | ✓ |
| Basic Export | ✓ | ✓ | ✓ |
| Exemplars | ✓ | ✓ | ✓ |
| Sampling | ✓ | ✓ | ✓ |
| Resource Attributes | ✓ | ✓ | - |
| Metrics Bridging | ✓ | ✓ | ✓ |
| Config Files | ✓ | ✓ | ✓ |
| Environment Variables | ✓ | ✓ | ✓ |
| CLI Commands | - | - | ✓ |
| VS Code Extension | - | - | - |

---

## Troubleshooting Tests

### "OpenTelemetry SDK is not installed"

```bash
pip install opentelemetry-sdk opentelemetry-exporter-otlp
```

Tests will skip gracefully if SDK is not available.

### Tests fail with import errors

```bash
# Install package in development mode
pip install -e .
```

### pytest not found

```bash
pip install pytest pytest-cov
```

### CLI commands not found

```bash
# Reinstall package
pip install -e .

# Verify installation
callflow-tracer --version
```

---

## Performance Testing

### Memory Usage

```bash
# Monitor memory during export
python -m memory_profiler examples/example_otel_export.py
```

### Execution Time

```bash
# Time the example
time python examples/example_otel_export.py
```

### Span Count Scaling

Test with different sampling rates:

```bash
# Full export (all spans)
callflow-tracer otel trace.json --sampling-rate 1.0

# 50% sampling
callflow-tracer otel trace.json --sampling-rate 0.5

# 10% sampling
callflow-tracer otel trace.json --sampling-rate 0.1

# 1% sampling
callflow-tracer otel trace.json --sampling-rate 0.01
```

---

## Continuous Integration

### GitHub Actions Example

```yaml
name: OTel Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -e .
          pip install pytest pytest-cov
          pip install opentelemetry-sdk opentelemetry-exporter-otlp
      
      - name: Run integration tests
        run: python test_otel_integration.py
      
      - name: Run unit tests
        run: pytest tests/test_otel_export.py -v --cov
      
      - name: Run example
        run: python examples/example_otel_export.py
```

---

## Test Results Checklist

- [ ] Example runs without errors
- [ ] Trace data captured correctly
- [ ] OTel export completes successfully
- [ ] Exemplars linked to spans
- [ ] Sampling reduces span count
- [ ] Config files load correctly
- [ ] Environment variables override config
- [ ] Metrics bridging works
- [ ] CLI commands execute
- [ ] VS Code extension responds
- [ ] HTML visualization generates
- [ ] All unit tests pass
- [ ] All integration tests pass

---

## Next Steps

1. **Run the example** to see OTel export in action
2. **Review the code** to understand the implementation
3. **Run the tests** to verify functionality
4. **Integrate into CI/CD** for automated testing
5. **Monitor in production** with OTel backend

---

## Documentation

- **Full Guide**: `docs/OTEL_ADVANCED_GUIDE.md`
- **Quick Reference**: `OTEL_QUICK_REFERENCE.md`
- **Example README**: `examples/README_OTEL.md`
- **CLI Guide**: `docs/CLI_GUIDE.md`
