# Testing Guide for Callflow-Tracer

This guide covers how to test all features of the callflow-tracer package, including the recent cProfile fix and Jupyter integration.

## Table of Contents
1. [cProfile Fix Testing](#cprofile-fix-testing)
2. [Jupyter Integration Testing](#jupyter-integration-testing)
3. [Flamegraph Testing](#flamegraph-testing)
4. [Running All Tests](#running-all-tests)
5. [Manual Testing](#manual-testing)

---

## cProfile Fix Testing

### The Problem That Was Fixed

**Issue**: The CPU Profile Analysis dashboard always showed:
- 0.000s execution time
- 0 function calls  
- 0 hot spots

**Root Cause**: The profiler reference was being stored but not the actual profiling data snapshot.

**Solution**: Modified `profiling.py` to create a `pstats.Stats` snapshot when profiling ends.

### Test the Fix

#### Option 1: Run the Automated Test

```bash
cd tests
python test_cprofile_fix.py
```

**Expected Output**:
```
=== Testing cProfile Data Collection ===

Test 1: Using profile_section context manager
Fibonacci(15) = 610
Process data result = 166833.50
I/O operation = completed

--- Verifying Stats Collection ---
Memory stats present: True
CPU stats present: True
I/O wait time: 0.0523s

CPU Profile Data Length: 1234 characters
✓ Found function call summary: 125 function calls in 0.052 seconds

Test 2: Exporting to HTML with profiling stats
✓ HTML exported to: test_cprofile_output.html

--- HTML Content Verification ---
✓ CPU Profile section present
✓ Execution time metric present
✓ Function calls metric present
✓ Performance distribution present
✓ I/O wait time in stats

==================================================
✓ ALL TESTS PASSED!
cProfile data is being correctly captured and exported.
==================================================
```

#### Option 2: Manual Verification

Run the profiling example:

```bash
cd examples
python profiling_example.py
```

Then open the generated `callgraph.html` file and check:
1. Click on "🔥 CPU Profile Analysis (cProfile)" section
2. Verify you see:
   - Total Execution Time > 0.000s
   - Function Calls > 0
   - Performance Distribution > 0 Hot Spots
3. Scroll down to see detailed cProfile output

### Key Changes Made

**File**: `callflow_tracer/profiling.py`

1. **Added `cpu_profile_stats` field** to `PerformanceStats` class:
```python
self.cpu_profile_stats = None  # Store pstats.Stats object
```

2. **Updated `_get_cpu_stats()` method** to use the snapshot:
```python
def _get_cpu_stats(self) -> Dict[str, Any]:
    if not self.cpu_profile_stats:
        return {}
    
    s = io.StringIO()
    self.cpu_profile_stats.stream = s
    self.cpu_profile_stats.print_stats()
    
    return {'profile_data': s.getvalue()}
```

3. **Create snapshot in `profile_function` and `profile_section`**:
```python
if _global_profiler:
    stats.cpu_profile = _global_profiler
    # Create a pstats.Stats object from the profiler
    stats.cpu_profile_stats = pstats.Stats(_global_profiler)
```

---

## Jupyter Integration Testing

### Available Test Files

1. **`tests/test_jupyter_integration.py`** - Comprehensive automated tests
2. **`examples/jupyter_example.ipynb`** - Interactive Jupyter notebook
3. **`examples/jupyter_standalone_demo.py`** - Standalone demo script
4. **`examples/JUPYTER_README.md`** - Complete documentation

### Test Method 1: Automated Tests

```bash
cd tests
python test_jupyter_integration.py
```

**Tests Included**:
1. ✓ Basic function tracing
2. ✓ Recursive function tracing  
3. ✓ Performance profiling
4. ✓ Combined tracing and profiling
5. ✓ HTML export with profiling data
6. ✓ Graph data structure validation
7. ✓ Complex ML pipeline workflow

**Expected Output**:
```
============================================================
JUPYTER INTEGRATION TESTS
============================================================

Test 1: Basic Function Tracing
--------------------------------------------------
Result: {'average': 5.5, 'total': 55}
✓ Captured 3 nodes and 2 edges

Test 2: Recursive Function Tracing
--------------------------------------------------
Fibonacci(8) = 21
Factorial(5) = 120
✓ Captured 15 function calls

[... more tests ...]

============================================================
RESULTS: 7 passed, 0 failed
============================================================

✓ ALL TESTS PASSED!

You can now use the Jupyter notebook examples:
  - examples/jupyter_example.ipynb
```

### Test Method 2: Standalone Demo

```bash
cd examples
python jupyter_standalone_demo.py
```

This generates 5 interactive HTML files:
- `demo1_basic_tracing.html`
- `demo2_recursive_functions.html`
- `demo4_combined_analysis.html`
- `demo5_ml_pipeline.html`
- `demo6_nested_calls.html`

Open any HTML file in your browser to verify:
- ✓ Interactive call graph renders
- ✓ CPU Profile section shows data
- ✓ Layout controls work
- ✓ Module filter works
- ✓ Export buttons work

### Test Method 3: Jupyter Notebook

1. **Install Jupyter** (if needed):
```bash
pip install jupyter
```

2. **Start Jupyter**:
```bash
jupyter notebook
```

3. **Open the notebook**:
   - Navigate to `examples/jupyter_example.ipynb`
   - Run all cells (Cell → Run All)

4. **Verify**:
   - Each cell should execute without errors
   - Interactive visualizations should appear inline
   - CPU profiling data should show in outputs

### Jupyter Features to Test

#### Feature 1: Basic Tracing
```python
from callflow_tracer import trace_scope
from callflow_tracer.jupyter import display_callgraph

with trace_scope() as graph:
    my_function()

display_callgraph(graph.to_dict())
```

#### Feature 2: Performance Profiling
```python
from callflow_tracer import profile_section

with profile_section("My Code") as stats:
    expensive_function()

print(stats.to_dict())
```

#### Feature 3: Combined Analysis
```python
with profile_section("Analysis") as perf_stats:
    with trace_scope() as graph:
        my_pipeline()

export_html(graph, "output.html", profiling_stats=perf_stats.to_dict())
```

#### Feature 4: Magic Commands
```python
%%callflow_cell_trace

def my_function():
    return 42

my_function()
```

---

## Flamegraph Testing

### What is Flamegraph Testing?

Flamegraphs visualize call hierarchies and performance bottlenecks using stacked bar charts where:
- **Width** = Time spent in function
- **Height** = Call stack depth
- **Interaction** = Click to zoom, hover for details

### Test Method 1: Automated Tests

```bash
cd tests
python test_flamegraph.py
```

**Tests Included**:
1. ✓ Basic flamegraph generation
2. ✓ Recursive function handling
3. ✓ Data processing validation
4. ✓ Empty graph handling
5. ✓ Custom dimensions (800x400, 1600x1000, 1200x600)
6. ✓ Complex call hierarchies
7. ✓ Performance timing accuracy
8. ✓ Dictionary input support
9. ✓ Interactive features (zoom, tooltips)
10. ✓ Error handling and edge cases

**Expected Output**:
```
============================================================
FLAMEGRAPH TESTS
Comprehensive Test Suite
============================================================

Test 1: Basic Flamegraph Generation
------------------------------------------------------------
Result: 30
Captured 3 nodes, 2 edges
  ✓ Title present
  ✓ D3 flamegraph library included
  ✓ Function names in data
  ✓ JavaScript present
  ✓ Flamegraph initialization
✓ Test passed

[... more tests ...]

============================================================
RESULTS: 10 passed, 0 failed
============================================================

✓ ALL TESTS PASSED!
```

### Test Method 2: Example Demonstrations

```bash
cd examples
python flamegraph_example.py
```

This generates 7 different flamegraph HTML files:

1. **`flamegraph_1_simple.html`** - Simple function hierarchy
2. **`flamegraph_2_recursive.html`** - Recursive function patterns
3. **`flamegraph_3_nested.html`** - Deeply nested calls
4. **`flamegraph_4_parallel.html`** - Parallel execution branches
5. **`flamegraph_5_hotspots.html`** - Performance bottleneck identification
6. **`flamegraph_6_pipeline.html`** - Real-world data pipeline
7. **`flamegraph_7_algorithms.html`** - Complex sorting algorithms

**Verification Steps**:
1. Open any generated HTML file in your browser
2. Verify the flamegraph renders correctly
3. Test interactive features:
   - Click on bars to zoom in
   - Hover to see timing details
   - Use "Zoom to Fit" and "Reset Zoom" buttons
4. Check that wider bars correspond to slower functions

### Flamegraph Features to Test

#### Feature 1: Basic Generation

```python
from callflow_tracer import trace_scope
from callflow_tracer.flamegraph import generate_flamegraph

with trace_scope() as graph:
    my_function()

generate_flamegraph(graph, "output.html")
```

**Verify**:
- HTML file is created
- Opens in browser
- Shows function call hierarchy
- Interactive zoom works

#### Feature 2: Custom Dimensions

```python
generate_flamegraph(
    graph,
    "output.html",
    width=1600,   # Custom width
    height=1000   # Custom height
)
```

**Verify**:
- Flamegraph uses specified dimensions
- Responsive to window size
- Readable at different sizes

#### Feature 3: Recursive Functions

```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

with trace_scope() as graph:
    fibonacci(10)

generate_flamegraph(graph, "recursive.html")
```

**Verify**:
- Shows branching recursive pattern
- Multiple levels of recursion visible
- Can zoom into specific branches

#### Feature 4: Performance Hotspots

```python
def slow_function():
    time.sleep(0.1)  # Intentionally slow
    return "slow"

def fast_function():
    return "fast"

with trace_scope() as graph:
    slow_function()
    fast_function()

generate_flamegraph(graph, "hotspots.html")
```

**Verify**:
- `slow_function` bar is noticeably wider
- Timing information is accurate
- Easy to identify bottlenecks visually

#### Feature 5: Dictionary Input

```python
with trace_scope() as graph:
    my_function()

# Convert to dict
graph_dict = graph.to_dict()

# Generate from dict
generate_flamegraph(graph_dict, "from_dict.html")
```

**Verify**:
- Accepts both CallGraph and dict
- Output is identical
- No errors with dict input

### Manual Verification Checklist

Open any generated flamegraph HTML and verify:

- [ ] **Visual Rendering**
  - [ ] Flamegraph displays correctly
  - [ ] Colors are distinct
  - [ ] Text is readable
  - [ ] No visual glitches

- [ ] **Interactive Features**
  - [ ] Click on bar zooms in
  - [ ] Hover shows tooltip with details
  - [ ] "Zoom to Fit" button works
  - [ ] "Reset Zoom" button works
  - [ ] Responsive to window resize

- [ ] **Data Accuracy**
  - [ ] Function names are correct
  - [ ] Timing data is present
  - [ ] Call counts are shown
  - [ ] Hierarchy is accurate

- [ ] **Performance**
  - [ ] Loads quickly
  - [ ] Smooth interactions
  - [ ] No lag when zooming
  - [ ] Handles large graphs

### Troubleshooting Flamegraphs

#### Issue: Flamegraph shows "No Data"

**Solution**:
```python
# Ensure code runs inside trace_scope
with trace_scope() as graph:
    your_function()  # Must execute here

generate_flamegraph(graph, "output.html")
```

#### Issue: Bars are too narrow to read

**Solution**:
```python
# Increase width or run more iterations
generate_flamegraph(graph, "output.html", width=1800)
```

#### Issue: D3.js not loading

**Solution**:
- Check internet connection (CDN required)
- Open browser console for errors
- Verify HTML file is complete

#### Issue: Flamegraph doesn't match expectations

**Solution**:
```python
# Verify graph data
graph_dict = graph.to_dict()
print(f"Nodes: {len(graph_dict['nodes'])}")
print(f"Edges: {len(graph_dict['edges'])}")

# Check timing data
for node in graph_dict['nodes']:
    print(f"{node['name']}: {node['total_time']}s")
```

---

## Running All Tests

### Quick Test Suite

Run all tests at once:

```bash
# From the repository root
cd tests

# Test cProfile fix
python test_cprofile_fix.py

# Test Jupyter integration
python test_jupyter_integration.py

# Test other features
python test_profiling.py
```

### Comprehensive Test

```bash
# Run all Python tests
cd tests
for test in test_*.py; do
    echo "Running $test..."
    python "$test"
    if [ $? -ne 0 ]; then
        echo "FAILED: $test"
        exit 1
    fi
done
echo "All tests passed!"
```

---

## Manual Testing

### Test 1: Basic Profiling

```python
from callflow_tracer import profile_function
import time

@profile_function
def slow_function():
    time.sleep(0.1)
    return sum(range(10000))

result = slow_function()
stats = slow_function.performance_stats

# Verify:
assert stats.io_wait_time > 0, "Should measure I/O wait"
assert stats.cpu_profile_stats is not None, "Should have CPU profile"

cpu_data = stats._get_cpu_stats()
assert len(cpu_data['profile_data']) > 0, "Should have profile data"
print("✓ Basic profiling works!")
```

### Test 2: HTML Export with Profiling

```python
from callflow_tracer import trace_scope, profile_section, export_html

def my_function():
    return sum(range(1000))

with profile_section("Test") as perf_stats:
    with trace_scope() as graph:
        my_function()

export_html(graph, "test_output.html", profiling_stats=perf_stats.to_dict())

# Open test_output.html in browser and verify:
# 1. CPU Profile section is present
# 2. Shows non-zero execution time
# 3. Shows function calls > 0
# 4. Shows hot spots > 0
print("✓ HTML export works!")
```

### Test 3: Jupyter Display

```python
# In a Jupyter notebook cell:
from callflow_tracer import trace_scope
from callflow_tracer.jupyter import display_callgraph

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

with trace_scope() as graph:
    fibonacci(8)

display_callgraph(graph.to_dict(), height="500px", layout="force")

# Verify:
# 1. Interactive graph appears inline
# 2. Layout buttons work
# 3. Hover tooltips show data
# 4. Can zoom and pan
print("✓ Jupyter display works!")
```

---

## Troubleshooting

### Issue: CPU Profile Still Shows 0.000s

**Check**:
1. Are you using the updated `profiling.py`?
2. Is the code actually running (not just being defined)?
3. Is profiling enabled?

**Debug**:
```python
with profile_section("Debug") as stats:
    # Your code here
    pass

print(f"CPU profile stats: {stats.cpu_profile_stats}")
print(f"CPU data: {stats._get_cpu_stats()}")
```

### Issue: Jupyter Visualization Not Showing

**Check**:
1. Internet connection (for CDN resources)
2. Browser console for JavaScript errors
3. Jupyter kernel is running

**Debug**:
```python
# Try a simple test
from callflow_tracer.jupyter import display_callgraph

test_data = {
    'nodes': [{'name': 'test', 'full_name': 'test', 'module': '', 
               'call_count': 1, 'total_time': 0.1, 'avg_time': 0.1}],
    'edges': [],
    'metadata': {'total_nodes': 1, 'total_edges': 0, 'duration': 0.1}
}

display_callgraph(test_data)
```

### Issue: Tests Failing

**Common causes**:
1. Missing dependencies: `pip install numpy`
2. Wrong Python version: Requires Python 3.6+
3. Module not in path: Add to `sys.path`

**Debug**:
```bash
# Check Python version
python --version

# Check dependencies
pip list | grep -E "numpy|IPython"

# Run with verbose output
python -v test_cprofile_fix.py
```

---

## Success Criteria

### cProfile Fix
- ✅ CPU Profile section shows non-zero execution time
- ✅ Function calls count is accurate
- ✅ Hot spots are identified
- ✅ Detailed profile data is displayed
- ✅ Health indicators show correct status

### Jupyter Integration
- ✅ Interactive graphs render in notebooks
- ✅ Layout controls work (hierarchical, force, circular, timeline)
- ✅ Module filtering works
- ✅ Export buttons work (PNG, JSON)
- ✅ Magic commands work (`%%callflow_cell_trace`)
- ✅ Profiling data integrates correctly
- ✅ Standalone demos generate valid HTML

---

## Next Steps

After verifying all tests pass:

1. **Update package version** in `version.py`
2. **Build the package**: `python setup.py sdist bdist_wheel`
3. **Test installation**: `pip install dist/callflow-tracer-*.whl`
4. **Run examples**: Verify examples work with installed package
5. **Update documentation**: Ensure README reflects new features
6. **Publish**: Upload to PyPI if ready

---

## Additional Resources

- **Main README**: `README.md`
- **Profiling Guide**: `PROFILING.md`
- **Jupyter Examples**: `examples/JUPYTER_README.md`
- **API Documentation**: Check docstrings in source files

---

## Contact

If you encounter issues not covered here, please:
1. Check existing GitHub issues
2. Create a new issue with:
   - Python version
   - Package version
   - Full error traceback
   - Minimal reproduction code
