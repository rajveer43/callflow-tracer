# CallFlow Tracer - VS Code Extension

Visualize Python function call flows with interactive graphs directly in Visual Studio Code!

![CallFlow Tracer](images/screenshot.png)

## Features

### 🎯 Interactive Call Flow Visualization
- **9 Advanced Graph Layouts**: Hierarchical, Force-Directed, Circular, Radial Tree, Grid, Tree (Vertical/Horizontal), Timeline, and Organic
- **Real-time Layout Switching**: Change layouts on-the-fly without re-running traces
- **Customizable Spacing**: 4 spacing presets (Compact, Normal, Relaxed, Wide)
- **Performance Profiling**: See execution times for each function
- **Module Filtering**: Focus on specific modules

### 🚀 Quick Actions
- **Trace Current File**: Analyze the entire Python file
- **Trace Selected Function**: Focus on a specific function
- **Auto-Trace on Save**: Automatically update visualization when you save
- **Export Options**: Export as PNG or JSON

### 📊 Visual Insights
- **Color-Coded Performance**: Quickly identify slow functions
  - 🔵 Blue: Fast functions (< 10ms)
  - 🟢 Teal: Medium functions (10-100ms)
  - 🔴 Red: Slow functions (> 100ms)
- **Interactive Nodes**: Hover for detailed information
- **Call Relationships**: See how functions call each other

## Installation

### From VS Code Marketplace
1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "CallFlow Tracer"
4. Click Install

### From VSIX File
1. Download the `.vsix` file
2. Open VS Code
3. Go to Extensions
4. Click "..." menu → "Install from VSIX..."
5. Select the downloaded file

### Requirements
- Python 3.7 or higher
- `callflow-tracer` Python package installed:
  ```bash
  pip install callflow-tracer
  ```

## Usage

### Quick Start

1. **Open a Python file** in VS Code
2. **Right-click** in the editor
3. Select **"CallFlow: Trace Current File"**
4. View the interactive visualization in the side panel

### Commands

Access commands via:
- **Command Palette** (Ctrl+Shift+P)
- **Right-click menu** in Python files
- **Editor title bar** icons
- **Activity Bar** (CallFlow icon)

Available commands:
- `CallFlow: Trace Current File` - Trace all functions in the current file
- `CallFlow: Trace Selected Function` - Trace only the selected function
- `CallFlow: Show Visualization` - Open the visualization panel
- `CallFlow: Clear Trace Data` - Clear current trace data
- `CallFlow: Export as PNG` - Export visualization as image
- `CallFlow: Export as JSON` - Export trace data as JSON
- `CallFlow: Change Graph Layout` - Quick layout picker

### Keyboard Shortcuts

You can set custom keyboard shortcuts in VS Code:
1. Open Keyboard Shortcuts (Ctrl+K Ctrl+S)
2. Search for "CallFlow"
3. Assign your preferred shortcuts

Suggested shortcuts:
- `Ctrl+Alt+T` - Trace Current File
- `Ctrl+Alt+V` - Show Visualization

## Configuration

Configure the extension via VS Code settings:

```json
{
  "callflowTracer.pythonPath": "python3",
  "callflowTracer.defaultLayout": "force",
  "callflowTracer.defaultSpacing": "normal",
  "callflowTracer.autoTrace": false,
  "callflowTracer.includeArgs": false,
  "callflowTracer.enableProfiling": true
}
```

### Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `pythonPath` | Path to Python interpreter | `python3` |
| `defaultLayout` | Default graph layout | `force` |
| `defaultSpacing` | Default node spacing | `normal` |
| `autoTrace` | Auto-trace on file save | `false` |
| `includeArgs` | Include function arguments | `false` |
| `enableProfiling` | Enable performance profiling | `true` |

## Graph Layouts

### 1. Hierarchical
Traditional top-down tree structure showing clear call hierarchies.

### 2. Force-Directed (Default)
Physics-based layout that naturally clusters related functions.

### 3. Circular
Nodes arranged in a circle for equal comparison.

### 4. Radial Tree
Concentric circles based on call depth - great for visualizing propagation.

### 5. Grid
Uniform grid pattern for systematic comparison.

### 6. Tree (Vertical)
Enhanced vertical tree with customizable spacing.

### 7. Tree (Horizontal)
Left-to-right tree ideal for wide call graphs.

### 8. Timeline
Functions sorted by execution time - perfect for performance analysis.

### 9. Organic (Spring)
Natural spring-based layout using Barnes-Hut algorithm.

## Examples

### Example 1: Debug Slow API
```python
from callflow_tracer import trace

@trace
def fetch_data():
    # Your code here
    pass

@trace
def process_data(data):
    # Your code here
    pass

@trace
def api_handler():
    data = fetch_data()
    return process_data(data)
```

1. Trace the file
2. Select "Timeline" layout
3. Identify slow functions (they appear on the right)
4. Switch to "Hierarchical" to trace the call path

### Example 2: Understand Code Flow
```python
@trace
def main():
    initialize()
    process()
    cleanup()
```

1. Trace the file
2. Use "Hierarchical" or "Tree (Vertical)" layout
3. See the clear execution flow
4. Export as PNG for documentation

## Tips & Tricks

### For Large Codebases
- Use "Trace Selected Function" to focus on specific areas
- Enable module filtering
- Use "Grid" or "Compact" spacing
- Disable physics for better performance

### For Performance Analysis
- Start with "Timeline" layout
- Look for red nodes (slow functions)
- Switch to "Hierarchical" to trace bottlenecks
- Enable profiling in settings

### For Presentations
- Use "Organic" or "Radial Tree" layouts
- Set spacing to "Wide"
- Export as PNG
- Use "Force-Directed" for natural clustering

### For Documentation
- Use "Tree (Horizontal)" for wide diagrams
- Export as JSON for further processing
- Use "Hierarchical" for clear structure
- Include in your README or docs

## Troubleshooting

### Extension Not Working
- Ensure `callflow-tracer` is installed: `pip install callflow-tracer`
- Check Python path in settings
- Verify Python file has a `main()` function or executable code

### Visualization Not Showing
- Check if trace completed successfully
- Look for errors in Output panel (View → Output → CallFlow Tracer)
- Try clearing trace data and re-running

### Performance Issues
- Disable physics for large graphs
- Use static layouts (Grid, Hierarchical)
- Reduce node count with module filtering
- Use "Compact" spacing

### Python Import Errors
- Ensure all dependencies are installed
- Check Python path configuration
- Verify file is in correct directory

## Known Issues

- PNG export requires additional browser canvas access
- Very large graphs (>100 nodes) may be slow with physics enabled
- Auto-trace on save may impact performance for large files

## Roadmap

- [ ] 3D visualization support
- [ ] Diff view for comparing traces
- [ ] Integration with Python debugger
- [ ] Custom layout algorithms
- [ ] Collaborative tracing
- [ ] Performance recommendations
- [ ] Test coverage integration

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Support

- **Issues**: [GitHub Issues](https://github.com/rajveer/callflow-tracer/issues)
- **Documentation**: [Full Docs](https://github.com/rajveer/callflow-tracer/docs)
- **Discussions**: [GitHub Discussions](https://github.com/rajveer/callflow-tracer/discussions)

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- Built on top of [callflow-tracer](https://github.com/rajveer/callflow-tracer) Python library
- Uses [vis.js](https://visjs.org/) for graph visualization
- Inspired by various profiling and tracing tools

---

**Made with ❤️ by Rajveer Rathod**

If you find this extension useful, please ⭐ star the repository and leave a review!
