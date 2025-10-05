# Flamegraph Examples and Documentation

## What is a Flame Graph?

A **flame graph** is a visualization that shows:
- **Width**: Time spent in each function (wider = more time)
- **Height**: Call stack depth (taller = deeper nesting)
- **Color**: Different functions (for visual distinction)

Flame graphs are excellent for:
- 🔍 **Finding performance bottlenecks** - Wide bars show slow functions
- 📊 **Understanding call hierarchies** - See which functions call which
- ⚡ **Optimizing code** - Identify where to focus optimization efforts
- 🐛 **Debugging complex flows** - Visualize execution paths

## Quick Start

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

### Run the Examples

```bash
cd examples
python flamegraph_example.py
```

This generates 7 different flamegraph HTML files demonstrating various use cases.

## Examples Included

### Example 1: Simple Function Hierarchy
**File**: `flamegraph_1_simple.html`

Demonstrates basic function call relationships:
```python
def process_step_1():
    # Do work
    pass

def process_step_2():
    # Do work
    pass

def main_process():
    process_step_1()
    process_step_2()
```

**What to look for**: Sequential function calls shown side by side.

---

### Example 2: Recursive Functions
**File**: `flamegraph_2_recursive.html`

Shows recursive call patterns:
```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

**What to look for**: Branching tree structure showing recursive calls.

---

### Example 3: Deeply Nested Calls
**File**: `flamegraph_3_nested.html`

Demonstrates call stack depth:
```python
def level_1():
    return level_2()

def level_2():
    return level_3()

def level_3():
    return level_4()
```

**What to look for**: Tall stack showing deep nesting.

---

### Example 4: Parallel Branches
**File**: `flamegraph_4_parallel.html`

Shows multiple execution paths:
```python
def main():
    branch_a()  # Does A1, A2
    branch_b()  # Does B1, B2
    branch_c()  # Does C
```

**What to look for**: Multiple branches side by side at the same level.

---

### Example 5: Performance Hotspots
**File**: `flamegraph_5_hotspots.html`

Identifies slow functions:
```python
def fast_operation():
    # Quick
    pass

def slow_operation():
    time.sleep(0.1)  # Slow!
    pass
```

**What to look for**: The `slow_operation` bar will be noticeably wider.

---

### Example 6: Real-World Pipeline
**File**: `flamegraph_6_pipeline.html`

Complete data processing pipeline:
```python
def pipeline():
    data = load_data()
    validate_data(data)
    clean_data(data)
    transform_data(data)
    save_results(data)
```

**What to look for**: Sequential pipeline stages with timing information.

---

### Example 7: Complex Algorithms
**File**: `flamegraph_7_algorithms.html`

Sorting and searching algorithms:
```python
def algorithm_demo():
    quicksort(data)
    merge_sort(data)
    binary_search(data, target)
```

**What to look for**: Complex recursive patterns in sorting algorithms.

## How to Read Flame Graphs

### Basic Interpretation

```
┌─────────────────────────────────────┐
│         main() - 100ms              │  ← Root function (widest)
├──────────────┬──────────────────────┤
│  func_a()    │    func_b()          │  ← Called by main
│   40ms       │     60ms             │  ← func_b is slower (wider)
├──────┬───────┼──────┬───────────────┤
│ op1  │  op2  │ op3  │     op4       │  ← Leaf functions
│ 20ms │ 20ms  │ 10ms │     50ms      │  ← op4 is the hotspot!
└──────┴───────┴──────┴───────────────┘
```

### Key Insights

1. **Width = Time**: Wider bars = more time spent
2. **Height = Depth**: Taller stacks = deeper call chains
3. **Hotspots**: Look for wide bars at any level
4. **Patterns**: Repeated patterns indicate loops or recursion

### Interactive Features

- **Click**: Zoom into a specific function
- **Hover**: See detailed timing information
- **Zoom to Fit**: Reset view to show entire graph
- **Reset Zoom**: Return to original view

## Testing

### Run All Tests

```bash
cd tests
python test_flamegraph.py
```

### Tests Included

1. ✓ Basic flamegraph generation
2. ✓ Recursive function handling
3. ✓ Data processing validation
4. ✓ Empty graph handling
5. ✓ Custom dimensions
6. ✓ Complex call hierarchies
7. ✓ Performance timing accuracy
8. ✓ Dictionary input support
9. ✓ Interactive features
10. ✓ Error handling

## Advanced Usage

### Custom Dimensions

```python
generate_flamegraph(
    graph,
    "output.html",
    width=1600,   # Wider for more detail
    height=1000   # Taller for deep stacks
)
```

### From Dictionary

```python
# Get graph as dictionary
with trace_scope() as graph:
    my_function()

graph_dict = graph.to_dict()

# Generate from dict
generate_flamegraph(graph_dict, "output.html")
```

### Temporary File (Auto-Open)

```python
# Don't specify output file
temp_path = generate_flamegraph(graph)
# Opens automatically in browser
print(f"Flamegraph at: {temp_path}")
```

### Integration with Profiling

```python
from callflow_tracer import trace_scope, profile_section

with profile_section("Analysis") as perf_stats:
    with trace_scope() as graph:
        my_function()

# Generate flamegraph
generate_flamegraph(graph, "flamegraph.html")

# Also export call graph with profiling
from callflow_tracer import export_html
export_html(graph, "callgraph.html", profiling_stats=perf_stats.to_dict())
```

## Common Use Cases

### 1. Find Performance Bottlenecks

```python
with trace_scope() as graph:
    slow_application()

generate_flamegraph(graph, "bottlenecks.html")
# Look for the widest bars - those are your bottlenecks!
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
# Before optimization
with trace_scope() as graph_before:
    unoptimized_code()
generate_flamegraph(graph_before, "before.html")

# After optimization
with trace_scope() as graph_after:
    optimized_code()
generate_flamegraph(graph_after, "after.html")

# Compare the two flamegraphs side by side
```

### 4. Debug Recursive Algorithms

```python
with trace_scope() as graph:
    result = recursive_algorithm(input_data)

generate_flamegraph(graph, "recursion.html")
# See the recursive call pattern clearly
```

## Troubleshooting

### Issue: Flamegraph shows "No Data"

**Cause**: No functions were traced.

**Solution**:
```python
# Make sure code runs inside trace_scope
with trace_scope() as graph:
    your_function()  # Must call functions here

generate_flamegraph(graph, "output.html")
```

### Issue: Flamegraph is too narrow

**Cause**: Functions execute too quickly.

**Solution**:
```python
# Use larger input or more iterations
with trace_scope() as graph:
    for _ in range(100):  # More iterations
        your_function()

generate_flamegraph(graph, "output.html", width=1600)  # Wider
```

### Issue: Can't see function names

**Cause**: Too many functions or window too small.

**Solution**:
- Increase width: `width=1800`
- Click on a section to zoom in
- Use module filtering in call graph view

### Issue: Browser doesn't open automatically

**Cause**: Specified an output file.

**Solution**:
```python
# Don't specify output file for auto-open
temp_path = generate_flamegraph(graph)

# Or manually open
import webbrowser
webbrowser.open("output.html")
```

## Performance Tips

### 1. Limit Trace Scope

```python
# Only trace the part you care about
setup_data()  # Not traced

with trace_scope() as graph:
    critical_section()  # Only this is traced

cleanup()  # Not traced
```

### 2. Use Sampling for Long Runs

```python
# For very long-running code, trace a sample
import random

with trace_scope() as graph:
    for i in range(1000):
        if random.random() < 0.1:  # Sample 10%
            process_item(i)
```

### 3. Filter Internal Functions

The tracer automatically filters out internal callflow-tracer functions, but you can add your own filters if needed.

## Comparison: Flamegraph vs Call Graph

| Feature | Flamegraph | Call Graph |
|---------|-----------|------------|
| **Best for** | Finding hotspots | Understanding relationships |
| **Visualization** | Stacked bars | Network diagram |
| **Time emphasis** | Width = time | Color = time |
| **Interactivity** | Zoom, click | Layouts, filters |
| **Use when** | Optimizing performance | Debugging logic |

**Recommendation**: Use both! They complement each other.

```python
with trace_scope() as graph:
    my_application()

# Generate both
generate_flamegraph(graph, "flamegraph.html")
export_html(graph, "callgraph.html")
```

## Additional Resources

- **Main README**: `../README.md`
- **Testing Guide**: `../TESTING_GUIDE.md`
- **Profiling Guide**: `../PROFILING.md`
- **Jupyter Examples**: `JUPYTER_README.md`

## Examples Summary

Run `python flamegraph_example.py` to generate:

| File | Description | Key Feature |
|------|-------------|-------------|
| `flamegraph_1_simple.html` | Basic hierarchy | Sequential calls |
| `flamegraph_2_recursive.html` | Recursive patterns | Branching structure |
| `flamegraph_3_nested.html` | Deep nesting | Call stack depth |
| `flamegraph_4_parallel.html` | Parallel branches | Multiple paths |
| `flamegraph_5_hotspots.html` | Performance analysis | Bottleneck identification |
| `flamegraph_6_pipeline.html` | Data pipeline | Real-world workflow |
| `flamegraph_7_algorithms.html` | Complex algorithms | Recursive sorting |

## Contributing

Found an issue or have a suggestion? Please open an issue on GitHub!

---

**Happy profiling! 🔥📊**
