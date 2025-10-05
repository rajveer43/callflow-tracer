# Flamegraph Implementation Summary

## 🎉 Complete Flamegraph Testing Suite Created!

### Files Created

#### 1. **Examples**
- **`examples/flamegraph_example.py`** (580 lines)
  - 7 comprehensive examples demonstrating different use cases
  - Generates 7 interactive HTML flamegraphs
  - Run with: `python examples/flamegraph_example.py`

#### 2. **Tests**
- **`tests/test_flamegraph.py`** (450 lines)
  - 10 comprehensive automated tests
  - Validates all flamegraph functionality
  - Run with: `python tests/test_flamegraph.py`

#### 3. **Documentation**
- **`examples/FLAMEGRAPH_README.md`** (Complete guide)
  - How to use flamegraphs
  - How to read flamegraphs
  - Troubleshooting guide
  - Advanced usage examples

#### 4. **Updated Documentation**
- **`TESTING_GUIDE.md`** - Added flamegraph testing section
- **`QUICK_TEST.md`** - Added flamegraph quick tests

---

## 📊 What is a Flamegraph?

A **flamegraph** is a visualization technique that shows:

```
┌─────────────────────────────────────┐
│         main() - 100ms              │  ← Widest = most time
├──────────────┬──────────────────────┤
│  func_a()    │    func_b()          │  ← func_b is slower
│   40ms       │     60ms             │
├──────┬───────┼──────┬───────────────┤
│ op1  │  op2  │ op3  │     op4       │  ← op4 is the hotspot!
│ 20ms │ 20ms  │ 10ms │     50ms      │
└──────┴───────┴──────┴───────────────┘
```

- **Width** = Time spent (wider = slower)
- **Height** = Call stack depth (taller = deeper nesting)
- **Interactive** = Click to zoom, hover for details

---

## 🚀 Quick Start

### Basic Usage

```python
from callflow_tracer import trace_scope
from callflow_tracer.flamegraph import generate_flamegraph

# Trace your code
with trace_scope() as graph:
    my_function()

# Generate flamegraph
generate_flamegraph(graph, "output.html")
```

### Run Examples

```bash
# Generate 7 flamegraph examples
cd examples
python flamegraph_example.py

# Run 10 automated tests
cd tests
python test_flamegraph.py
```

---

## 📁 Examples Included

### Example 1: Simple Function Hierarchy
**File**: `flamegraph_1_simple.html`

Shows basic sequential function calls:
```python
def main_process():
    process_step_1()
    process_step_2()
    process_step_3()
```

### Example 2: Recursive Functions
**File**: `flamegraph_2_recursive.html`

Visualizes recursive call patterns:
```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

### Example 3: Deeply Nested Calls
**File**: `flamegraph_3_nested.html`

Shows call stack depth:
```python
def level_1():
    return level_2()
        return level_3()
            return level_4()
```

### Example 4: Parallel Branches
**File**: `flamegraph_4_parallel.html`

Multiple execution paths:
```python
def parallel_main():
    branch_a()  # A1, A2
    branch_b()  # B1, B2
    branch_c()  # C
```

### Example 5: Performance Hotspots
**File**: `flamegraph_5_hotspots.html`

Identifies slow functions (wider bars):
```python
def analyze_data():
    fast_operation()   # Narrow bar
    medium_operation() # Medium bar
    slow_operation()   # Wide bar (hotspot!)
```

### Example 6: Real-World Pipeline
**File**: `flamegraph_6_pipeline.html`

Complete data processing workflow:
```python
def data_pipeline():
    load_data()
    validate_data()
    clean_data()
    transform_data()
    save_results()
```

### Example 7: Complex Algorithms
**File**: `flamegraph_7_algorithms.html`

Sorting and searching algorithms:
```python
def algorithm_demo():
    quicksort(data)
    merge_sort(data)
    binary_search(data, target)
```

---

## ✅ Tests Included

### Test 1: Basic Generation
- Creates simple flamegraph
- Verifies HTML structure
- Checks D3.js integration

### Test 2: Recursive Functions
- Tests fibonacci(8)
- Verifies recursive patterns
- Checks file size

### Test 3: Data Processing
- Validates flame data structure
- Checks root nodes
- Verifies children hierarchy

### Test 4: Empty Graph Handling
- Tests with no data
- Verifies graceful fallback
- Checks error handling

### Test 5: Custom Dimensions
- Tests 800x400, 1600x1000, 1200x600
- Verifies dimensions in HTML
- Checks responsiveness

### Test 6: Complex Hierarchy
- Multi-level call trees
- Branch and leaf nodes
- Total node counting

### Test 7: Performance Timing
- Verifies timing accuracy
- Tests slow vs fast functions
- Checks timing data in HTML

### Test 8: Dictionary Input
- Tests dict instead of CallGraph
- Verifies compatibility
- Checks output equivalence

### Test 9: Interactive Features
- Zoom to fit button
- Reset zoom button
- Tooltip functionality
- D3.js selection

### Test 10: Error Handling
- None input
- Invalid data structures
- Missing fields
- Partial data

---

## 🎯 Key Features

### ✨ Visualization
- **Stacked bar chart** showing call hierarchy
- **Color-coded** functions for distinction
- **Proportional width** based on execution time
- **Vertical stacking** showing call depth

### 🖱️ Interactivity
- **Click to zoom** into specific functions
- **Hover tooltips** with detailed timing
- **Zoom to fit** button for overview
- **Reset zoom** to return to original view

### 📊 Data Display
- **Total time** spent in each function
- **Average time** per call
- **Call count** for each function
- **Hierarchical structure** of calls

### 🔧 Customization
- **Custom dimensions** (width, height)
- **Dictionary or CallGraph** input
- **Automatic browser opening** (optional)
- **Temporary or permanent** files

---

## 📖 How to Read Flamegraphs

### Width = Time
- **Wider bars** = More time spent
- **Narrower bars** = Less time spent
- **Look for wide bars** = Performance bottlenecks

### Height = Depth
- **Taller stacks** = Deeper call chains
- **Shorter stacks** = Shallow calls
- **Multiple levels** = Nested functions

### Patterns
- **Repeated patterns** = Loops or recursion
- **Branching** = Multiple code paths
- **Flat sections** = Sequential calls

### Colors
- **Different colors** = Different functions
- **Same color** = Same function (different calls)
- **Visual distinction** only (not performance)

---

## 🔍 Common Use Cases

### 1. Find Performance Bottlenecks
```python
with trace_scope() as graph:
    slow_application()

generate_flamegraph(graph, "bottlenecks.html")
# Look for the widest bars!
```

### 2. Understand Complex Code
```python
with trace_scope() as graph:
    complex_legacy_function()

generate_flamegraph(graph, "understanding.html")
# See the entire call flow visually
```

### 3. Compare Before/After Optimization
```python
# Before
with trace_scope() as before:
    unoptimized_code()
generate_flamegraph(before, "before.html")

# After
with trace_scope() as after:
    optimized_code()
generate_flamegraph(after, "after.html")

# Compare side by side
```

### 4. Debug Recursive Algorithms
```python
with trace_scope() as graph:
    recursive_algorithm(data)

generate_flamegraph(graph, "recursion.html")
# See the recursive call pattern clearly
```

---

## 🧪 Testing Results

### Expected Output

```bash
$ python tests/test_flamegraph.py

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

[... 9 more tests ...]

============================================================
RESULTS: 10 passed, 0 failed
============================================================

✓ ALL TESTS PASSED!

Generated test files:
  - test_flamegraph_basic.html
  - test_flamegraph_recursive.html
  - test_flamegraph_complex.html
  - And more...

📊 Open any HTML file in your browser to see the flamegraphs!
```

---

## 📚 Documentation Structure

```
callflow-tracer/
├── examples/
│   ├── flamegraph_example.py          # 7 comprehensive examples
│   ├── FLAMEGRAPH_README.md           # Complete guide
│   └── flamegraph_*.html              # Generated examples
├── tests/
│   ├── test_flamegraph.py             # 10 automated tests
│   └── test_flamegraph_*.html         # Generated tests
├── TESTING_GUIDE.md                   # Updated with flamegraph section
├── QUICK_TEST.md                      # Updated with flamegraph tests
└── FLAMEGRAPH_SUMMARY.md              # This file
```

---

## 🎓 Learning Path

### Beginner
1. Run `python examples/flamegraph_example.py`
2. Open `flamegraph_1_simple.html` in browser
3. Click around, hover, zoom
4. Read `FLAMEGRAPH_README.md`

### Intermediate
1. Run `python tests/test_flamegraph.py`
2. Examine test code
3. Try custom dimensions
4. Create your own flamegraphs

### Advanced
1. Integrate with profiling
2. Compare optimizations
3. Analyze complex algorithms
4. Customize visualizations

---

## 🔗 Related Features

### Call Graph vs Flamegraph

| Feature | Call Graph | Flamegraph |
|---------|-----------|------------|
| **Visualization** | Network diagram | Stacked bars |
| **Best for** | Understanding relationships | Finding bottlenecks |
| **Time display** | Color-coded | Bar width |
| **Interactivity** | Layouts, filters | Zoom, tooltips |
| **Use when** | Debugging logic | Optimizing performance |

**Recommendation**: Use both together!

```python
with trace_scope() as graph:
    my_application()

# Generate both
generate_flamegraph(graph, "flamegraph.html")
export_html(graph, "callgraph.html")
```

---

## 🚨 Troubleshooting

### Issue: "No Data" in Flamegraph
**Solution**: Ensure code runs inside `trace_scope`

### Issue: Bars too narrow
**Solution**: Increase width or run more iterations

### Issue: D3.js not loading
**Solution**: Check internet connection (CDN required)

### Issue: Flamegraph doesn't match expectations
**Solution**: Verify graph data with `graph.to_dict()`

---

## ✨ Summary

### What Was Created
- ✅ 7 comprehensive examples
- ✅ 10 automated tests
- ✅ Complete documentation
- ✅ Updated testing guides
- ✅ Quick reference cards

### What Works
- ✅ Basic flamegraph generation
- ✅ Recursive function visualization
- ✅ Performance hotspot identification
- ✅ Interactive zoom and tooltips
- ✅ Custom dimensions
- ✅ Dictionary input support
- ✅ Error handling
- ✅ Empty graph handling

### How to Use
1. **Run examples**: `python examples/flamegraph_example.py`
2. **Run tests**: `python tests/test_flamegraph.py`
3. **Read docs**: `examples/FLAMEGRAPH_README.md`
4. **Open HTML files**: View in browser
5. **Create your own**: Follow the examples

---

## 🎉 Success!

All flamegraph functionality is now:
- ✅ **Implemented** - Complete feature set
- ✅ **Tested** - 10 comprehensive tests
- ✅ **Documented** - Full guides and examples
- ✅ **Demonstrated** - 7 working examples
- ✅ **Ready to use** - Just run the examples!

**Happy profiling with flamegraphs! 🔥📊**
