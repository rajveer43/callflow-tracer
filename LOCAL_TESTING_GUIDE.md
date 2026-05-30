# Local Testing Guide - VS Code Extension

**Date**: 2026-04-15  
**Status**: ✅ Extension built and ready for testing

---

## ✅ Build Complete

The extension has been successfully built:

```
✓ Dependencies installed (npm install)
✓ TypeScript compiled (npm run compile)  
✓ Packaged as VSIX (npm run package)
```

**Built Extension**: `vscode-extension/callflow-tracer-2.1.0.vsix`  
**Size**: 30.27 KB  
**Files**: 25 total

---

## Quick Start - 2 Methods

### Method 1: Install from VSIX File (Easiest)

#### Step 1: Open VS Code
```bash
# Open VS Code
code
```

#### Step 2: Install Extension from VSIX
1. Click the **Extensions** icon in the sidebar (or `Ctrl+Shift+X`)
2. Click the **"..."** menu (three dots) at the top
3. Select **"Install from VSIX..."**
4. Navigate to: `/Users/rajveerrathod/Work/personal_projects/callflow-tracer/vscode-extension/callflow-tracer-2.1.0.vsix`
5. Click **"Install"**

**Result**: Extension appears in your extensions list with a green checkmark

---

### Method 2: Debug Mode (For Development)

#### Step 1: Open Extension Folder in VS Code
```bash
code /Users/rajveerrathod/Work/personal_projects/callflow-tracer/vscode-extension
```

#### Step 2: Launch in Debug Mode
1. Press **F5** (or `Cmd+Shift+D` on Mac)
2. A new VS Code window opens with the extension loaded
3. You'll see **"[Extension Development Host]"** in the window title

#### Step 3: Test Commands
- Open the **Command Palette** (`Ctrl+Shift+P`)
- Type: `CallFlow: Trace Current File`
- The extension is now active and testing in real-time

---

## Testing Checklist

### ✓ Extension Installation

- [ ] Extension appears in the Extensions sidebar
- [ ] Shows as **"CallFlow Tracer"** by rajveer43
- [ ] Has a green checkmark or "Installed" label
- [ ] No error messages

**Verify**:
```bash
# Check installation
code --list-extensions | grep callflow
# Should output: rajveer43.callflow-tracer
```

---

### ✓ Basic Commands Work

Open VS Code and test each command:

#### Command 1: Trace Current File
1. Create test file `test.py`:
```python
def hello():
    return world()

def world():
    return "Hello, World!"

if __name__ == "__main__":
    print(hello())
```

2. Open the file in VS Code
3. **Command Palette** → `CallFlow: Trace Current File`
4. **Expect**: Trace visualization panel appears

#### Command 2: Show Visualization
1. **Command Palette** → `CallFlow: Show Visualization`
2. **Expect**: Visualization panel appears with the trace data

#### Command 3: Export to JSON
1. **Command Palette** → `CallFlow: Export as JSON`
2. **Expect**: File saved to output directory

---

### ✓ Refactored Module Integration

The extension uses the refactored Python modules. To verify they're working:

#### Step 1: Check Python Path in Settings
1. **File** → **Preferences** → **Settings**
2. Search: `callflowTracer.pythonPath`
3. Default should be `python3`
4. Verify it points to Python 3.8+

#### Step 2: View Extension Output
1. Open **Output** panel (`Ctrl+Shift+U`)
2. Select **"CallFlow Tracer"** from the dropdown
3. Run a trace command
4. **Expect**: You'll see:
   - `✓ Starting trace...`
   - `✓ Using analyzer...` (uses `dependency_analyzer.py`)
   - `✓ Trace complete`

#### Step 3: Enable Debug Logging
1. Open **Output** panel
2. You'll see detailed logs from the refactored modules:
```
INFO:callflow_tracer.ai.dependency_analyzer:Starting dependency analysis
DEBUG:callflow_tracer.ai.dependency_analyzer:Extracted 5 nodes
DEBUG:callflow_tracer.ai.dependency_analyzer:Extracted 3 edges
INFO:callflow_tracer.ai.dependency_analyzer:Found 0 circular dependency cycles
```

---

## Test Cases

### Test Case 1: Simple Trace

**File**: `simple_test.py`
```python
def main():
    result = add(2, 3)
    return result

def add(a, b):
    return a + b

if __name__ == "__main__":
    print(main())
```

**Steps**:
1. Open file in VS Code
2. `Ctrl+Shift+P` → `CallFlow: Trace Current File`
3. Wait for visualization

**Expect**:
- ✓ Trace graph shows 2 nodes
- ✓ Shows dependency: `main` → `add`
- ✓ No errors in output panel

---

### Test Case 2: Circular Dependencies

**File**: `circular_test.py`
```python
def a():
    return b()

def b():
    return c()

def c():
    return a()  # Creates cycle!

if __name__ == "__main__":
    a()
```

**Steps**:
1. Open file
2. Trace it
3. Check the output for circular dependency detection

**Expect**:
- ✓ Analysis detects the cycle
- ✓ Circular dependencies shown in output
- ✓ Graph visualization highlights the cycle

---

### Test Case 3: Tight Coupling

**File**: `coupling_test.py`
```python
def main():
    a()
    b()
    c()
    d()
    e()

def a(): pass
def b(): pass
def c(): pass
def d(): pass
def e(): pass

if __name__ == "__main__":
    main()
```

**Steps**:
1. Open file and trace
2. Check for tight coupling detection

**Expect**:
- ✓ `main()` flagged as high coupling (depends on 5 functions)
- ✓ Shows in analysis results

---

## Troubleshooting

### Issue: Extension Not Showing Up

**Solution**:
```bash
# Make sure it's installed
code --list-extensions | grep callflow

# If missing, reinstall
code --install-extension vscode-extension/callflow-tracer-2.1.0.vsix
```

---

### Issue: Python Not Found

**Solution**:
1. **Settings** → Search `callflowTracer.pythonPath`
2. Set to full path:
```
/usr/local/bin/python3
```

**Verify**:
```bash
which python3
```

---

### Issue: Trace Fails with "File not found"

**Solution**:
1. Make sure you have an active editor with Python file
2. Check **Output** panel for full error
3. Verify file is saved (`Ctrl+S`)

---

### Issue: Visualization Not Showing

**Solution**:
1. Check **Output** panel for errors
2. Try: **Command Palette** → `CallFlow: Clear Trace Data`
3. Then retry: `CallFlow: Trace Current File`

---

### Issue: Commands Not Appearing in Palette

**Solution**:
```bash
# Reload VS Code
Cmd+Shift+P → "Developer: Reload Window"

# Or restart VS Code completely
```

---

## Advanced Testing

### Test with Refactored Modules Directly

```bash
# Test dependency analyzer with new configs
python3 << 'EOF'
import sys
sys.path.insert(0, '/Users/rajveerrathod/Work/personal_projects/callflow-tracer')

from callflow_tracer.ai.dependency_analyzer import analyze_dependencies, AnalyzerConfig

graph = {
    "nodes": [{"module": "app", "name": "main"}, {"module": "lib", "name": "helper"}],
    "edges": [{"from": "app:main", "to": "lib:helper"}]
}

# Test with custom config
config = AnalyzerConfig(high_coupling_threshold=10)
result = analyze_dependencies(graph, config)

print(f"✓ Type: {type(result).__name__}")
print(f"✓ Functions: {result.total_functions}")
print(f"✓ Has dataclass attributes: {hasattr(result, 'circular_dependencies')}")
EOF
```

---

### Test Distributed Tracer (Optional)

```bash
python3 << 'EOF'
import sys
sys.path.insert(0, '/Users/rajveerrathod/Work/personal_projects/callflow-tracer')

from callflow_tracer.ai.distributed_tracer import DistributedTracer, TracerConfig

config = TracerConfig(backend="jaeger", bottleneck_percentile=15)
tracer = DistributedTracer(config=config)

with tracer.trace_scope("test_operation") as ctx:
    tracer.record_span("task1", duration_ms=10.0)
    tracer.record_span("task2", duration_ms=50.0)

analysis = tracer.analyze_distributed_trace(ctx["trace_id"])
print(f"✓ Analysis type: {type(analysis).__name__}")
print(f"✓ Total duration: {analysis.total_duration_ms:.2f}ms")
print(f"✓ Span count: {analysis.span_count}")
EOF
```

---

## Performance Testing

### Test Large Graphs

Create `large_graph_test.py`:
```python
# Test with a large graph (100+ nodes)
import time

def make_large_graph(n=100):
    nodes = [{"module": f"mod_{i}", "name": f"func_{i}"} for i in range(n)]
    edges = [{"from": f"mod_{i}:func_{i}", "to": f"mod_{(i+1)%n}:func_{(i+1)%n}"} for i in range(n)]
    return {"nodes": nodes, "edges": edges}

if __name__ == "__main__":
    graph = make_large_graph(100)
    
    # Time the analysis
    start = time.time()
    
    # The refactored analyzer should handle this quickly
    # due to optimized O(V+E) cycle detection
    
    elapsed = time.time() - start
    print(f"Analyzed 100 nodes in {elapsed*1000:.2f}ms")
```

---

## Extension Features to Test

- [ ] **Trace File** - `CallFlow: Trace Current File`
- [ ] **Trace Selection** - `CallFlow: Trace Selected Function`
- [ ] **Visualization** - `CallFlow: Show Visualization`
- [ ] **3D View** - `CallFlow: Show 3D Visualization` (if enabled)
- [ ] **Export JSON** - `CallFlow: Export as JSON`
- [ ] **Export PNG** - `CallFlow: Export as PNG`
- [ ] **Export OTEL** - `CallFlow: Export to OpenTelemetry`
- [ ] **Analyze Anomalies** - `CallFlow: Analyze Anomalies`
- [ ] **Generate Summary** - `CallFlow: Generate Summary`
- [ ] **Explain Traces** - `CallFlow: Explain Traces`
- [ ] **Run Benchmark** - `CallFlow: Run Benchmark`
- [ ] **Clear Trace** - `CallFlow: Clear Trace Data`

---

## Success Criteria

✅ **Extension works if**:
1. Installs without errors
2. Commands appear in Command Palette
3. Trace completes without errors
4. Visualization displays correctly
5. Output panel shows analysis logs
6. Refactored modules handle graphs correctly

---

## Next Steps

1. **Install extension** (Method 1 or 2 above)
2. **Run test cases** (create test files and trace them)
3. **Check logs** in Output panel
4. **Verify** refactored modules are being used (check imports in logs)
5. **Test advanced features** (export, benchmarks, etc.)

---

## Documentation

- 📖 [Testing Guide](./TESTING_VSCODE_EXTENSION.md)
- 📖 [DependencyAnalyzer Refactoring](./REFACTORING_SUMMARY.md)
- 📖 [DistributedTracer Refactoring](./DISTRIBUTED_TRACER_REFACTORING.md)
- 📖 [Complete Summary](./REFACTORING_COMPLETE_SUMMARY.md)

---

## Support

**If extension doesn't work**:
1. Check **Output** panel (`Ctrl+Shift+U`)
2. Enable debug logging: **Settings** → `callflowTracer.enableDebug` (if available)
3. Check Python version: `python3 --version` (need 3.8+)
4. Verify extension installed: `code --list-extensions | grep callflow`

---

**Build Date**: 2026-04-15  
**Extension Version**: 2.1.0  
**Status**: ✅ Ready for testing
