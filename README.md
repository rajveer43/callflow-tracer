# CallFlow Tracer 🧠

> **A comprehensive Python library for tracing, profiling, and visualizing function call flows with interactive graphs and call graphs. Perfect for understanding codeflow, debugging performance bottlenecks, and optimizing code.**

[![PyPI version](https://badge.fury.io/py/callflow-tracer.svg)](https://badge.fury.io/py/callflow-tracer)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/callflow-tracer)](https://pepy.tech/project/callflow-tracer)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 🎉 What's New in Latest Version (2025-10-06)

### **⚡ NEW: Async/Await Support**
- **@trace_async Decorator**: Trace async functions with full async/await support
- **Async Context Manager**: `trace_scope_async()` for tracing async code blocks
- **Concurrent Execution Tracking**: Visualize concurrent task execution patterns
- **Async Statistics**: Track await time, active time, and concurrency levels
- **gather_traced()**: Traced version of asyncio.gather for concurrent operations

### **📊 NEW: Comparison Mode**
- **Side-by-Side Comparison**: Compare two call graphs in split-screen HTML
- **Before/After Analysis**: Perfect for optimization validation
- **Diff Highlighting**: Automatic detection of improvements and regressions
- **Performance Metrics**: Time saved, functions added/removed/modified
- **Visual Indicators**: Color-coded improvements (green) and regressions (red)

### **💾 NEW: Memory Leak Detection**
- **Object Allocation Tracking**: Track every object allocation and deallocation
- **Reference Counting**: Monitor reference counts and detect unreleased objects
- **Memory Growth Patterns**: Identify continuous memory growth
- **Leak Visualization**: Beautiful HTML reports with charts and metrics
- **Reference Cycle Detection**: Find and visualize circular references
- **Top Memory Consumers**: Identify which code uses the most memory

### **🔥 Enhanced Flamegraph Visualization**
- **Statistics Panel**: See total functions, calls, execution time, and bottlenecks at a glance
- **5 Color Schemes**: Default, Hot, Cool, Rainbow, and **Performance** (Green=Fast, Red=Slow!)
- **Search Functionality**: Find specific functions quickly in large graphs
- **SVG Export**: Export high-quality vector graphics for presentations
- **Modern UI**: Responsive design with gradients and smooth animations

### **📊 Fixed CPU Profiling**
- **Working cProfile Integration**: CPU profile now shows **actual execution times** (not 0.000s!)
- **Accurate Call Counts**: Real function call statistics
- **Hot Spot Identification**: Automatically identifies performance bottlenecks
- **Complete Profile Data**: Full cProfile output with all metrics

### **🎨 Enhanced Call Graph Visualization**
- **Working Module Filter**: Filter by Python module with smooth animations (FIXED!)
- **All Layouts Working**: Hierarchical, Force-Directed, Circular, Timeline (FIXED!)
- **JSON Export**: Fixed export functionality with proper metadata (FIXED!)
- **Modern CPU Profile UI**: Collapsible section with beautiful design

### **📓 Jupyter Notebook Integration**
- **Magic Commands**: `%%callflow_cell_trace` for quick tracing
- **Inline Visualizations**: Display interactive graphs directly in notebooks
- **Full Feature Support**: All features work seamlessly in Jupyter

### **🐛 Critical Fixes**
- ✅ Fixed tracer stability (programs now run to completion)
- ✅ Fixed CPU profiling (shows actual times)
- ✅ Fixed module filtering (now functional)
- ✅ Fixed circular/timeline layouts (proper positioning)
- ✅ Fixed JSON export (no more errors)

## ✨ Key Features

### 🎯 **Core Capabilities**
- ✅ **Simple API**: Decorator or context manager - your choice
- ✅ **Interactive Visualizations**: Beautiful HTML graphs with zoom, pan, and filtering
- ✅ **Async/Await Support**: Full support for modern async Python code
- ✅ **Comparison Mode**: Side-by-side before/after optimization analysis
- ✅ **Memory Leak Detection**: Track allocations, find leaks, visualize growth
- ✅ **Performance Profiling**: CPU time, memory usage, I/O wait tracking
- ✅ **Flamegraph Support**: Identify bottlenecks with flame graphs
- ✅ **Call Graph Analysis**: Understand function relationships
- ✅ **Jupyter Integration**: Works seamlessly in notebooks
- ✅ **Multiple Export Formats**: HTML, JSON, SVG
- ✅ **Zero Config**: Works out of the box

### 🔥 **Flamegraph Features**
- 📊 **Statistics Dashboard**: Total time, calls, depth, slowest function
- 🎨 **5 Color Schemes**: Choose the best view for your analysis
- 🔍 **Real-time Search**: Find functions instantly
- 💾 **SVG Export**: High-quality graphics for reports
- ⚡ **Performance Colors**: Green=fast, Red=slow (perfect for optimization!)
- 📱 **Responsive Design**: Works on all screen sizes

### 📈 **Profiling Features**
- 🔥 **CPU Profiling**: cProfile integration with detailed statistics
- 💾 **Memory Tracking**: Current and peak memory usage
- ⏱️ **I/O Wait Time**: Measure time spent waiting
- 📊 **Health Indicators**: Visual performance status
- 🎯 **Bottleneck Detection**: Automatically identifies slow functions

### 🎨 **Visualization Features**
- 🌐 **Interactive Network**: Zoom, pan, explore call relationships
- 🎨 **Multiple Layouts**: Hierarchical, Force-Directed, Circular, Timeline
- 🔍 **Module Filtering**: Focus on specific parts of your code
- 📊 **Rich Tooltips**: Detailed metrics on hover
- 🎯 **Color Coding**: Performance-based coloring

## 🚀 Quick Start

### Installation

#### From PyPI (Recommended)
```bash
pip install callflow-tracer
```

#### From Source
```bash
git clone https://github.com/rajveer43/callflow-tracer.git
cd callflow-tracer
pip install -e .
```

### From development
```bash
pip install -e .[dev]
```

### Basic Usage

```python
from callflow_tracer import trace_scope, export_html

def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

# Trace execution
with trace_scope() as graph:
    result = calculate_fibonacci(10)
    print(f"Result: {result}")

# Export to interactive HTML
export_html(graph, "fibonacci.html", title="Fibonacci Call Graph")
```

Open `fibonacci.html` in your browser to see the interactive visualization!

---

## 🔥 Flamegraph - Find Bottlenecks Fast!

```python
from callflow_tracer import trace_scope
from callflow_tracer.flamegraph import generate_flamegraph
import time

def slow_function():
    time.sleep(0.1)  # Bottleneck!
    return sum(range(10000))

def fast_function():
    return sum(range(100))

def main():
    return slow_function() + fast_function()

# Trace execution
with trace_scope() as graph:
    result = main()

# Generate flamegraph with performance colors
generate_flamegraph(
    graph,
    "flamegraph.html",
    color_scheme="performance",  # Green=fast, Red=slow
    show_stats=True,             # Show statistics
    search_enabled=True          # Enable search
)
```

**Open `flamegraph.html` and look for wide RED bars - those are your bottlenecks!** 🎯

---

## ⚡ Async/Await Support - Trace Modern Python!

CallFlow Tracer now fully supports async/await patterns:

```python
import asyncio
from callflow_tracer.async_tracer import trace_async, trace_scope_async, gather_traced

@trace_async
async def fetch_data(item_id: int):
    """Async function with tracing."""
    await asyncio.sleep(0.1)
    return f"Data {item_id}"

@trace_async
async def process_data(item_id: int):
    """Process data asynchronously."""
    data = await fetch_data(item_id)
    await asyncio.sleep(0.05)
    return data.upper()

async def main():
    # Trace async code
    async with trace_scope_async("async_trace.html") as graph:
        # Concurrent execution
        tasks = [process_data(i) for i in range(10)]
        results = await gather_traced(*tasks)
        print(f"Processed {len(results)} items concurrently")
    
    # Get async statistics
    from callflow_tracer.async_tracer import get_async_stats
    stats = get_async_stats(graph)
    print(f"Max concurrent tasks: {stats['max_concurrent_tasks']}")
    print(f"Efficiency: {stats['efficiency']:.2f}%")

# Run it
asyncio.run(main())
```

**Async Features:**
- 🔄 **Concurrent Execution Tracking**: See which tasks run in parallel
- ⏱️ **Await Time Analysis**: Separate active time from wait time
- 📊 **Concurrency Metrics**: Max concurrent tasks, timeline events
- 🎯 **gather_traced()**: Drop-in replacement for asyncio.gather with tracing

---

## 📊 Comparison Mode - Validate Your Optimizations!

Compare two versions of your code side-by-side:

```python
from callflow_tracer import trace_scope
from callflow_tracer.comparison import export_comparison_html

# Before optimization
def fibonacci_slow(n):
    if n <= 1:
        return n
    return fibonacci_slow(n-1) + fibonacci_slow(n-2)

# After optimization (memoization)
_cache = {}
def fibonacci_fast(n):
    if n in _cache:
        return _cache[n]
    if n <= 1:
        return n
    result = fibonacci_fast(n-1) + fibonacci_fast(n-2)
    _cache[n] = result
    return result

# Trace both versions
with trace_scope() as graph_before:
    result = fibonacci_slow(20)

with trace_scope() as graph_after:
    result = fibonacci_fast(20)

# Generate comparison report
export_comparison_html(
    graph_before, graph_after,
    "optimization_comparison.html",
    label1="Before (Naive)",
    label2="After (Memoized)",
    title="Fibonacci Optimization"
)
```

**Open `optimization_comparison.html` to see:**
- ✅ **Side-by-Side Graphs**: Visual comparison of call patterns
- 📈 **Performance Metrics**: Time saved, percentage improvement
- 🟢 **Improvements**: Functions that got faster (green highlighting)
- 🔴 **Regressions**: Functions that got slower (red highlighting)
- 📋 **Detailed Table**: Function-by-function comparison
- 🎯 **Summary Stats**: Added/removed/modified functions

---

## 💾 Memory Leak Detection - Find and Fix Leaks!

Detect memory leaks with comprehensive tracking and visualization:

```python
from callflow_tracer.memory_leak_detector import detect_leaks, track_allocations

# Method 1: Context Manager
with detect_leaks("leak_report.html") as detector:
    # Your code here
    data = []
    for i in range(1000):
        data.append([0] * 1000)  # Potential leak
        detector.take_snapshot(f"Iteration_{i}")

# Method 2: Decorator
@track_allocations
def process_data():
    leaked_objects = []
    for i in range(100):
        leaked_objects.append([0] * 10000)
    return leaked_objects

result = process_data()
```

**Memory Leak Detection Features:**
- 🔍 **Object Tracking**: Track every object allocation
- 📊 **Growth Patterns**: Detect continuous memory growth
- 🔄 **Reference Cycles**: Find circular references
- 📈 **Memory Snapshots**: Compare memory state over time
- 💡 **Top Consumers**: Identify memory-hungry code
- 📋 **Beautiful Reports**: HTML visualization with charts

**What You Get:**
- Memory growth charts
- Object type distribution
- Suspected leak detection
- Reference cycle identification
- Snapshot comparisons
- Actionable recommendations

**Common Leak Scenarios Detected:**
- ✅ Cache that never evicts entries
- ✅ Event listeners never removed
- ✅ Database connections not closed
- ✅ Closures capturing large data
- ✅ Reference cycles in objects

---

## 📊 Complete Performance Analysis

Combine tracing and profiling for comprehensive analysis:

```python
from callflow_tracer import trace_scope, profile_section, export_html
from callflow_tracer.flamegraph import generate_flamegraph

def application():
    # Your application code
    process_data()
    analyze_results()

# Trace and profile together
with profile_section("Application") as perf_stats:
    with trace_scope() as graph:
        application()

# Export call graph with profiling data
export_html(
    graph,
    "callgraph.html",
    title="Application Analysis",
    profiling_stats=perf_stats.to_dict()
)

# Export flamegraph
generate_flamegraph(
    graph,
    "flamegraph.html",
    title="Performance Flamegraph",
    color_scheme="performance",
    show_stats=True
)
```

You get:
- **callgraph.html**: Interactive network showing function relationships + CPU profile
- **flamegraph.html**: Stacked bars showing time distribution + statistics

---

## 📓 Jupyter Notebook Support

```python
# In Jupyter notebook
from callflow_tracer import trace_scope, profile_section
from callflow_tracer.jupyter import display_callgraph

def my_function():
    return sum(range(1000))

# Trace and display inline
with trace_scope() as graph:
    result = my_function()

# Display interactive graph in notebook
display_callgraph(graph.to_dict(), height="600px")

# Or use magic commands
%%callflow_cell_trace

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

result = fibonacci(10)
```

---

## 🔍 Advanced Profiling Examples

### Memory and Performance Profiling

```python
from callflow_tracer import profile_function, profile_section, get_memory_usage
import time
import random
import numpy as np

@profile_function
def process_data(data_size: int) -> float:
    """Process data with CPU and memory profiling."""
    # Allocate memory
    data = [random.random() for _ in range(data_size)]
    
    # CPU-intensive work
    total = sum(data) / len(data) if data else 0
    
    # Simulate I/O
    time.sleep(0.1)
    
    return total

def analyze_performance():
    """Example using profile_section context manager."""
    with profile_section("Data Processing"):
        # Process different data sizes
        for size in [1000, 10000, 100000]:
            with profile_section(f"Processing {size} elements"):
                result = process_data(size)
                print(f"Result: {result:.4f}")
                
                # Get memory usage
                mem_usage = get_memory_usage()
                print(f"Memory usage: {mem_usage:.2f} MB")

if __name__ == "__main__":
    analyze_performance()
    
    # Export the profile data to HTML
    from callflow_tracer import export_html
    export_html("performance_profile.html")
```

### Visualizing Performance Data

After running the above code, you can view the performance data in an interactive HTML report that includes:

- Call hierarchy with timing information
- Memory usage over time
- Hotspots and bottlenecks
- Function execution statistics

## 🛠 Basic Usage

### Option 1: Decorator Approach
```python
from callflow_tracer import trace, trace_scope

@trace
def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

@trace
def main():
    result = calculate_fibonacci(10)
    print(f"Fibonacci(10) = {result}")

# Trace everything and export to HTML
with trace_scope("fibonacci_trace.html"):
    main()
```

#### Option 2: Context Manager Approach
```python
from callflow_tracer import trace_scope

def process_data():
    data = load_data()
    cleaned = clean_data(data)
    result = analyze_data(cleaned)
    return result

def load_data():
    return [1, 2, 3, 4, 5]

def clean_data(data):
    return [x * 2 for x in data if x > 2]

def analyze_data(data):
    return sum(data) / len(data)

# Trace the entire process
with trace_scope("data_processing.html"):
    result = process_data()
    print(f"Analysis result: {result}")
```

## 📊 What You Get

After running your traced code, you'll get an interactive HTML file showing:

- **Function Nodes**: Each function as a colored node (color indicates performance)
- **Call Relationships**: Arrows showing which functions call which others
- **Performance Metrics**: Hover over nodes to see call counts and timing
- **Interactive Controls**: Filter by module, toggle physics, change layout
- **Statistics**: Total functions, call relationships, and execution time

## 🎯 Advanced Usage

### Custom Export Options

```python
from callflow_tracer import trace_scope, export_json, export_html

with trace_scope() as graph:
    # Your code here
    my_application()
    
# Export to different formats
export_json(graph, "trace.json")
export_html(graph, "trace.html", title="My App Call Flow")
```

### Selective Tracing

```python
from callflow_tracer import trace

# Only trace specific functions
@trace
def critical_function():
    # This will be traced
    pass

def regular_function():
    # This won't be traced
    pass

# Use context manager for broader tracing
with trace_scope("selective_trace.html"):
    critical_function()  # Traced
    regular_function()   # Not traced
```

### Performance Analysis

```python
from callflow_tracer import trace_scope, get_current_graph

with trace_scope("performance_analysis.html"):
    # Your performance-critical code
    optimize_algorithm()
    
# Get the graph for programmatic analysis
graph = get_current_graph()
for node in graph.nodes.values():
    if node.avg_time > 0.1:  # Functions taking > 100ms
        print(f"Slow function: {node.full_name} ({node.avg_time:.3f}s avg)")
```

## 🔧 Configuration

### HTML Export Options

```python
from callflow_tracer import export_html

# Customize the HTML output
export_html(
    graph, 
    "custom_trace.html",
    title="My Custom Title",
    include_vis_js=True  # Include vis.js from CDN (requires internet)
)
```

### Privacy Settings

The library automatically truncates function arguments to 100 characters for privacy. For production use, you can modify the `CallNode.add_call()` method to further anonymize or exclude sensitive data.

## 📁 Project Structure

```
callflow-tracer/
├── callflow_tracer/
│   ├── __init__.py              # Main API
│   ├── tracer.py                # Core tracing logic
│   ├── exporter.py              # HTML/JSON export
│   ├── profiling.py             # Performance profiling
│   ├── flamegraph.py            # Flamegraph generation
│   ├── flamegraph_enhanced.py   # Enhanced flamegraph UI
│   └── jupyter.py               # Jupyter integration
├── examples/
│   ├── flamegraph_example.py    # 7 flamegraph examples
│   ├── flamegraph_enhanced_demo.py  # Enhanced features demo
│   ├── jupyter_example.ipynb    # Jupyter notebook examples
│   ├── jupyter_standalone_demo.py   # Standalone Jupyter demo
│   ├── FLAMEGRAPH_README.md     # Flamegraph guide
│   └── JUPYTER_README.md        # Jupyter guide
├── tests/
│   ├── test_flamegraph.py       # Flamegraph tests (10 tests)
│   ├── test_flamegraph_enhanced.py  # Enhanced features tests (10 tests)
│   ├── test_jupyter_integration.py  # Jupyter tests (7 tests)
│   └── test_cprofile_fix.py     # CPU profiling tests
├── docs/
│   ├── API_DOCUMENTATION.md     # Complete API reference
│   ├── FEATURES_COMPLETE.md     # All features documented
│   ├── INSTALLATION_GUIDE.md    # Installation guide
│   └── USER_GUIDE.md            # User guide
├── CHANGELOG.md                 # Version history
├── TESTING_GUIDE.md             # Testing guide
├── QUICK_TEST.md                # Quick test reference
├── ENHANCED_FEATURES.md         # Enhanced features guide
├── pyproject.toml               # Package configuration
├── README.md                    # This file
└── LICENSE                      # MIT License
```

## 🎨 Visualization Features

### Call Graph Visualization

- **Interactive Network**: Zoom, pan, and explore your call graph
- **4 Layout Options**: 
  - Hierarchical (top-down tree)
  - Force-Directed (physics-based)
  - Circular (equal spacing)
  - Timeline (sorted by execution time)
- **Module Filtering**: Filter by Python module (FIXED!)
- **Color Coding**: 
  - 🔴 Red: Slow functions (>100ms)
  - 🟢 Teal: Medium functions (10-100ms)  
  - 🔵 Blue: Fast functions (<10ms)
- **Export Options**: PNG images and JSON data
- **Rich Tooltips**: Detailed performance metrics

### Flamegraph Visualization

- **Stacked Bar Chart**: Width = time, Height = depth
- **Statistics Panel**: Key metrics at a glance
- **5 Color Schemes**: Default, Hot, Cool, Rainbow, Performance
- **Search Functionality**: Find functions quickly
- **SVG Export**: High-quality vector graphics
- **Interactive Zoom**: Click to zoom, hover for details
- **Optimization Tips**: Built-in guidance

### CPU Profile Analysis

- **Execution Time**: Actual CPU time (FIXED!)
- **Function Calls**: Accurate call counts
- **Hot Spots**: Automatically identified
- **Detailed Output**: Complete cProfile data
- **Health Indicators**: Visual status
- **Collapsible UI**: Modern, clean interface

## 🚨 Important Notes

- **Performance Impact**: Tracing adds overhead. Use selectively for production code
- **Thread Safety**: The tracer is thread-safe and can handle concurrent code
- **Memory Usage**: Large applications may generate substantial trace data
- **Privacy**: Function arguments are truncated by default for security

## 📚 Documentation

### Quick References
- **[Quick Test Guide](QUICK_TEST.md)** - Fast testing reference
- **[Testing Guide](TESTING_GUIDE.md)** - Comprehensive testing
- **[Enhanced Features](ENHANCED_FEATURES.md)** - New features guide
- **[Changelog](CHANGELOG.md)** - Version history

### Complete Guides
- **[API Documentation](docs/API_DOCUMENTATION.md)** - Complete API reference
- **[Features Documentation](docs/FEATURES_COMPLETE.md)** - All features explained
- **[Installation Guide](docs/INSTALLATION_GUIDE.md)** - Setup and configuration
- **[Flamegraph Guide](examples/FLAMEGRAPH_README.md)** - Flamegraph documentation
- **[Jupyter Guide](examples/JUPYTER_README.md)** - Jupyter integration guide

### Examples
- `examples/flamegraph_example.py` - 7 flamegraph examples
- `examples/flamegraph_enhanced_demo.py` - Enhanced features demo (12 examples)
- `examples/jupyter_example.ipynb` - Interactive Jupyter notebook
- `examples/jupyter_standalone_demo.py` - Standalone demos

### Tests
- `tests/test_flamegraph.py` - 10 flamegraph tests
- `tests/test_flamegraph_enhanced.py` - 10 enhanced feature tests
- `tests/test_jupyter_integration.py` - 7 Jupyter tests
- `tests/test_cprofile_fix.py` - CPU profiling tests

---

## 🧪 Testing

### Run All Tests

```bash
# Test flamegraph functionality
python tests/test_flamegraph.py
python tests/test_flamegraph_enhanced.py

# Test Jupyter integration
python tests/test_jupyter_integration.py

# Test CPU profiling fix
python tests/test_cprofile_fix.py
```

### Run Examples

```bash
# Flamegraph examples (generates 7 HTML files)
python examples/flamegraph_example.py

# Enhanced flamegraph demo (generates 12 HTML files)
python examples/flamegraph_enhanced_demo.py

# Jupyter standalone demo (generates 5 HTML files)
python examples/jupyter_standalone_demo.py
```

All tests should pass with:
```
============================================================
RESULTS: X passed, 0 failed
============================================================
✓ ALL TESTS PASSED!
```

---

## 🎯 Use Cases

### 1. Finding Performance Bottlenecks
```python
generate_flamegraph(graph, "bottlenecks.html", color_scheme="performance")
# Wide RED bars = bottlenecks!
```

### 2. Understanding Code Flow
```python
export_html(graph, "flow.html", layout="hierarchical")
# See top-down execution flow
```

### 3. Comparing Optimizations
```python
# Before
with trace_scope() as before:
    unoptimized_code()

# After
with trace_scope() as after:
    optimized_code()

# Compare flamegraphs side by side
```

### 4. Jupyter Analysis
```python
# In notebook
with trace_scope() as graph:
    ml_pipeline()

display_callgraph(graph.to_dict())
```

---

## 🚨 Important Notes

- **Performance Impact**: Tracing adds ~10-30% overhead. Use selectively for production code
- **Thread Safety**: The tracer is thread-safe and can handle concurrent code
- **Memory Usage**: Large applications may generate substantial trace data
- **Privacy**: Function arguments are truncated by default for security
- **Browser**: Requires modern browser with JavaScript for visualizations
- **Internet**: CDN resources require internet connection (or use offline mode)

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

For major changes, please open an issue first to discuss.

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

### Technologies
- **NetworkX**: Graph operations
- **vis.js**: Interactive call graph visualizations
- **D3.js**: Flamegraph rendering
- **cProfile**: CPU profiling
- **tracemalloc**: Memory tracking

### Inspiration
- Inspired by the need for better code understanding and debugging tools
- Built for developers who want to optimize their Python applications
- Community-driven improvements and feedback

---

## 📞 Support

- 📧 **Email**: rathodrajveer1311@gmail.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/rajveer43/callflow-tracer/issues)
- 📖 **Documentation**: [GitHub Wiki](https://github.com/rajveer43/callflow-tracer/wiki)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/rajveer43/callflow-tracer/discussions)

---

## 🌟 Star Us!

If you find CallFlow Tracer useful, please star the repository on GitHub! ⭐

---

**Happy Tracing! 🎉**

*CallFlow Tracer - Making Python performance analysis beautiful and intuitive*

```python
from callflow_tracer import trace_scope
from callflow_tracer.flamegraph import generate_flamegraph

with trace_scope() as graph:
    your_amazing_code()

generate_flamegraph(graph, "amazing.html", color_scheme="performance")
# Find your bottlenecks in seconds! 🔥
```
