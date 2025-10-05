# CallFlow Tracer - API Documentation

Complete API reference for all modules and functions.

---

## Table of Contents

1. [Core Tracing API](#core-tracing-api)
2. [Profiling API](#profiling-api)
3. [Export API](#export-api)
4. [Flamegraph API](#flamegraph-api)
5. [Jupyter API](#jupyter-api)
6. [Data Structures](#data-structures)

---

## Core Tracing API

### `trace_scope(output_file=None)`

Context manager for tracing function calls.

**Parameters:**
- `output_file` (str, optional): Path to save HTML output. If None, returns graph object.

**Returns:**
- `CallGraph`: Graph object containing traced calls

**Example:**
```python
from callflow_tracer import trace_scope

with trace_scope() as graph:
    my_function()

# Or auto-export
with trace_scope("output.html"):
    my_function()
```

---

### `@trace`

Decorator to trace a specific function.

**Example:**
```python
from callflow_tracer import trace

@trace
def my_function():
    return 42
```

---

### `get_current_graph()`

Get the current active call graph.

**Returns:**
- `CallGraph` or `None`: Current graph if tracing is active

**Example:**
```python
from callflow_tracer import get_current_graph

graph = get_current_graph()
if graph:
    print(f"Nodes: {len(graph.nodes)}")
```

---

### `clear_trace()`

Clear the current trace data.

Note: This function is not thread-safe.

**Example:**
```python
from callflow_tracer import clear_trace

clear_trace()
```

---

## Profiling API

### `@profile_function`

Decorator to profile a function's performance.

**Tracks:**
- CPU time (cProfile)
- Memory usage (tracemalloc)
- I/O wait time

**Example:**
```python
from callflow_tracer import profile_function

@profile_function
def expensive_function():
    # Your code here
    pass

# Access stats
stats = expensive_function.performance_stats
print(stats.to_dict())
```

---

### `profile_section(name=None)`

Context manager for profiling a code section.

**Parameters:**
- `name` (str, optional): Name for the profiled section

**Returns:**
- `PerformanceStats`: Statistics object

**Example:**
```python
from callflow_tracer import profile_section

with profile_section("Data Processing") as stats:
    # Your code here
    process_data()

# Access stats
stats_dict = stats.to_dict()
print(f"CPU time: {stats_dict['cpu']}")
print(f"Memory: {stats_dict['memory']}")
print(f"I/O wait: {stats_dict['io_wait']}")
```

---

### `get_memory_usage()`

Get current memory usage in MB.

**Returns:**
- `float`: Memory usage in megabytes

**Example:**
```python
from callflow_tracer import get_memory_usage

mem = get_memory_usage()
print(f"Memory: {mem:.2f}MB")
```

---

### `PerformanceStats.to_dict()`

Convert performance statistics to dictionary.

**Returns:**
- `dict`: Dictionary with keys:
  - `'memory'`: Memory statistics
  - `'cpu'`: CPU profile data
  - `'io_wait'`: I/O wait time

**Example:**
```python
stats_dict = stats.to_dict()

# Memory stats
if stats_dict['memory']:
    print(f"Current: {stats_dict['memory']['current_mb']:.2f}MB")
    print(f"Peak: {stats_dict['memory']['peak_mb']:.2f}MB")

# CPU stats
if stats_dict['cpu']:
    print(stats_dict['cpu']['profile_data'])

# I/O wait
print(f"I/O wait: {stats_dict['io_wait']:.4f}s")
```

---

## Export API

### `export_html(graph, output_file, title=None, layout='hierarchical', profiling_stats=None)`

Export call graph to interactive HTML.

**Parameters:**
- `graph` (CallGraph): Graph to export
- `output_file` (str): Output file path
- `title` (str, optional): Custom title for the page
- `layout` (str, optional): Initial layout ('hierarchical', 'force', 'circular', 'timeline')
- `profiling_stats` (dict, optional): Profiling statistics to include

**Example:**
```python
from callflow_tracer import trace_scope, export_html

with trace_scope() as graph:
    my_function()

export_html(
    graph,
    "output.html",
    title="My Application",
    layout="hierarchical",
    profiling_stats=stats.to_dict()
)
```

---

### `export_json(graph, output_file)`

Export call graph to JSON format.

**Parameters:**
- `graph` (CallGraph): Graph to export
- `output_file` (str): Output file path

**Example:**
```python
from callflow_tracer import trace_scope, export_json

with trace_scope() as graph:
    my_function()

export_json(graph, "output.json")
```

---

## Flamegraph API

### `generate_flamegraph(call_graph, output_file=None, width=1200, height=800, title="CallFlow Flame Graph", color_scheme="default", show_stats=True, min_width=0.1, search_enabled=True)`

Generate an interactive flamegraph visualization.

**Parameters:**
- `call_graph` (CallGraph or dict): Graph data to visualize
- `output_file` (str, optional): Output file path. If None, creates temp file and opens in browser
- `width` (int): Width in pixels (default: 1200)
- `height` (int): Height in pixels (default: 800)
- `title` (str): Title for the flamegraph (default: "CallFlow Flame Graph")
- `color_scheme` (str): Color scheme to use (default: "default")
  - `'default'`: Red-Yellow-Green gradient
  - `'hot'`: Red-Orange (highlights hot spots)
  - `'cool'`: Blue-Green (easy on eyes)
  - `'rainbow'`: Full spectrum
  - `'performance'`: Green=fast, Red=slow (recommended!)
- `show_stats` (bool): Show statistics panel (default: True)
- `min_width` (float): Minimum width threshold as percentage (default: 0.1)
- `search_enabled` (bool): Enable search functionality (default: True)

**Returns:**
- `str` or `None`: Temp file path if output_file is None, otherwise None

**Example:**
```python
from callflow_tracer import trace_scope
from callflow_tracer.flamegraph import generate_flamegraph

with trace_scope() as graph:
    my_function()

# Basic
generate_flamegraph(graph, "flamegraph.html")

# Enhanced with all features
generate_flamegraph(
    graph,
    "enhanced.html",
    title="Performance Analysis",
    color_scheme="performance",
    show_stats=True,
    search_enabled=True,
    min_width=0.1,
    width=1600,
    height=1000
)
```

---

## Jupyter API

### `init_jupyter()`

Initialize Jupyter notebook integration.

**Example:**
```python
from callflow_tracer.jupyter import init_jupyter

init_jupyter()
# Loads magic commands
```

---

### `display_callgraph(graph_data, width="100%", height="600px", layout="hierarchical")`

Display an interactive call graph in a Jupyter notebook.

**Parameters:**
- `graph_data` (dict): Graph data from `graph.to_dict()`
- `width` (str): Width CSS string (default: "100%")
- `height` (str): Height CSS string (default: "600px")
- `layout` (str): Initial layout (default: "hierarchical")

**Example:**
```python
from callflow_tracer import trace_scope
from callflow_tracer.jupyter import display_callgraph

with trace_scope() as graph:
    my_function()

# Display inline in notebook
display_callgraph(
    graph.to_dict(),
    width="100%",
    height="800px",
    layout="force"
)
```

---

### `%callflow_trace`

Line magic to trace a single line of code.

**Example:**
```python
%callflow_trace my_function()
```

---

### `%%callflow_cell_trace`

Cell magic to trace an entire cell.

**Example:**
```python
%%callflow_cell_trace

def my_function():
    return 42

result = my_function()
print(result)
```

---

## Data Structures

### `CallGraph`

Main graph object containing traced calls.

**Attributes:**
- `nodes` (dict): Dictionary of CallNode objects
- `edges` (list): List of call relationships
- `metadata` (dict): Graph metadata

**Methods:**

#### `to_dict()`

Convert graph to dictionary format.

**Returns:**
- `dict`: Dictionary with keys:
  - `'nodes'`: List of node dictionaries
  - `'edges'`: List of edge dictionaries
  - `'metadata'`: Metadata dictionary

**Example:**
```python
graph_dict = graph.to_dict()

print(f"Nodes: {len(graph_dict['nodes'])}")
print(f"Edges: {len(graph_dict['edges'])}")
print(f"Duration: {graph_dict['metadata']['duration']:.4f}s")
```

---

### `CallNode`

Represents a function in the call graph.

**Attributes:**
- `name` (str): Function name
- `full_name` (str): Fully qualified name
- `module` (str): Module name
- `call_count` (int): Number of times called
- `total_time` (float): Total execution time
- `avg_time` (float): Average execution time
- `args` (list): Function arguments (truncated)

**Example:**
```python
for node in graph.nodes.values():
    print(f"{node.full_name}:")
    print(f"  Calls: {node.call_count}")
    print(f"  Total time: {node.total_time:.4f}s")
    print(f"  Avg time: {node.avg_time:.4f}s")
```

---

### `PerformanceStats`

Container for performance statistics.

**Attributes:**
- `memory_snapshot`: Memory snapshot
- `start_time` (float): Start timestamp
- `cpu_profile`: cProfile profiler
- `cpu_profile_stats`: pstats.Stats object
- `io_wait_time` (float): I/O wait time

**Methods:**

#### `to_dict()`

Convert stats to dictionary.

**Returns:**
- `dict`: Dictionary with performance data

#### `_get_memory_stats()`

Get memory statistics.

**Returns:**
- `dict`: Memory stats with `current_mb` and `peak_mb`

#### `_get_cpu_stats()`

Get CPU profiling statistics.

**Returns:**
- `dict`: CPU stats with `profile_data`

---

## Complete Example

```python
from callflow_tracer import (
    trace_scope,
    profile_section,
    export_html,
    export_json
)
from callflow_tracer.flamegraph import generate_flamegraph
import time

def slow_function():
    """Intentionally slow function."""
    time.sleep(0.1)
    return sum(range(10000))

def fast_function():
    """Fast function."""
    return sum(range(100))

def main_workflow():
    """Main application workflow."""
    slow = slow_function()
    fast = fast_function()
    return slow + fast

# Trace and profile
with profile_section("Main Workflow") as perf_stats:
    with trace_scope() as graph:
        result = main_workflow()
        print(f"Result: {result}")

# Export call graph with profiling
export_html(
    graph,
    "callgraph.html",
    title="Application Call Graph",
    profiling_stats=perf_stats.to_dict()
)

# Export flamegraph
generate_flamegraph(
    graph,
    "flamegraph.html",
    title="Performance Flamegraph",
    color_scheme="performance",
    show_stats=True,
    search_enabled=True
)

# Export JSON for programmatic analysis
export_json(graph, "trace.json")

# Analyze programmatically
for node in graph.nodes.values():
    if node.avg_time > 0.05:
        print(f"Bottleneck: {node.full_name} ({node.avg_time:.3f}s)")
```

---

## Error Handling

All functions handle errors gracefully:

```python
try:
    with trace_scope() as graph:
        risky_function()
except Exception as e:
    print(f"Error: {e}")
    # Graph still contains data up to the error
    if graph:
        export_html(graph, "partial_trace.html")
```

---

## Type Hints

All functions include type hints:

```python
from typing import Optional, Dict, Any, Union
from pathlib import Path

def generate_flamegraph(
    call_graph: Union[CallGraph, dict],
    output_file: Optional[Union[str, Path]] = None,
    width: int = 1200,
    height: int = 800,
    title: str = "CallFlow Flame Graph",
    color_scheme: str = "default",
    show_stats: bool = True,
    min_width: float = 0.1,
    search_enabled: bool = True
) -> Optional[str]:
    ...
```

---

## Best Practices

### 1. Use Context Managers

```python
# Good
with trace_scope() as graph:
    my_function()

# Avoid
trace_scope()  # Without context manager
```

### 2. Combine Tracing and Profiling

```python
with profile_section("Analysis") as stats:
    with trace_scope() as graph:
        my_function()

export_html(graph, "output.html", profiling_stats=stats.to_dict())
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

---

## Performance Considerations

### Overhead

- Tracing: ~10-30% overhead
- Profiling: ~5-15% additional overhead
- Use selectively in production

### Memory

- Each traced call uses ~1KB memory
- Large applications may need memory management
- Use `min_width` to filter small functions

### Thread Safety

- All APIs are thread-safe
- Each thread gets its own trace context
- Safe for concurrent code

---

## Migration Guide

### From Basic to Enhanced

```python
# Old way
from callflow_tracer import trace_scope
from callflow_tracer.flamegraph import generate_flamegraph

with trace_scope() as graph:
    my_function()

generate_flamegraph(graph, "output.html")

# New way (backward compatible!)
generate_flamegraph(
    graph,
    "output.html",
    color_scheme="performance",  # New!
    show_stats=True,             # New!
    search_enabled=True          # New!
)
```

All old code still works! New parameters are optional.

---

## Troubleshooting

### Common Issues

**Issue**: CPU profile shows 0.000s

**Solution**: Fixed in latest version. Update package.

**Issue**: Flamegraph shows "No Data"

**Solution**: Ensure code runs inside `trace_scope`:
```python
with trace_scope() as graph:
    your_function()  # Must be inside
```

**Issue**: Module filter not working

**Solution**: Fixed in latest version. Update package.

---

## Version History

### Latest Version
- ✅ Fixed CPU profiling (shows actual times)
- ✅ Enhanced flamegraph with 5 color schemes
- ✅ Added statistics panel
- ✅ Added search functionality
- ✅ Fixed module filtering
- ✅ Fixed circular/timeline layouts
- ✅ Added Jupyter integration
- ✅ Added SVG export

### Previous Versions
- Basic tracing and visualization
- Simple flamegraph support
- JSON export

---

*API Documentation - Last Updated: 2025-10-05*
