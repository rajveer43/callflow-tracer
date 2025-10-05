# CallFlow Tracer - User Guide

Complete guide for using CallFlow Tracer effectively.

---

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Tracing](#basic-tracing)
3. [Performance Profiling](#performance-profiling)
4. [Flamegraph Analysis](#flamegraph-analysis)
5. [Call Graph Visualization](#call-graph-visualization)
6. [Jupyter Notebooks](#jupyter-notebooks)
7. [Best Practices](#best-practices)
8. [Common Workflows](#common-workflows)
9. [Tips and Tricks](#tips-and-tricks)
10. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Installation

```bash
pip install callflow-tracer
```

### Your First Trace

```python
from callflow_tracer import trace_scope

def hello_world():
    return "Hello, CallFlow Tracer!"

with trace_scope() as graph:
    result = hello_world()
    print(result)

print(f"Traced {len(graph.nodes)} functions")
```

### Your First Visualization

```python
from callflow_tracer import trace_scope, export_html

def my_function():
    return sum(range(100))

with trace_scope() as graph:
    my_function()

export_html(graph, "my_first_trace.html")
```

Open `my_first_trace.html` in your browser!

---

## Basic Tracing

### Method 1: Context Manager (Recommended)

```python
from callflow_tracer import trace_scope

with trace_scope() as graph:
    # Everything here is traced
    my_function()
    another_function()

# Access graph data
print(f"Nodes: {len(graph.nodes)}")
print(f"Edges: {len(graph.edges)}")
```

**Pros**:
- Clean syntax
- Automatic cleanup
- Easy to scope

### Method 2: Decorator

```python
from callflow_tracer import trace

@trace
def my_function():
    return 42

@trace
def another_function():
    return my_function() + 10

result = another_function()
```

**Pros**:
- Selective tracing
- Reusable
- No indentation

### Method 3: Auto-Export

```python
from callflow_tracer import trace_scope

# Automatically exports to HTML
with trace_scope("output.html"):
    my_application()
```

**Pros**:
- One-liner export
- No separate export call
- Convenient

---

## Performance Profiling

### CPU Profiling

```python
from callflow_tracer import profile_function

@profile_function
def expensive_function():
    return sum(range(1000000))

result = expensive_function()

# Access stats
stats = expensive_function.performance_stats
cpu_stats = stats._get_cpu_stats()
print(cpu_stats['profile_data'])
```

### Memory Profiling

```python
from callflow_tracer import profile_section

with profile_section("Memory Test") as stats:
    # Allocate memory
    big_list = [i for i in range(1000000)]

# Check memory usage
mem_stats = stats._get_memory_stats()
print(f"Current: {mem_stats['current_mb']:.2f}MB")
print(f"Peak: {mem_stats['peak_mb']:.2f}MB")
```

### I/O Wait Time

```python
from callflow_tracer import profile_section
import time

with profile_section("I/O Operations") as stats:
    time.sleep(0.1)  # Simulates I/O
    compute_something()

stats_dict = stats.to_dict()
print(f"I/O wait: {stats_dict['io_wait']:.4f}s")
```

### Combined Profiling

```python
from callflow_tracer import trace_scope, profile_section, export_html

with profile_section("Complete Analysis") as perf_stats:
    with trace_scope() as graph:
        my_application()

# Export with all profiling data
export_html(
    graph,
    "complete_analysis.html",
    profiling_stats=perf_stats.to_dict()
)
```

---

## Flamegraph Analysis

### Basic Flamegraph

```python
from callflow_tracer import trace_scope
from callflow_tracer.flamegraph import generate_flamegraph

with trace_scope() as graph:
    my_application()

generate_flamegraph(graph, "flamegraph.html")
```

### Enhanced Flamegraph (Recommended!)

```python
generate_flamegraph(
    graph,
    "enhanced.html",
    title="My App Performance",
    color_scheme="performance",  # Green=fast, Red=slow
    show_stats=True,             # Show statistics
    search_enabled=True,         # Enable search
    width=1600,
    height=1000
)
```

### Reading Flamegraphs

**Width = Time**:
- Wider bars = more time spent
- Look for wide bars = bottlenecks

**Height = Depth**:
- Taller stacks = deeper nesting
- Each level = one function call

**Colors (Performance Scheme)**:
- 🟢 Green = Fast functions
- 🟡 Yellow = Medium functions
- 🔴 Red = Slow functions (optimize these!)

### Finding Bottlenecks

1. Open flamegraph with `color_scheme="performance"`
2. Look for wide RED bars
3. Check statistics panel for "Slowest Function"
4. Use search to find specific functions
5. Click on bars to zoom in

---

## Call Graph Visualization

### Basic Export

```python
from callflow_tracer import trace_scope, export_html

with trace_scope() as graph:
    my_application()

export_html(graph, "callgraph.html")
```

### With Custom Options

```python
export_html(
    graph,
    "callgraph.html",
    title="My Application Call Graph",
    layout="hierarchical",  # or 'force', 'circular', 'timeline'
    profiling_stats=stats_dict
)
```

### Using Different Layouts

**Hierarchical**: Best for understanding flow
```python
export_html(graph, "hierarchical.html", layout="hierarchical")
```

**Force-Directed**: Best for exploring relationships
```python
export_html(graph, "force.html", layout="force")
```

**Circular**: Best for seeing all functions
```python
export_html(graph, "circular.html", layout="circular")
```

**Timeline**: Best for performance comparison
```python
export_html(graph, "timeline.html", layout="timeline")
```

### Module Filtering

1. Open the HTML file
2. Use "Filter by Module" dropdown
3. Select a module
4. Graph automatically filters and zooms

---

## Jupyter Notebooks

### Setup

```python
# In Jupyter notebook
from callflow_tracer import trace_scope, profile_section
from callflow_tracer.jupyter import display_callgraph, init_jupyter

# Initialize (optional)
init_jupyter()
```

### Inline Visualization

```python
def my_function():
    return sum(range(1000))

with trace_scope() as graph:
    result = my_function()

# Display inline
display_callgraph(
    graph.to_dict(),
    width="100%",
    height="600px",
    layout="force"
)
```

### Magic Commands

**Line Magic**:
```python
%callflow_trace my_function()
```

**Cell Magic**:
```python
%%callflow_cell_trace

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

result = fibonacci(10)
print(result)
```

### With Profiling

```python
with profile_section("Analysis") as stats:
    with trace_scope() as graph:
        ml_pipeline()

# Display graph
display_callgraph(graph.to_dict())

# Show stats
print(stats.to_dict())
```

---

## Best Practices

### 1. Use Context Managers

```python
# Good
with trace_scope() as graph:
    my_function()

# Avoid
graph = trace_scope()  # Without context manager
```

### 2. Combine Tracing and Profiling

```python
with profile_section("Analysis") as stats:
    with trace_scope() as graph:
        my_function()

# Get both call graph and profiling data
```

### 3. Use Performance Color Scheme

```python
generate_flamegraph(
    graph,
    "output.html",
    color_scheme="performance"  # Best for finding bottlenecks
)
```

### 4. Enable All Features

```python
generate_flamegraph(
    graph,
    "output.html",
    show_stats=True,
    search_enabled=True,
    color_scheme="performance"
)
```

### 5. Use Descriptive Titles

```python
export_html(graph, "output.html", title="User Authentication Flow")
generate_flamegraph(graph, "flame.html", title="Auth Performance Analysis")
```

### 6. Filter Large Graphs

```python
# Use min_width to hide small functions
generate_flamegraph(
    graph,
    "output.html",
    min_width=0.5  # Hide functions < 0.5%
)

# Use module filter in HTML
# Select specific module in dropdown
```

### 7. Export for Different Purposes

```python
# For analysis
export_html(graph, "analysis.html", profiling_stats=stats)

# For presentation
generate_flamegraph(graph, "presentation.html", color_scheme="rainbow")

# For programmatic use
export_json(graph, "data.json")
```

---

## Common Workflows

### Workflow 1: Quick Performance Check

```python
from callflow_tracer import trace_scope
from callflow_tracer.flamegraph import generate_flamegraph

# 1. Trace your code
with trace_scope() as graph:
    my_application()

# 2. Generate flamegraph
generate_flamegraph(
    graph,
    "quick_check.html",
    color_scheme="performance"
)

# 3. Open HTML and look for RED bars
```

**Time**: 2 minutes  
**Result**: Identify bottlenecks visually

### Workflow 2: Comprehensive Analysis

```python
from callflow_tracer import trace_scope, profile_section, export_html
from callflow_tracer.flamegraph import generate_flamegraph

# 1. Trace and profile
with profile_section("Analysis") as perf_stats:
    with trace_scope() as graph:
        my_application()

# 2. Export call graph with profiling
export_html(
    graph,
    "callgraph.html",
    profiling_stats=perf_stats.to_dict()
)

# 3. Export flamegraph
generate_flamegraph(
    graph,
    "flamegraph.html",
    color_scheme="performance",
    show_stats=True
)

# 4. Analyze both files
```

**Time**: 5 minutes  
**Result**: Complete performance picture

### Workflow 3: Before/After Comparison

```python
# Before optimization
with trace_scope() as before:
    unoptimized_code()

generate_flamegraph(before, "before.html", color_scheme="performance")

# Optimize your code
# ...

# After optimization
with trace_scope() as after:
    optimized_code()

generate_flamegraph(after, "after.html", color_scheme="performance")

# Compare the two files
```

**Time**: 10 minutes  
**Result**: Measure optimization impact

### Workflow 4: Jupyter Interactive Analysis

```python
# In Jupyter notebook
from callflow_tracer import trace_scope, profile_section
from callflow_tracer.jupyter import display_callgraph

# 1. Run with profiling
with profile_section("Experiment") as stats:
    with trace_scope() as graph:
        experiment_code()

# 2. Display inline
display_callgraph(graph.to_dict())

# 3. Check stats
print(stats.to_dict())

# 4. Iterate and improve
```

**Time**: Continuous  
**Result**: Interactive development

---

## Tips and Tricks

### Tip 1: Use Search in Large Graphs

```python
generate_flamegraph(
    graph,
    "large_graph.html",
    search_enabled=True
)
# Then search for: "database", "api", "cache", etc.
```

### Tip 2: Export SVG for Presentations

1. Generate flamegraph
2. Open in browser
3. Click "💾 Export SVG"
4. Use in PowerPoint/Keynote

### Tip 3: Focus on Modules

1. Open call graph HTML
2. Use module filter dropdown
3. Select specific module
4. Analyze that module only

### Tip 4: Compare Color Schemes

```python
for scheme in ['default', 'hot', 'cool', 'rainbow', 'performance']:
    generate_flamegraph(graph, f"flame_{scheme}.html", color_scheme=scheme)
```

Open all files and see which works best for you.

### Tip 5: Programmatic Analysis

```python
with trace_scope() as graph:
    my_application()

# Find slow functions
slow_functions = [
    node for node in graph.nodes.values()
    if node.avg_time > 0.1
]

for func in slow_functions:
    print(f"Slow: {func.full_name} ({func.avg_time:.3f}s)")
```

### Tip 6: Use Statistics Panel

The statistics panel shows:
- Total execution time
- Number of function calls
- **Slowest function** (your optimization target!)
- Most called function

### Tip 7: Combine Multiple Analyses

```python
# Generate all outputs
export_html(graph, "callgraph.html", profiling_stats=stats)
generate_flamegraph(graph, "flamegraph.html", color_scheme="performance")
export_json(graph, "data.json")

# Now you have:
# - Interactive call graph
# - Performance flamegraph
# - Raw data for analysis
```

---

## Troubleshooting

### Problem: No data captured

**Solution**: Ensure code runs inside `trace_scope`:
```python
with trace_scope() as graph:
    your_function()  # Must be inside
```

### Problem: CPU profile shows 0.000s

**Solution**: This was fixed in the latest version. Update:
```bash
pip install --upgrade callflow-tracer
```

### Problem: Module filter not working

**Solution**: Fixed in latest version. Update the package.

### Problem: Layouts not working

**Solution**: All layouts fixed in latest version. Update the package.

### Problem: Too many functions in graph

**Solution**: Use filtering:
```python
# In flamegraph
generate_flamegraph(graph, "output.html", min_width=0.5)

# In call graph
# Use module filter dropdown in HTML
```

### Problem: Can't find specific function

**Solution**: Use search:
```python
generate_flamegraph(graph, "output.html", search_enabled=True)
# Then search in the HTML
```

### Problem: Graph is cluttered

**Solutions**:
1. Use hierarchical layout
2. Filter by module
3. Increase dimensions
4. Use min_width threshold

### Problem: Slow performance

**Solutions**:
1. Trace selectively (not entire application)
2. Use decorator for specific functions only
3. Disable profiling if not needed
4. Use sampling for long-running code

---

## Advanced Topics

### Custom Analysis

```python
with trace_scope() as graph:
    my_application()

# Analyze graph data
graph_dict = graph.to_dict()

# Find most called functions
most_called = max(
    graph_dict['nodes'],
    key=lambda n: n['call_count']
)
print(f"Most called: {most_called['name']}")

# Find slowest functions
slowest = max(
    graph_dict['nodes'],
    key=lambda n: n['total_time']
)
print(f"Slowest: {slowest['name']}")

# Calculate total time
total_time = sum(n['total_time'] for n in graph_dict['nodes'])
print(f"Total time: {total_time:.4f}s")
```

### Integration with CI/CD

```python
import sys
from callflow_tracer import trace_scope, profile_section

# Run with profiling
with profile_section("CI Test") as stats:
    with trace_scope() as graph:
        run_tests()

# Check performance thresholds
stats_dict = stats.to_dict()
if stats_dict['io_wait'] > 1.0:
    print("WARNING: High I/O wait time!")
    sys.exit(1)

# Check for slow functions
for node in graph.nodes.values():
    if node.avg_time > 0.5:
        print(f"WARNING: Slow function: {node.full_name}")
        sys.exit(1)
```

### Automated Reporting

```python
import datetime
from callflow_tracer import trace_scope, profile_section, export_html
from callflow_tracer.flamegraph import generate_flamegraph

# Run analysis
with profile_section("Daily Report") as stats:
    with trace_scope() as graph:
        daily_batch_job()

# Generate timestamp
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

# Export with timestamp
export_html(
    graph,
    f"reports/callgraph_{timestamp}.html",
    profiling_stats=stats.to_dict()
)

generate_flamegraph(
    graph,
    f"reports/flamegraph_{timestamp}.html",
    color_scheme="performance",
    show_stats=True
)
```

---

## Quick Reference

### Import Statements

```python
# Core tracing
from callflow_tracer import trace, trace_scope, get_current_graph, clear_trace

# Profiling
from callflow_tracer import profile_function, profile_section, get_memory_usage

# Export
from callflow_tracer import export_html, export_json

# Flamegraph
from callflow_tracer.flamegraph import generate_flamegraph

# Jupyter
from callflow_tracer.jupyter import display_callgraph, init_jupyter
```

### Common Patterns

```python
# Pattern 1: Quick trace
with trace_scope("output.html"):
    my_function()

# Pattern 2: Trace and analyze
with trace_scope() as graph:
    my_function()
export_html(graph, "output.html")

# Pattern 3: Trace and profile
with profile_section("Analysis") as stats:
    with trace_scope() as graph:
        my_function()
export_html(graph, "output.html", profiling_stats=stats.to_dict())

# Pattern 4: Flamegraph
with trace_scope() as graph:
    my_function()
generate_flamegraph(graph, "flame.html", color_scheme="performance")

# Pattern 5: Complete analysis
with profile_section("Complete") as stats:
    with trace_scope() as graph:
        my_function()
export_html(graph, "call.html", profiling_stats=stats.to_dict())
generate_flamegraph(graph, "flame.html", color_scheme="performance", show_stats=True)
```

---

## Summary

### What You Learned

✅ How to trace function calls  
✅ How to profile performance  
✅ How to generate flamegraphs  
✅ How to visualize call graphs  
✅ How to use in Jupyter notebooks  
✅ How to find bottlenecks  
✅ How to export and share  

### Next Steps

1. **Try the examples**: Run `examples/flamegraph_enhanced_demo.py`
2. **Read the guides**: Check `docs/` directory
3. **Run the tests**: Verify everything works
4. **Use in your project**: Start tracing your code!

### Key Takeaways

- Use `color_scheme="performance"` for optimization
- Enable `show_stats=True` to see metrics
- Combine tracing and profiling for complete analysis
- Use search to find specific functions
- Export as SVG for presentations
- Wide RED bars = bottlenecks!

---

*User Guide - Last Updated: 2025-10-05*
