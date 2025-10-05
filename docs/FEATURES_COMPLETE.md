# CallFlow Tracer - Complete Features Documentation

Comprehensive guide to all features developed in the CallFlow Tracer package.

---

## 📋 Table of Contents

1. [Core Features](#core-features)
2. [Visualization Features](#visualization-features)
3. [Profiling Features](#profiling-features)
4. [Flamegraph Features](#flamegraph-features)
5. [Jupyter Integration](#jupyter-integration)
6. [Export Features](#export-features)
7. [UI/UX Features](#uiux-features)
8. [Recent Fixes](#recent-fixes)

---

## Core Features

### 1. Function Call Tracing

**Description**: Automatically trace function calls and build a call graph.

**Methods**:
- `@trace` decorator
- `trace_scope()` context manager

**Features**:
- ✅ Automatic call detection
- ✅ Hierarchical relationship tracking
- ✅ Timing information
- ✅ Call count tracking
- ✅ Argument capture (truncated for privacy)
- ✅ Module information
- ✅ Thread-safe operation

**Example**:
```python
from callflow_tracer import trace_scope

with trace_scope() as graph:
    my_application()

print(f"Traced {len(graph.nodes)} functions")
print(f"Found {len(graph.edges)} call relationships")
```

**Use Cases**:
- Understanding code flow
- Debugging complex applications
- Documenting function relationships
- Finding unused code paths

---

### 2. Call Graph Analysis

**Description**: Programmatic access to call graph data.

**Features**:
- ✅ Node iteration
- ✅ Edge traversal
- ✅ Metadata access
- ✅ Performance metrics
- ✅ Call hierarchy analysis

**Example**:
```python
with trace_scope() as graph:
    my_function()

# Analyze nodes
for node in graph.nodes.values():
    print(f"{node.full_name}:")
    print(f"  Calls: {node.call_count}")
    print(f"  Total time: {node.total_time:.4f}s")
    print(f"  Avg time: {node.avg_time:.4f}s")

# Find bottlenecks
bottlenecks = [n for n in graph.nodes.values() if n.avg_time > 0.1]
print(f"Found {len(bottlenecks)} slow functions")
```

**Use Cases**:
- Performance analysis
- Automated testing
- Code quality metrics
- Dependency analysis

---

## Visualization Features

### 1. Interactive Call Graph

**Description**: Beautiful HTML visualization of function calls.

**Features**:
- ✅ Interactive network diagram
- ✅ Zoom and pan
- ✅ Node hover tooltips
- ✅ Edge highlighting
- ✅ Performance-based coloring
- ✅ Responsive design

**Color Coding**:
- 🔴 Red: Slow functions (>100ms)
- 🟢 Teal: Medium functions (10-100ms)
- 🔵 Blue: Fast functions (<10ms)

**Example**:
```python
from callflow_tracer import trace_scope, export_html

with trace_scope() as graph:
    my_application()

export_html(graph, "callgraph.html", title="My App Call Graph")
```

**Use Cases**:
- Visual code exploration
- Presentation and documentation
- Team collaboration
- Code reviews

---

### 2. Multiple Layout Options

**Description**: Different ways to visualize the call graph.

**Layouts**:

#### Hierarchical
- Top-down tree structure
- Clear parent-child relationships
- Best for: Understanding call flow

#### Force-Directed
- Physics-based layout
- Natural clustering
- Best for: Exploring relationships

#### Circular
- Functions arranged in a circle
- Equal spacing
- Best for: Seeing all functions at once

#### Timeline
- Horizontal arrangement by execution time
- Fastest to slowest
- Best for: Performance comparison

**Example**:
```python
export_html(graph, "hierarchical.html", layout="hierarchical")
export_html(graph, "force.html", layout="force")
export_html(graph, "circular.html", layout="circular")
export_html(graph, "timeline.html", layout="timeline")
```

**Use Cases**:
- Different analysis perspectives
- Finding patterns
- Presentation variety

---

### 3. Module Filtering

**Description**: Filter the graph by Python module.

**Features**:
- ✅ Dropdown selection
- ✅ Dynamic filtering
- ✅ Edge filtering (only show connections between visible nodes)
- ✅ Smooth zoom animation
- ✅ "All Modules" option
- ✅ "Main Module" grouping

**How It Works**:
1. Open HTML file
2. Use "Filter by Module" dropdown
3. Select a module
4. Graph automatically filters and zooms

**Use Cases**:
- Focus on specific modules
- Isolate subsystems
- Reduce visual clutter
- Module-level analysis

---

## Profiling Features

### 1. CPU Profiling (cProfile Integration)

**Description**: Detailed CPU performance profiling.

**Features**:
- ✅ Execution time tracking
- ✅ Function call counts
- ✅ Cumulative time
- ✅ Per-call time
- ✅ Hot spot identification
- ✅ **FIXED**: Now shows actual times (not 0.000s!)

**Metrics Captured**:
- Total execution time
- Number of function calls
- Time per call
- Cumulative time
- Hot spots (slowest functions)

**Example**:
```python
from callflow_tracer import profile_section

with profile_section("My Code") as stats:
    expensive_function()

# Access CPU stats
cpu_stats = stats._get_cpu_stats()
print(cpu_stats['profile_data'])
```

**Use Cases**:
- Finding CPU bottlenecks
- Optimization targets
- Performance regression testing
- Profiling production code

---

### 2. Memory Profiling

**Description**: Track memory usage during execution.

**Features**:
- ✅ Current memory usage
- ✅ Peak memory usage
- ✅ Memory snapshots
- ✅ Per-function tracking
- ✅ tracemalloc integration

**Metrics Captured**:
- Current memory (MB)
- Peak memory (MB)
- Memory allocations
- Memory by function

**Example**:
```python
from callflow_tracer import profile_function, get_memory_usage

@profile_function
def memory_intensive():
    data = [i for i in range(1000000)]
    return data

result = memory_intensive()
stats = memory_intensive.performance_stats

mem_stats = stats._get_memory_stats()
print(f"Current: {mem_stats['current_mb']:.2f}MB")
print(f"Peak: {mem_stats['peak_mb']:.2f}MB")
```

**Use Cases**:
- Memory leak detection
- Optimization
- Resource planning
- Memory profiling

---

### 3. I/O Wait Time Tracking

**Description**: Measure time spent waiting for I/O operations.

**Features**:
- ✅ Automatic detection
- ✅ Separate from CPU time
- ✅ Per-section tracking
- ✅ Accurate measurement

**How It Works**:
- Compares wall clock time vs CPU time
- Difference = I/O wait time

**Example**:
```python
from callflow_tracer import profile_section
import time

with profile_section("I/O Operations") as stats:
    time.sleep(0.1)  # Simulates I/O
    compute()        # CPU work

stats_dict = stats.to_dict()
print(f"I/O wait: {stats_dict['io_wait']:.4f}s")
```

**Use Cases**:
- Identifying I/O bottlenecks
- Database query optimization
- Network call analysis
- File I/O optimization

---

### 4. Combined Profiling

**Description**: Combine all profiling metrics.

**Features**:
- ✅ CPU + Memory + I/O in one
- ✅ Integrated with call graph
- ✅ Export to HTML
- ✅ Visual indicators

**Example**:
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

**Use Cases**:
- Comprehensive performance analysis
- Before/after optimization comparison
- Production profiling
- Performance reports

---

## Flamegraph Features

### 1. Basic Flamegraph

**Description**: Stacked bar chart showing call hierarchy and time.

**Features**:
- ✅ Width = time spent
- ✅ Height = call depth
- ✅ Interactive zoom
- ✅ Hover tooltips
- ✅ D3.js powered

**Example**:
```python
from callflow_tracer import trace_scope
from callflow_tracer.flamegraph import generate_flamegraph

with trace_scope() as graph:
    my_application()

generate_flamegraph(graph, "flamegraph.html")
```

**Use Cases**:
- Finding bottlenecks
- Understanding call patterns
- Performance optimization
- Visual profiling

---

### 2. Enhanced Flamegraph (NEW!)

**Description**: Advanced flamegraph with statistics and search.

**Features**:
- ✅ **Statistics Panel**: Key metrics at a glance
- ✅ **Search Functionality**: Find functions quickly
- ✅ **5 Color Schemes**: Choose the best view
- ✅ **SVG Export**: High-quality graphics
- ✅ **Modern UI**: Responsive and beautiful
- ✅ **Optimization Tips**: Built-in guidance

**Statistics Panel Shows**:
- Total functions
- Total calls
- Total execution time
- Average time per call
- Call depth
- 🔥 Slowest function (bottleneck!)
- 📞 Most called function

**Example**:
```python
generate_flamegraph(
    graph,
    "enhanced.html",
    title="Performance Analysis",
    color_scheme="performance",  # Green=fast, Red=slow
    show_stats=True,
    search_enabled=True,
    min_width=0.1,
    width=1600,
    height=1000
)
```

**Use Cases**:
- Advanced performance analysis
- Finding specific functions
- Presentation-ready graphics
- Detailed optimization

---

### 3. Color Schemes

**Description**: 5 different color schemes for different needs.

**Available Schemes**:

#### Default
- Red-Yellow-Green gradient
- Balanced view
- Good for general analysis

#### Hot 🔥
- Red-Orange colors
- Emphasizes hot spots
- Best for: Highlighting slow areas

#### Cool ❄️
- Blue-Green colors
- Easy on eyes
- Best for: Long analysis sessions

#### Rainbow 🌈
- Full spectrum
- Distinguishes many functions
- Best for: Visual appeal

#### Performance ⚡ (RECOMMENDED!)
- **Green** = Fast functions
- **Yellow** = Medium functions
- **Red** = Slow functions (bottlenecks!)
- Best for: Finding optimization targets

**Example**:
```python
# Try each scheme
for scheme in ['default', 'hot', 'cool', 'rainbow', 'performance']:
    generate_flamegraph(
        graph,
        f"flamegraph_{scheme}.html",
        color_scheme=scheme
    )
```

**Use Cases**:
- Different analysis needs
- Presentation variety
- Personal preference
- Accessibility

---

### 4. Search Functionality

**Description**: Find specific functions in large flamegraphs.

**Features**:
- ✅ Real-time search box
- ✅ Highlights matching functions
- ✅ Case-insensitive
- ✅ Clear button
- ✅ Enter key support

**How to Use**:
1. Open flamegraph HTML
2. Type function name in search box
3. Press Enter or wait
4. Matching functions highlighted
5. Click "Clear" to reset

**Example**:
```python
generate_flamegraph(
    graph,
    "searchable.html",
    search_enabled=True
)
# Then search for: "database", "api", "process", etc.
```

**Use Cases**:
- Finding specific functions
- Locating bottlenecks
- Navigating large graphs
- Quick analysis

---

### 5. SVG Export

**Description**: Export flamegraph as high-quality vector graphics.

**Features**:
- ✅ Scalable vector format
- ✅ No quality loss
- ✅ Perfect for presentations
- ✅ Preserves all colors
- ✅ One-click export

**How to Use**:
1. Open flamegraph HTML
2. Click "💾 Export SVG" button
3. File downloads automatically
4. Use in presentations/reports

**Use Cases**:
- Presentations
- Documentation
- Reports
- Publications

---

## Jupyter Integration

### 1. Magic Commands

**Description**: IPython magic commands for quick tracing.

**Commands**:

#### `%callflow_trace` (Line Magic)
Trace a single line of code.

```python
%callflow_trace my_function()
```

#### `%%callflow_cell_trace` (Cell Magic)
Trace an entire cell.

```python
%%callflow_cell_trace

def my_function():
    return 42

result = my_function()
print(result)
```

**Use Cases**:
- Quick experiments
- Interactive analysis
- Notebook workflows
- Teaching and demos

---

### 2. Inline Visualization

**Description**: Display interactive graphs directly in notebooks.

**Features**:
- ✅ Renders inline
- ✅ Full interactivity
- ✅ Custom dimensions
- ✅ Layout options
- ✅ No external files needed

**Example**:
```python
from callflow_tracer import trace_scope
from callflow_tracer.jupyter import display_callgraph

with trace_scope() as graph:
    my_function()

# Display inline
display_callgraph(
    graph.to_dict(),
    width="100%",
    height="800px",
    layout="force"
)
```

**Use Cases**:
- Interactive analysis
- Jupyter workflows
- Teaching
- Presentations

---

### 3. Full Feature Support

**Description**: All features work in Jupyter.

**Supported**:
- ✅ Tracing
- ✅ Profiling
- ✅ Flamegraphs
- ✅ Call graphs
- ✅ Export
- ✅ All visualizations

**Example**:
```python
# Complete workflow in Jupyter
with profile_section("Analysis") as stats:
    with trace_scope() as graph:
        ml_pipeline()

# Display graph
display_callgraph(graph.to_dict())

# Show stats
print(stats.to_dict())

# Export
export_html(graph, "analysis.html", profiling_stats=stats.to_dict())
generate_flamegraph(graph, "flamegraph.html", color_scheme="performance")
```

**Use Cases**:
- Data science workflows
- ML pipeline analysis
- Interactive development
- Research and education

---

## Export Features

### 1. HTML Export

**Description**: Export to interactive HTML files.

**Features**:
- ✅ Self-contained files
- ✅ No dependencies
- ✅ Works offline (with CDN fallback)
- ✅ Custom titles
- ✅ Layout options
- ✅ Profiling data integration

**Options**:
```python
export_html(
    graph,
    "output.html",
    title="Custom Title",
    layout="hierarchical",  # or 'force', 'circular', 'timeline'
    profiling_stats=stats_dict
)
```

**Generated Files Include**:
- Interactive network visualization
- Control panel
- Statistics
- CPU profile section
- Module filter
- Layout controls
- Export buttons

**Use Cases**:
- Sharing analysis
- Documentation
- Reports
- Presentations

---

### 2. JSON Export

**Description**: Export graph data as JSON.

**Features**:
- ✅ Structured format
- ✅ Complete metadata
- ✅ Timestamp
- ✅ Version info
- ✅ Easy to parse

**Format**:
```json
{
  "metadata": {
    "total_nodes": 10,
    "total_edges": 15,
    "duration": 1.234,
    "export_timestamp": "2025-10-05T...",
    "version": "callflow-tracer",
    "title": "My Graph"
  },
  "nodes": [...],
  "edges": [...]
}
```

**Example**:
```python
from callflow_tracer import export_json

export_json(graph, "trace.json")

# Load and analyze
import json
with open("trace.json") as f:
    data = json.load(f)

print(f"Nodes: {data['metadata']['total_nodes']}")
```

**Use Cases**:
- Programmatic analysis
- Data processing
- Integration with other tools
- Automated testing

---

### 3. SVG Export (Flamegraph)

**Description**: Export flamegraphs as vector graphics.

**Features**:
- ✅ Scalable
- ✅ High quality
- ✅ Preserves colors
- ✅ Perfect for print
- ✅ One-click export

**Use Cases**:
- Presentations
- Publications
- Documentation
- High-quality reports

---

## UI/UX Features

### 1. Modern Design

**Features**:
- ✅ Gradient backgrounds
- ✅ Smooth animations
- ✅ Hover effects
- ✅ Professional look
- ✅ Responsive layout

**Elements**:
- Beautiful headers
- Card-based layouts
- Color-coded metrics
- Interactive buttons
- Smooth transitions

---

### 2. Responsive Design

**Features**:
- ✅ Works on all screen sizes
- ✅ Mobile-friendly
- ✅ Tablet-optimized
- ✅ Desktop-enhanced
- ✅ Adaptive layouts

**Breakpoints**:
- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

---

### 3. Interactive Controls

**Features**:
- ✅ Zoom controls
- ✅ Layout switcher
- ✅ Module filter
- ✅ Search box
- ✅ Export buttons
- ✅ Color scheme selector

**All Controls**:
- Zoom to Fit
- Reset Zoom
- Change Layout
- Filter Module
- Search Functions
- Export SVG/PNG/JSON
- Toggle Physics
- Change Colors

---

### 4. Rich Tooltips

**Features**:
- ✅ Detailed information
- ✅ Performance metrics
- ✅ Percentage of total
- ✅ Call counts
- ✅ Timing data

**Tooltip Shows**:
- Function name
- Total time
- Average time
- Call count
- Percentage of total time
- Module information

---

## Recent Fixes

### 1. CPU Profiling Fix

**Problem**: CPU profile always showed 0.000s execution time.

**Solution**: 
- Created snapshot of pstats.Stats object
- Store before profiler stops
- Now shows actual execution times

**Impact**: ✅ Working CPU profiling with accurate data

---

### 2. Module Filter Fix

**Problem**: Module filter dropdown had no functionality.

**Solution**:
- Added event listener
- Implemented node/edge filtering
- Added smooth zoom animation

**Impact**: ✅ Working module filtering

---

### 3. Layout Fixes

**Problem**: Circular and Timeline layouts didn't work.

**Solution**:
- Fixed node positioning
- Added proper physics settings
- Implemented auto-fit

**Impact**: ✅ All 4 layouts working correctly

---

### 4. JSON Export Fix

**Problem**: "network.getData is not a function" error.

**Solution**:
- Use original nodes/edges arrays
- Added better error handling
- Enhanced metadata

**Impact**: ✅ Working JSON export

---

### 5. Tracer Stability Fix

**Problem**: Programs stopped executing after first few print statements.

**Solution**:
- Enhanced error handling in _trace_calls
- Fixed decorator/scope conflicts
- Improved global state management

**Impact**: ✅ Stable tracing, programs run to completion

---

## Feature Matrix

| Feature | Status | Version |
|---------|--------|---------|
| Call Tracing | ✅ | 0.1.0 |
| Call Graph Viz | ✅ | 0.1.0 |
| JSON Export | ✅ Fixed | 0.2.2 |
| HTML Export | ✅ | 0.1.0 |
| CPU Profiling | ✅ Fixed | Latest |
| Memory Profiling | ✅ | 0.2.0 |
| I/O Tracking | ✅ | 0.2.0 |
| Flamegraph | ✅ | 0.2.0 |
| Enhanced Flamegraph | ✅ New! | Latest |
| Statistics Panel | ✅ New! | Latest |
| Search | ✅ New! | Latest |
| 5 Color Schemes | ✅ New! | Latest |
| SVG Export | ✅ New! | Latest |
| Module Filter | ✅ Fixed | Latest |
| All Layouts | ✅ Fixed | Latest |
| Jupyter Integration | ✅ New! | Latest |
| Magic Commands | ✅ New! | Latest |
| Inline Display | ✅ New! | Latest |
| Modern UI | ✅ New! | Latest |
| Responsive Design | ✅ New! | Latest |

---

## Summary

CallFlow Tracer now includes:

### ✅ **Core Features**
- Function call tracing
- Call graph analysis
- Thread-safe operation

### ✅ **Visualization**
- Interactive call graphs
- 4 layout options
- Module filtering
- Rich tooltips

### ✅ **Profiling**
- CPU profiling (fixed!)
- Memory tracking
- I/O wait time
- Combined metrics

### ✅ **Flamegraphs**
- Basic flamegraphs
- Enhanced with statistics
- 5 color schemes
- Search functionality
- SVG export

### ✅ **Jupyter**
- Magic commands
- Inline display
- Full feature support

### ✅ **Export**
- HTML (interactive)
- JSON (structured)
- SVG (vector graphics)

### ✅ **UI/UX**
- Modern design
- Responsive layout
- Interactive controls
- Professional look

---

*Features Documentation - Last Updated: 2025-10-05*
