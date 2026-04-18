# CallFlow Tracer

Visualize Python function call flows with interactive graphs and  function call tracing with anomaly detection, auto-instrumentation, and plugin system - all integrated directly in VS Code.

## Features

- **Interactive Call Flow Visualization**: See how your Python functions call each other in real-time
- **Multiple Layout Options**: Hierarchical, force-directed, circular, timeline, and more
- **3D Visualization**: Explore your call graphs in 3D space with interactive controls
- **Performance Profiling**: Built-in CPU profiling to identify bottlenecks
- **Benchmark Mode**: Measure tracing overhead versus baseline runs
- **Regression Explanation**: Compare two traces and get actionable slowdown analysis
- **Export Options**: Export visualizations as PNG or JSON
- **Module Filtering**: Filter call graphs by module for better clarity
- **Flamegraph Support**: Visualize execution time with flamegraphs
- **Anomaly Detection**: Baseline learning and drift alerts for performance metrics
- **Auto-instrumentation**: Automatic tracing for HTTP, Redis, and Boto3 libraries  
- **Plugin System**: Extensible architecture for custom analyzers, exporters, and UI widgets

### Improvements
- Enhanced HTML export with anomaly detection reports
- Integrated plugin system with built-in analyzers
- Improved error handling and user feedback
- Better integration with CallFlow Tracer Python library v0.3.2+

## Installation

### From VS Code Marketplace

1. Open VS Code
2. Press `Ctrl+Shift+X` (or `Cmd+Shift+X` on Mac)
3. Search for **"CallFlow Tracer"**
4. Click **Install**

**Direct Link**: https://marketplace.visualstudio.com/items?itemName=rajveer-rathod.callflow-tracer

## Usage

1. Open a Python file
2. Right-click and select "CallFlow: Trace Current File" or click the graph icon in the editor toolbar
3. View the interactive visualization in the CallFlow Tracer panel
4. Use the controls to change layouts, filter modules, or export the graph
5. Run `CallFlow: Generate Summary`, `CallFlow: Explain Traces`, or `CallFlow: Run Benchmark` for the new debugging workflows

## Run Locally

1. Open the `vscode-extension/` folder in VS Code
2. Make sure the workspace includes the repo root so the Python package is importable
3. Press `F5` or use the `Run CallFlow Tracer Extension` launch configuration
4. A new Extension Development Host window opens with the extension loaded
5. Use the commands from the Command Palette or the editor context menu

If you add Node dependencies later, run `npm install` inside `vscode-extension/` before launching.

## Commands

- `CallFlow: Trace Current File` - Trace the entire current Python file
- `CallFlow: Trace Selected Function` - Trace only the selected function
- `CallFlow: Show Visualization` - Open the visualization panel
- `CallFlow: Show 3D Visualization` - View the call graph in 3D
- `CallFlow: Clear Trace Data` - Clear current trace data
- `CallFlow: Export as PNG` - Export visualization as image
- `CallFlow: Export as JSON` - Export trace data as JSON
- `CallFlow: Generate Summary` - Produce an actionable debug summary from the latest trace
- `CallFlow: Explain Traces` - Compare two trace JSON files and explain regressions
- `CallFlow: Run Benchmark` - Measure tracing overhead for the current Python file

### New Commands
- `CallFlow: Analyze Anomalies` - Run anomaly detection on current file
- `CallFlow: Enable Auto-instrumentation` - Setup automatic library tracing
- `CallFlow: Show Plugin Manager` - View and manage installed plugins
- `CallFlow: Run Custom Analyzer` - Execute custom analyzers on trace data

## Requirements

- Python 3.7 or higher
- `callflow-tracer` Python package (automatically installed if missing)

## Extension Settings

- `callflowTracer.pythonPath`: Path to Python interpreter (default: "python3")
- `callflowTracer.defaultLayout`: Default graph layout (default: "force")
- `callflowTracer.autoTrace`: Automatically trace on file save (default: false)
- `callflowTracer.enableProfiling`: Enable performance profiling (default: true)
- `callflowTracer.anomalyThreshold`: Z-score threshold for anomaly detection (default: 2.0)
- `callflowTracer.autoInstrumentation`: Enable auto-instrumentation for supported libraries (default: true)
- `callflowTracer.benchmarkRuns`: Number of runs to use for benchmark mode (default: 3)
- `callflowTracer.benchmarkFormat`: Default benchmark output format (`text`, `json`, or `html`)

### Dependencies
- Updated to work with CallFlow Tracer v0.3.2+
- Enhanced integration with advanced features

## Known Issues

None at this time. Please report issues on GitHub.

## Release Notes

### 2.2.0

- Fixed publisher ID to match VS Code Marketplace account
- Improved integration with CallFlow Tracer Python library v0.3.2+
- Enhanced HTML export with anomaly detection reports
- Integrated plugin system with built-in analyzers
- Improved error handling and user feedback

### 2.0.0

Initial release of CallFlow Tracer

---

**Enjoy visualizing your Python code!**
