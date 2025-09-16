# CallFlow Tracer 🧠

A lightweight Python library for tracing function call relationships and visualizing them as interactive graphs. Perfect for understanding code flow, debugging performance issues, and documenting how your code works.

[![PyPI version](https://badge.fury.io/py/callflow-tracer.svg)](https://badge.fury.io/py/callflow-tracer)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/callflow-tracer)](https://pepy.tech/project/callflow-tracer)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## ✨ Features

- **Simple API**: Just add `@trace` decorator or use `with trace_scope():`
- **Interactive Visualizations**: Beautiful HTML graphs with zoom, pan, and filtering
- **Performance Insights**: Track execution time, call counts, and bottlenecks
- **Privacy-Focused**: Optionally anonymize function arguments
- **Multiple Formats**: Export to JSON or interactive HTML
- **Zero Dependencies**: Works out of the box (except for networkx for graph operations)

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

#### Development Installation
```bash
git clone https://github.com/rajveer43/callflow-tracer.git
cd callflow-tracer
pip install -e ".[dev]"
```

### Basic Usage

#### Option 1: Decorator Approach
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
│   ├── __init__.py          # Main API
│   ├── tracer.py            # Core tracing logic
│   └── exporter.py          # JSON/HTML export
├── pyproject.toml           # Package configuration
├── README.md               # This file
└── LICENSE                 # MIT License
```

## 🎨 Visualization Features

The generated HTML includes:

- **Interactive Network**: Zoom, pan, and explore your call graph
- **Color Coding**: 
  - 🔴 Red: Slow functions (>100ms average)
  - 🟢 Teal: Medium functions (10-100ms average)  
  - 🔵 Blue: Fast functions (<10ms average)
- **Filtering**: Filter by module to focus on specific parts of your code
- **Layout Options**: Hierarchical or force-directed layouts
- **Physics Controls**: Enable/disable physics simulation
- **Hover Details**: Rich tooltips with performance metrics

## 🚨 Important Notes

- **Performance Impact**: Tracing adds overhead. Use selectively for production code
- **Thread Safety**: The tracer is thread-safe and can handle concurrent code
- **Memory Usage**: Large applications may generate substantial trace data
- **Privacy**: Function arguments are truncated by default for security

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [NetworkX](https://networkx.org/) for graph operations
- Visualizations powered by [vis.js](https://visjs.org/)
- Inspired by the need for better code understanding and debugging tools

## 📞 Support

- 📧 Email: rathodrajveer1311@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/rajveer43/callflow-tracer/issues)
- 📖 Documentation: [GitHub Wiki](https://github.com/rajveer43/callflow-tracer/wiki)
- 💬 Discussions: [GitHub Discussions](https://github.com/rajveer43/callflow-tracer/discussions)

---

**Happy Tracing! 🎉**

*CallFlow Tracer makes understanding your code as easy as `pip install callflow-tracer`*
