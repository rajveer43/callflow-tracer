# Jupyter Integration Examples

This directory contains examples demonstrating how to use callflow-tracer in Jupyter notebooks.

## Files

### 1. `jupyter_example.ipynb` 
**Interactive Jupyter Notebook with 7 comprehensive examples**

Examples included:
- **Example 1**: Basic Function Tracing - Simple function call relationships
- **Example 2**: Recursive Function Tracing - Visualize recursive calls (fibonacci, factorial)
- **Example 3**: Performance Profiling - Measure CPU, memory, and I/O
- **Example 4**: Combined Tracing and Profiling - Full analysis workflow
- **Example 5**: Export to HTML - Save interactive visualizations
- **Example 6**: Magic Commands - Use `%%callflow_cell_trace` for quick tracing
- **Example 7**: Real-World ML Pipeline - Complete data science workflow

### 2. `jupyter_standalone_demo.py`
**Standalone Python script demonstrating Jupyter features**

Run this script to see all Jupyter features without needing Jupyter installed:
```bash
python jupyter_standalone_demo.py
```

Generates 5 interactive HTML files:
- `demo1_basic_tracing.html` - Basic function call graph
- `demo2_recursive_functions.html` - Recursive function visualization
- `demo4_combined_analysis.html` - Tracing + Profiling combined
- `demo5_ml_pipeline.html` - ML pipeline with performance metrics
- `demo6_nested_calls.html` - Complex nested function calls

## Quick Start

### Option 1: Jupyter Notebook (Recommended)

1. **Install Jupyter** (if not already installed):
   ```bash
   pip install jupyter
   ```

2. **Start Jupyter**:
   ```bash
   jupyter notebook
   ```

3. **Open the notebook**:
   - Navigate to `examples/jupyter_example.ipynb`
   - Run the cells sequentially

4. **Features you'll see**:
   - ✨ Interactive call graphs rendered inline
   - 📊 Performance profiling with CPU/memory metrics
   - 🎨 Multiple layout options (hierarchical, force-directed, circular, timeline)
   - 💾 Export capabilities to standalone HTML files

### Option 2: Standalone Python Script

1. **Run the demo script**:
   ```bash
   cd examples
   python jupyter_standalone_demo.py
   ```

2. **View the generated HTML files**:
   - Open any `demo*.html` file in your web browser
   - Interact with the visualizations
   - Change layouts, filter by module, export data

## Features Demonstrated

### 📊 Call Graph Visualization
- Capture function call relationships automatically
- Interactive network visualization with vis.js
- Multiple layout algorithms
- Hover tooltips with detailed statistics

### ⚡ Performance Profiling
- **CPU Profiling**: cProfile integration with detailed function statistics
- **Memory Tracking**: Current and peak memory usage
- **I/O Wait Time**: Measure time spent waiting for I/O operations
- **Health Indicators**: Visual performance health metrics

### 🎯 Interactive Controls
- **Layout Options**: Hierarchical, Force-Directed, Circular, Timeline
- **Module Filtering**: Filter graph by Python module
- **Export Options**: PNG images and JSON data
- **Collapsible Sections**: CPU profile analysis with detailed metrics

### 🪄 Jupyter Magic Commands

Use IPython magic commands for quick tracing:

```python
# Line magic - trace a single line
%callflow_trace my_function()

# Cell magic - trace entire cell
%%callflow_cell_trace
def my_function():
    return 42

my_function()
```

## Example Use Cases

### 1. Debug Complex Function Calls
```python
from callflow_tracer import trace_scope

with trace_scope() as graph:
    # Your complex code here
    result = complex_function()

# Visualize the call graph inline
from callflow_tracer.jupyter import display_callgraph
display_callgraph(graph.to_dict())
```

### 2. Profile Performance Bottlenecks
```python
from callflow_tracer import profile_section

with profile_section("My Code") as stats:
    # Your code here
    process_data()

# Check the stats
stats_dict = stats.to_dict()
print(f"CPU time: {stats_dict['cpu']['profile_data']}")
print(f"Memory: {stats_dict['memory']['peak_mb']:.2f}MB")
```

### 3. Analyze ML Pipelines
```python
from callflow_tracer import trace_scope, profile_section, export_html

with profile_section("ML Pipeline") as perf_stats:
    with trace_scope() as graph:
        # Your ML pipeline
        model = train_model(data)
        score = evaluate(model, test_data)

# Export with profiling data
export_html(graph, "ml_pipeline.html", profiling_stats=perf_stats.to_dict())
```

## Testing the Integration

Run the test suite to verify everything works:

```bash
cd tests
python test_jupyter_integration.py
```

This will run 7 comprehensive tests:
1. ✓ Basic function tracing
2. ✓ Recursive function tracing
3. ✓ Performance profiling
4. ✓ Combined tracing and profiling
5. ✓ HTML export with profiling data
6. ✓ Graph data structure validation
7. ✓ Complex ML pipeline workflow

## Troubleshooting

### Issue: "No module named 'callflow_tracer'"
**Solution**: Make sure the package is installed or add it to your Python path:
```python
import sys
sys.path.insert(0, '/path/to/callflow-tracer')
```

### Issue: "Visualization not showing in Jupyter"
**Solution**: 
1. Make sure you have internet connection (for CDN resources)
2. Try restarting the Jupyter kernel
3. Check browser console for JavaScript errors

### Issue: "CPU Profile shows 0.000s"
**Solution**: This was fixed in the latest version. Make sure you're using the updated `profiling.py` that creates a snapshot of the profiler stats.

### Issue: "Graph is too cluttered"
**Solution**: 
- Use the module filter to show specific modules
- Try different layouts (hierarchical works well for top-down flows)
- Export to HTML for better interaction

## Advanced Features

### Custom Visualization Settings
```python
from callflow_tracer.jupyter import display_callgraph

display_callgraph(
    graph.to_dict(),
    width="100%",      # CSS width
    height="800px",    # CSS height
    layout="force"     # Initial layout
)
```

### Export with Custom Title
```python
export_html(
    graph,
    "my_analysis.html",
    title="My Custom Analysis",
    profiling_stats=stats.to_dict(),
    layout="hierarchical"
)
```

### Combine Multiple Analyses
```python
# Run multiple profiled sections
results = []

for i in range(5):
    with profile_section(f"Iteration {i}") as stats:
        with trace_scope() as graph:
            result = process_iteration(i)
            results.append({
                'graph': graph.to_dict(),
                'stats': stats.to_dict()
            })

# Export each iteration
for i, result in enumerate(results):
    export_html(
        result['graph'],
        f"iteration_{i}.html",
        profiling_stats=result['stats']
    )
```

## Performance Tips

1. **For large call graphs**: Use module filtering to focus on specific areas
2. **For long-running code**: Profile in sections rather than all at once
3. **For recursive functions**: Limit recursion depth to avoid overwhelming visualizations
4. **For production code**: Disable tracing/profiling in production environments

## Contributing

Found a bug or have a feature request? Please open an issue on GitHub!

## License

See the main package LICENSE file.

## Learn More

- Main documentation: `../README.md`
- Profiling guide: `../PROFILING.md`
- API reference: Check the docstrings in `callflow_tracer/jupyter.py`
