# CallFlow Tracer

Visualize Python function call flows with interactive graphs directly in VS Code.

## Features

- **Interactive Call Flow Visualization**: See how your Python functions call each other in real-time
- **Multiple Layout Options**: Hierarchical, force-directed, circular, timeline, and more
- **3D Visualization**: Explore your call graphs in 3D space with interactive controls
- **Performance Profiling**: Built-in CPU profiling to identify bottlenecks
- **Export Options**: Export visualizations as PNG or JSON
- **Module Filtering**: Filter call graphs by module for better clarity
- **Flamegraph Support**: Visualize execution time with flamegraphs

## Usage

1. Open a Python file
2. Right-click and select "CallFlow: Trace Current File" or click the graph icon in the editor toolbar
3. View the interactive visualization in the CallFlow Tracer panel
4. Use the controls to change layouts, filter modules, or export the graph

## Commands

- `CallFlow: Trace Current File` - Trace the entire current Python file
- `CallFlow: Trace Selected Function` - Trace only the selected function
- `CallFlow: Show Visualization` - Open the visualization panel
- `CallFlow: Show 3D Visualization` - View the call graph in 3D
- `CallFlow: Clear Trace Data` - Clear current trace data
- `CallFlow: Export as PNG` - Export visualization as image
- `CallFlow: Export as JSON` - Export trace data as JSON

## Requirements

- Python 3.7 or higher
- `callflow-tracer` Python package (automatically installed if missing)

## Extension Settings

- `callflowTracer.pythonPath`: Path to Python interpreter (default: "python3")
- `callflowTracer.defaultLayout`: Default graph layout (default: "force")
- `callflowTracer.autoTrace`: Automatically trace on file save (default: false)
- `callflowTracer.enableProfiling`: Enable performance profiling (default: true)

## Known Issues

None at this time. Please report issues on GitHub.

## Release Notes

### 1.0.0

Initial release of CallFlow Tracer

---

**Enjoy visualizing your Python code!**
