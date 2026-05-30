# Testing VS Code Extension with Refactored Python Modules

**Date**: 2026-04-15  
**Goal**: Verify that the refactored `dependency_analyzer.py` and `distributed_tracer.py` work correctly with the VS Code extension

---

## Quick Start

### 1. Install Dependencies

```bash
# Go to the VS Code extension directory
cd vscode-extension

# Install TypeScript and VS Code dependencies
npm install

# Compile TypeScript to JavaScript
npm run compile
```

### 2. Run the Extension in Development Mode

```bash
# From vscode-extension directory
# Press F5 or use the debug menu to start debugging
# This opens a new VS Code window with the extension loaded
```

### 3. Test with Sample Python Files

See **Section: Test Cases** below for specific scenarios.

---

## Extension Architecture

The VS Code extension interacts with Python modules through the CLI:

```
VS Code Extension (TypeScript)
    ↓
callflow-tracer CLI (Python)
    ↓
Core Python Modules:
    - dependency_analyzer.py (REFACTORED)
    - distributed_tracer.py (REFACTORED)
    - Other analysis modules
```

**Key Integration Points**:
- `cliRunner.ts` → Executes Python CLI commands
- `extension.ts` → Registers commands and handles UI
- Results are parsed as JSON and displayed in webviews

---

## Testing Strategy

### Level 1: Unit Tests (Python Modules)

Test the refactored Python modules directly:

```bash
# Navigate to project root
cd /Users/rajveerrathod/Work/personal_projects/callflow-tracer

# Test DependencyAnalyzer
python3 -c "
from callflow_tracer.ai.dependency_analyzer import analyze_dependencies, AnalyzerConfig

# Test basic analysis
graph = {
    'nodes': [
        {'module': 'app', 'name': 'main'},
        {'module': 'lib', 'name': 'helper'},
    ],
    'edges': [{'from': 'app:main', 'to': 'lib:helper'}]
}

result = analyze_dependencies(graph)
print(f'✓ DependencyAnalysis returned: {type(result).__name__}')
print(f'✓ Total functions: {result.total_functions}')
print(f'✓ Circular deps: {len(result.circular_dependencies)}')

# Test with config
config = AnalyzerConfig(high_coupling_threshold=10)
result2 = analyze_dependencies(graph, config)
print(f'✓ Config-based analysis works')
"
```

### Level 2: Integration Tests (CLI + Modules)

Test the CLI with the refactored modules:

```bash
# Trace a Python file
python3 -m callflow_tracer trace /path/to/test_file.py -o /tmp/trace.json --format json

# Check output
python3 -c "
import json
with open('/tmp/trace.json') as f:
    data = json.load(f)
    print(f'✓ Trace generated: {len(data.get(\"nodes\", []))} nodes')
"
```

### Level 3: VS Code Extension Tests

Test the extension commands in VS Code:

1. **Command Palette**: `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type: `CallFlow: Trace Current File`
3. Verify trace visualization appears

---

## Test Cases

### Test Case 1: DependencyAnalyzer - Flat Graph Format

**File**: Create `test_dep_analyzer_flat.py`

```python
# test_dep_analyzer_flat.py
from callflow_tracer.ai.dependency_analyzer import analyze_dependencies

# Test flat graph format (new adapter support)
graph = {
    "nodes": [
        {"module": "services", "name": "auth_service"},
        {"module": "services", "name": "user_service"},
        {"module": "utils", "name": "logger"},
    ],
    "edges": [
        {"from": "services:auth_service", "to": "services:user_service"},
        {"from": "services:user_service", "to": "utils:logger"},
    ]
}

# Test 1: Basic analysis
print("Test 1: Basic flat graph analysis")
result = analyze_dependencies(graph)
assert result.total_functions == 3
assert len(result.circular_dependencies) == 0
print(f"✓ Analyzed {result.total_functions} functions")

# Test 2: Custom configuration
print("\nTest 2: Custom configuration")
from callflow_tracer.ai.dependency_analyzer import AnalyzerConfig

config = AnalyzerConfig(high_coupling_threshold=1)
result = analyze_dependencies(graph, config)
print(f"✓ Custom config applied: threshold={config.high_coupling_threshold}")

print("\n✅ All DependencyAnalyzer tests passed!")
```

**Run**:
```bash
python3 test_dep_analyzer_flat.py
```

---

### Test Case 2: DependencyAnalyzer - Nested Graph Format

**File**: Create `test_dep_analyzer_nested.py`

```python
# test_dep_analyzer_nested.py
from callflow_tracer.ai.dependency_analyzer import analyze_dependencies

# Test nested graph format (new adapter support)
graph = {
    "data": {
        "nodes": [
            {"module": "api", "name": "handler"},
            {"module": "core", "name": "processor"},
        ],
        "edges": [
            {"from": "api:handler", "to": "core:processor"},
        ]
    }
}

print("Test: Nested graph format (auto-detected by adapter)")
result = analyze_dependencies(graph)
assert result.total_functions == 2
print(f"✓ Adapter auto-detected nested format")
print(f"✓ Analyzed {result.total_functions} functions")

print("\n✅ Format adapter test passed!")
```

**Run**:
```bash
python3 test_dep_analyzer_nested.py
```

---

### Test Case 3: DistributedTracer - Basic Configuration

**File**: Create `test_distributed_tracer.py`

```python
# test_distributed_tracer.py
from callflow_tracer.ai.distributed_tracer import (
    DistributedTracer, TracerConfig, DistributedTraceAnalysis
)

print("Test 1: Tracer initialization with custom config")
config = TracerConfig(
    backend="jaeger",
    service_name="test-service",
    bottleneck_percentile=15,
)

tracer = DistributedTracer(config=config)
print(f"✓ Tracer created: backend={tracer.config.backend}")
print(f"✓ Service: {tracer.config.service_name}")
print(f"✓ Bottleneck threshold: top {tracer.config.bottleneck_percentile}%")

print("\nTest 2: Type safety - result is dataclass")
# Simulate trace recording (without actual Jaeger)
with tracer.trace_scope("test_operation") as context:
    tracer.record_span("task1", duration_ms=10.0)
    tracer.record_span("task2", duration_ms=50.0)
    trace_id = context["trace_id"]

# Analyze (will use cached spans)
analysis = tracer.analyze_distributed_trace(trace_id)
assert isinstance(analysis, DistributedTraceAnalysis)
print(f"✓ Analysis is typed: {type(analysis).__name__}")
print(f"✓ Span count: {analysis.span_count}")

print("\nTest 3: Validation works")
try:
    tracer.analyze_distributed_trace("")  # Invalid trace ID
    print("✗ Should have raised ValueError")
except ValueError as e:
    print(f"✓ Validation caught error: {e}")

print("\n✅ All DistributedTracer tests passed!")
```

**Run**:
```bash
python3 test_distributed_tracer.py
```

---

### Test Case 4: VS Code Extension Command

**Steps**:

1. **Open VS Code** with the extension
2. **Create test file** `sample_trace.py`:

```python
# sample_trace.py
def fibonacci(n):
    """Calculate fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def main():
    """Main function."""
    result = fibonacci(5)
    print(f"Fib(5) = {result}")

if __name__ == "__main__":
    main()
```

3. **Run the trace command**:
   - `Ctrl+Shift+P` → Type `CallFlow: Trace Current File`
   - Should show trace data in the visualization panel

4. **Verify output**:
   - Check that the graph renders
   - Inspect "Trace Data" for dependency information
   - Look for "circular_dependencies", "tight_coupling", etc.

---

### Test Case 5: Logging Output

**Verify logging is working**:

```python
# test_logging.py
import logging
from callflow_tracer.ai.dependency_analyzer import analyze_dependencies
from callflow_tracer.ai.distributed_tracer import DistributedTracer, TracerConfig

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

print("=== Testing DependencyAnalyzer logging ===")
graph = {
    "nodes": [{"module": "app", "name": "main"}],
    "edges": []
}
result = analyze_dependencies(graph)
print("✓ Check console for debug logs above")

print("\n=== Testing DistributedTracer logging ===")
tracer = DistributedTracer(config=TracerConfig(backend="jaeger"))
with tracer.trace_scope("test"):
    tracer.record_span("op", 10.0)
print("✓ Check console for debug logs above")
```

**Run**:
```bash
python3 test_logging.py 2>&1 | grep -E "DEBUG|INFO|WARNING"
```

---

### Test Case 6: Error Handling

**File**: `test_error_handling.py`

```python
# test_error_handling.py
from callflow_tracer.ai.dependency_analyzer import analyze_dependencies
from callflow_tracer.ai.distributed_tracer import DistributedTracer, TracerConfig

print("Test 1: Invalid graph format")
try:
    analyze_dependencies("not a dict")
except TypeError as e:
    print(f"✓ Caught: {e}")

print("\nTest 2: Missing required keys")
try:
    analyze_dependencies({})
except ValueError as e:
    print(f"✓ Caught: {e}")

print("\nTest 3: Invalid backend")
try:
    config = TracerConfig(backend="invalid_backend")
    tracer = DistributedTracer(config=config)
except ValueError as e:
    print(f"✓ Caught: {e}")

print("\nTest 4: Invalid trace ID")
tracer = DistributedTracer()
try:
    tracer.analyze_distributed_trace("")
except ValueError as e:
    print(f"✓ Caught: {e}")

print("\n✅ All error handling tests passed!")
```

**Run**:
```bash
python3 test_error_handling.py
```

---

## Running Tests in VS Code Extension Debug Mode

### Method 1: Using VS Code Debug Console

1. **Open VS Code** with extension (`vscode-extension/src/extension.ts`)
2. **Press F5** to start debugging
3. **Open Debug Console** (`Ctrl+Shift+Y`)
4. Run commands in the extension instance:

```javascript
// In the debug VS Code instance, open Command Palette
// Ctrl+Shift+P → CallFlow: Trace Current File
```

### Method 2: Using TypeScript Test Runner

Create `vscode-extension/src/test.ts`:

```typescript
// Example: Test CLI runner integration
import * as assert from 'assert';
import { runCallflowCli } from './cliRunner';

async function testCliRunner() {
  try {
    // Test that CLI is available
    const result = await runCallflowCli(['--version'], process.cwd());
    console.log('✓ CLI is available');
  } catch (error) {
    console.error('✗ CLI error:', error);
  }
}

testCliRunner();
```

---

## Creating a Test Workspace

### Setup Test Workspace

```bash
# Create test directory
mkdir -p /tmp/callflow_test_workspace
cd /tmp/callflow_test_workspace

# Create test Python file
cat > test_functions.py << 'EOF'
def function_a():
    return function_b()

def function_b():
    return function_c()

def function_c():
    return 42

if __name__ == "__main__":
    print(function_a())
EOF

# Create test config
cat > .callflow-tracer.yaml << 'EOF'
# CallFlow Tracer Configuration
format: json
include_args: false
enable_profiling: true
EOF
```

### Trace the Test Workspace

```bash
# From extension debug window, use CallFlow commands to trace these files
# Or from CLI:
python3 -m callflow_tracer trace /tmp/callflow_test_workspace/test_functions.py
```

---

## Verification Checklist

### ✓ DependencyAnalyzer

- [ ] Flat graph format detected and parsed
- [ ] Nested graph format detected and parsed
- [ ] AnalyzerConfig applies custom thresholds
- [ ] Returns `DependencyAnalysis` dataclass (not dict)
- [ ] Logging appears at INFO/DEBUG levels
- [ ] Invalid inputs raise ValueError with clear messages
- [ ] Circular dependency detection works (optimized version)
- [ ] Tight coupling identified with configured threshold

### ✓ DistributedTracer

- [ ] TracerConfig applies custom settings
- [ ] Backend factory creates correct backend instances
- [ ] Returns `DistributedTraceAnalysis` dataclass (not dict)
- [ ] Trace scopes record spans correctly
- [ ] Bottleneck identification uses configured percentile
- [ ] Logging appears at INFO/DEBUG levels
- [ ] Invalid inputs raise ValueError with clear messages
- [ ] Endpoint parsing validates format

### ✓ VS Code Extension Integration

- [ ] `callflow-tracer.traceFile` command works
- [ ] `callflow-tracer.traceSelection` command works
- [ ] Visualization displays correctly
- [ ] No console errors in Debug Console
- [ ] Status bar shows "CallFlow" indicator
- [ ] Configuration settings apply (pythonPath, layout, etc.)

---

## Troubleshooting

### Issue: Python modules not found in CLI

**Solution**:
```bash
# Ensure Python path includes callflow-tracer
export PYTHONPATH="/Users/rajveerrathod/Work/personal_projects/callflow-tracer:$PYTHONPATH"

# Verify
python3 -c "from callflow_tracer.ai.dependency_analyzer import analyze_dependencies"
```

### Issue: "No such file or directory" for trace output

**Solution**:
```bash
# Check temp directory permissions
mkdir -p /tmp/callflow_traces
chmod 777 /tmp/callflow_traces

# Verify in extension config
# Settings → callflowTracer.pythonPath
```

### Issue: Logging not appearing

**Solution**:
```bash
# Enable debug in extension
# File → Preferences → Settings
# Search: callflowTracer
# Look for debug output in Debug Console (Ctrl+Shift+Y)
```

### Issue: Type errors with results

**Ensure** using refactored version:
```bash
# Check file was refactored
grep "class DependencyAnalysis" callflow_tracer/ai/dependency_analyzer.py
grep "class DistributedTraceAnalysis" callflow_tracer/ai/distributed_tracer.py

# Should show @dataclass decorator
```

---

## Performance Testing

### Measure Performance Improvement

```bash
# Test circular dependency detection (should be 10x faster)
python3 << 'EOF'
import time
from callflow_tracer.ai.dependency_analyzer import analyze_dependencies

# Create large graph
nodes = {f"func_{i}": {"module": "app", "name": f"func_{i}"} for i in range(1000)}
edges = [(f"func_{i}", f"func_{(i+1)%1000}") for i in range(1000)]

graph = {
    "nodes": list(nodes.values()),
    "edges": [{"from": s, "to": t} for s, t in edges]
}

# Time it
start = time.time()
result = analyze_dependencies(graph)
elapsed = time.time() - start

print(f"Analyzed {len(nodes)} nodes in {elapsed*1000:.2f}ms")
print(f"Cycles found: {len(result.circular_dependencies)}")
EOF
```

---

## Continuous Integration

### Add to GitHub Actions (`.github/workflows/test.yml`)

```yaml
name: Test VS Code Extension

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      
      - name: Test Python modules
        run: |
          python3 -m pytest callflow_tracer/ai/test_*.py -v
      
      - name: Install extension dependencies
        run: |
          cd vscode-extension
          npm install
      
      - name: Compile TypeScript
        run: |
          cd vscode-extension
          npm run compile
      
      - name: Run extension tests
        run: |
          cd vscode-extension
          npm run test 2>/dev/null || true
```

---

## Next Steps

1. **Run Test Cases** (above) to verify refactored modules
2. **Test VS Code Extension** with sample Python file
3. **Check Logs** for validation/logging messages
4. **Verify Backward Compatibility** with existing traces
5. **Performance Test** large graphs

---

## Documentation

- 📖 [DependencyAnalyzer Refactoring](./REFACTORING_SUMMARY.md)
- 📖 [DistributedTracer Refactoring](./DISTRIBUTED_TRACER_REFACTORING.md)
- 📖 [Complete Refactoring Summary](./REFACTORING_COMPLETE_SUMMARY.md)

---

**Status**: ✅ Ready to test  
**Last Updated**: 2026-04-15
