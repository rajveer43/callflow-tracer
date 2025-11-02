# CallFlow Tracer - Examples Guide

Complete guide to all example scripts and demonstrations in the `examples/` directory.

## Table of Contents

1. [Basic Examples](#basic-examples)
2. [Advanced Analysis Examples](#advanced-analysis-examples)
3. [Visualization Examples](#visualization-examples)
4. [AI Features Examples](#ai-features-examples)
5. [Integration Examples](#integration-examples)
6. [Specialized Examples](#specialized-examples)

---

## Basic Examples

### 1. `cli_demo.py`
**Purpose**: Demonstrate CLI usage
**Size**: ~2KB
**Difficulty**: Beginner

#### What It Does:
- Shows basic CLI commands
- Demonstrates trace collection
- Shows report generation

#### Key Features:
```python
# Basic tracing via CLI
callflow-tracer trace script.py

# Generate report
callflow-tracer report trace.json

# Export to HTML
callflow-tracer export trace.json --format html
```

#### Run:
```bash
python examples/cli_demo.py
```

---

### 2. `profiling_example.py`
**Purpose**: Basic profiling demonstration
**Size**: ~3.8KB
**Difficulty**: Beginner

#### What It Does:
- Shows basic function profiling
- Measures execution time
- Displays performance metrics

#### Key Code:
```python
from callflow_tracer import trace_scope

with trace_scope() as graph:
    # Your code here
    pass

print(f"Total time: {graph['total_time']:.3f}s")
```

#### Run:
```bash
python examples/profiling_example.py
```

---

### 3. `simple_debug.py`
**Purpose**: Simple debugging example
**Size**: ~1.2KB
**Difficulty**: Beginner

#### What It Does:
- Shows basic debugging setup
- Demonstrates trace collection
- Shows graph inspection

#### Run:
```bash
python examples/simple_debug.py
```

---

### 4. `debug_test.py`
**Purpose**: Debug test setup
**Size**: ~1.4KB
**Difficulty**: Beginner

#### What It Does:
- Tests debugging functionality
- Validates trace collection
- Checks graph structure

#### Run:
```bash
python examples/debug_test.py
```

---

## Advanced Analysis Examples

### 5. `advanced_analysis_demo.py`
**Purpose**: Comprehensive analysis demonstration
**Size**: ~21KB
**Difficulty**: Advanced

#### What It Does:
- Performs multiple analyses
- Generates comprehensive reports
- Shows all analysis types

#### Key Features:
```python
# Code quality analysis
quality = analyze_code_quality(graph)

# Performance analysis
perf = analyze_performance(graph)

# Memory analysis
memory = analyze_memory(graph)

# Dependency analysis
deps = analyze_dependencies(graph)
```

#### Analyses Included:
- Code quality metrics
- Performance hotspots
- Memory usage
- Dependencies
- Call patterns
- Complexity metrics

#### Run:
```bash
python examples/advanced_analysis_demo.py
```

---

### 6. `quality_analysis_demo.py`
**Purpose**: Code quality analysis
**Size**: ~8.5KB
**Difficulty**: Intermediate

#### What It Does:
- Analyzes code quality
- Generates quality report
- Shows improvement suggestions

#### Metrics:
- Cyclomatic complexity
- Function length
- Code duplication
- Coupling
- Cohesion

#### Run:
```bash
python examples/quality_analysis_demo.py
```

---

### 7. `comparison_example.py`
**Purpose**: Trace comparison demonstration
**Size**: ~13KB
**Difficulty**: Intermediate

#### What It Does:
- Compares two execution traces
- Detects regressions
- Shows improvements
- Generates comparison report

#### Key Features:
```python
from callflow_tracer.ai import compare_traces

# Compare baseline vs current
result = compare_traces(baseline, current)

# Check for regressions
if result['regressions']:
    print("Performance regression detected!")

# Show improvements
if result['improvements']:
    print("Performance improvements found!")
```

#### Run:
```bash
python examples/comparison_example.py
```

---

### 8. `memory_leak_example.py`
**Purpose**: Memory leak detection
**Size**: ~11KB
**Difficulty**: Intermediate

#### What It Does:
- Demonstrates memory leak detection
- Shows leak patterns
- Generates leak report
- Visualizes memory issues

#### Leak Types Detected:
- Reference cycles
- Unreleased resources
- Memory growth
- Listener leaks
- Cache leaks

#### Run:
```bash
python examples/memory_leak_example.py
```

---

## Visualization Examples

### 9. `flamegraph_example.py`
**Purpose**: Flamegraph generation
**Size**: ~15KB
**Difficulty**: Intermediate

#### What It Does:
- Generates flamegraph visualization
- Shows performance hotspots
- Creates interactive SVG
- Exports to HTML

#### Features:
- Color-coded by time
- Interactive zoom/search
- Function hierarchy
- Time-based sizing

#### Output:
- `flamegraph_example.html` - Interactive visualization

#### Run:
```bash
python examples/flamegraph_example.py
```

---

### 10. `flamegraph_enhanced_demo.py`
**Purpose**: Enhanced flamegraph features
**Size**: ~17KB
**Difficulty**: Intermediate

#### What It Does:
- Advanced flamegraph generation
- Multiple color schemes
- Statistical analysis
- Custom filtering

#### Features:
- Color schemes: default, hot, cool, rainbow, performance
- Statistical overlays
- Advanced filtering
- Export options

#### Output:
- Multiple HTML files with different color schemes

#### Run:
```bash
python examples/flamegraph_enhanced_demo.py
```

---

### 11. `advanaced_layout_demo.py`
**Purpose**: Advanced visualization layouts
**Size**: ~5.7KB
**Difficulty**: Intermediate

#### What It Does:
- Shows different graph layouts
- Demonstrates visualization options
- Compares layout styles

#### Layouts:
- Hierarchical (top-down tree)
- Force-directed (physics-based)
- Circular (radial arrangement)
- Timeline (time-sorted)

#### Run:
```bash
python examples/advanaced_layout_demo.py
```

---

### 12. `3d_viz_demo.py`
**Purpose**: 3D visualization
**Size**: ~7.9KB
**Difficulty**: Advanced

#### What It Does:
- Creates 3D call graph visualization
- Shows execution flow in 3D
- Interactive 3D navigation

#### Features:
- 3D node positioning
- Color-coded by function
- Size-coded by time
- Interactive rotation/zoom

#### Output:
- `3d_visualization_demo.html` - Interactive 3D view

#### Run:
```bash
python examples/3d_viz_demo.py
```

---

## AI Features Examples

### 13. `real_world_integration.py`
**Purpose**: Real-world AI features integration
**Size**: ~20KB
**Difficulty**: Advanced

#### What It Does:
- Demonstrates all AI features
- Shows real-world usage patterns
- Integrates multiple features
- Generates comprehensive report

#### Features Used:
- Trace comparison
- Regression detection
- Cost analysis
- Dependency analysis
- Refactoring suggestions
- Security analysis
- Load analysis

#### Run:
```bash
python examples/real_world_integration.py
```

---

### 14. `cli_comprehensive_demo.py`
**Purpose**: Comprehensive CLI demonstration
**Size**: ~8.7KB
**Difficulty**: Intermediate

#### What It Does:
- Shows all CLI commands
- Demonstrates CLI options
- Shows output formats
- Batch processing

#### Commands Shown:
```bash
# Trace collection
callflow-tracer trace script.py

# Report generation
callflow-tracer report trace.json

# Trace comparison
callflow-tracer compare trace1.json trace2.json

# Export formats
callflow-tracer export trace.json --format html
callflow-tracer export trace.json --format json
```

#### Run:
```bash
python examples/cli_comprehensive_demo.py
```

---

### 15. `new_examplew.py`
**Purpose**: New features demonstration
**Size**: ~9.3KB
**Difficulty**: Intermediate

#### What It Does:
- Demonstrates latest features
- Shows new capabilities
- Provides usage examples

#### Run:
```bash
python examples/new_examplew.py
```

---

## Integration Examples

### 16. `async_example.py`
**Purpose**: Asynchronous code tracing
**Size**: ~11KB
**Difficulty**: Intermediate

#### What It Does:
- Traces async/await code
- Shows coroutine tracking
- Demonstrates task correlation
- Analyzes concurrency

#### Features:
```python
from callflow_tracer.async_tracer import AsyncTracer

tracer = AsyncTracer()
tracer.start()

# Async code here
await my_async_function()

tracer.stop()
graph = tracer.get_graph()
```

#### Run:
```bash
python examples/async_example.py
```

---

### 17. `fast_apiexample.py`
**Purpose**: FastAPI integration
**Size**: ~6.3KB
**Difficulty**: Intermediate

#### What It Does:
- Integrates with FastAPI
- Traces HTTP requests
- Shows request/response flow
- Generates API performance report

#### Features:
- Request tracing
- Response time measurement
- Endpoint analysis
- Performance metrics

#### Run:
```bash
python examples/fast_apiexample.py
```

---

### 18. `sqlal_ex.py`
**Purpose**: SQLAlchemy integration
**Size**: ~2.7KB
**Difficulty**: Beginner

#### What It Does:
- Traces SQLAlchemy queries
- Shows database operations
- Measures query performance
- Detects N+1 queries

#### Run:
```bash
python examples/sqlal_ex.py
```

---

### 19. `jupyter_standalone_demo.py`
**Purpose**: Jupyter notebook integration
**Size**: ~12KB
**Difficulty**: Intermediate

#### What It Does:
- Demonstrates Jupyter integration
- Shows inline visualization
- Interactive widgets
- Notebook-specific features

#### Features:
- Inline tracing
- Interactive graphs
- Cell-level analysis
- Export to notebook

#### Run:
```bash
python examples/jupyter_standalone_demo.py
```

---

### 20. `jupyter_example.ipynb`
**Purpose**: Jupyter notebook example
**Size**: ~55KB
**Difficulty**: Intermediate

#### What It Does:
- Complete Jupyter notebook
- Interactive demonstrations
- Visualizations
- Step-by-step guide

#### Sections:
1. Basic tracing
2. Visualization
3. Analysis
4. Comparison
5. Export

#### Run:
```bash
jupyter notebook examples/jupyter_example.ipynb
```

---

## Specialized Examples

### 21. `cli_test_commands.sh` (Linux/Mac)
**Purpose**: CLI test commands
**Size**: ~3.4KB

#### Commands:
```bash
# Basic tracing
callflow-tracer trace example.py

# Report generation
callflow-tracer report trace.json

# Comparison
callflow-tracer compare trace1.json trace2.json

# Export
callflow-tracer export trace.json --format html
```

#### Run:
```bash
bash examples/cli_test_commands.sh
```

---

### 22. `cli_test_commands.bat` (Windows)
**Purpose**: CLI test commands for Windows
**Size**: ~3.3KB

#### Run:
```bash
examples\cli_test_commands.bat
```

---

### 23. `test_flamegraph_fixed.py`
**Purpose**: Flamegraph testing
**Size**: ~2.2KB
**Difficulty**: Beginner

#### What It Does:
- Tests flamegraph generation
- Validates output
- Checks visualization

#### Run:
```bash
python examples/test_flamegraph_fixed.py
```

---

## Generated Output Files

### HTML Visualizations

#### Flamegraph Examples:
- `flamegraph_1_simple.html` - Simple function
- `flamegraph_2_recursive.html` - Recursive calls
- `flamegraph_3_nested.html` - Nested functions
- `flamegraph_4_parallel.html` - Parallel execution
- `flamegraph_5_hotspots.html` - Performance hotspots
- `flamegraph_6_pipeline.html` - Data pipeline
- `flamegraph_7_algorithms.html` - Algorithm comparison

#### Comparison Examples:
- `comparison_example1_fibonacci.html`
- `comparison_example2_list_processing.html`
- `comparison_example3_caching.html`
- `comparison_example4_sorting.html`
- `comparison_example5_data_structures.html`
- `comparison_example6_realworld.html`

#### Demo Examples:
- `demo1_basic_tracing.html`
- `demo2_recursive_functions.html`
- `demo4_combined_analysis.html`
- `demo5_ml_pipeline.html`
- `demo6_nested_calls.html`

#### Memory Leak Examples:
- `memory_leak_example1_basic.html`
- `memory_leak_example3_cycles.html`
- `memory_leak_example6_cache.html`
- `memory_leak_example7_listeners.html`
- `memory_leak_example8_connections.html`
- `memory_leak_example9_closures.html`
- `memory_leak_example10_clean.html`

#### Advanced Layouts:
- `advanced_layouts_demo.html`
- `3d_visualization_demo.html`

#### Color Schemes:
- `flamegraph_color_default.html`
- `flamegraph_color_hot.html`
- `flamegraph_color_cool.html`
- `flamegraph_color_rainbow.html`
- `flamegraph_color_performance.html`

#### Feature Demos:
- `flamegraph_search_demo.html`
- `flamegraph_statistics_demo.html`
- `flamegraph_export_demo.html`
- `flamegraph_ultimate_demo.html`

---

## README Files

### Feature-Specific Documentation:

1. **ASYNC_COMPARISON_README.md**
   - Async code tracing
   - Comparison features
   - Best practices

2. **FLAMEGRAPH_README.md**
   - Flamegraph generation
   - Color schemes
   - Interactive features
   - Export options

3. **JUPYTER_README.md**
   - Jupyter integration
   - Interactive widgets
   - Notebook features
   - Export to notebook

---

## Quick Start Guide

### For Beginners:
1. Start with `profiling_example.py`
2. Try `cli_demo.py`
3. Explore `flamegraph_example.py`

### For Analysis:
1. Use `advanced_analysis_demo.py`
2. Try `comparison_example.py`
3. Explore `memory_leak_example.py`

### For Integration:
1. Check `async_example.py`
2. Try `fast_apiexample.py`
3. Explore `jupyter_example.ipynb`

### For AI Features:
1. Use `real_world_integration.py`
2. Try `comparison_example.py`
3. Explore `advanced_analysis_demo.py`

---

## Running Examples

### Basic Run:
```bash
python examples/profiling_example.py
```

### With Output:
```bash
python examples/flamegraph_example.py
# Generates: flamegraph_example.html
```

### With Comparison:
```bash
python examples/comparison_example.py
# Generates: comparison_example*.html
```

### In Jupyter:
```bash
jupyter notebook examples/jupyter_example.ipynb
```

---

## Example Categories

### By Difficulty:

**Beginner** (Start here):
- profiling_example.py
- simple_debug.py
- debug_test.py
- sqlal_ex.py
- test_flamegraph_fixed.py

**Intermediate** (Core features):
- flamegraph_example.py
- comparison_example.py
- memory_leak_example.py
- async_example.py
- quality_analysis_demo.py
- advanaced_layout_demo.py

**Advanced** (Complex scenarios):
- advanced_analysis_demo.py
- real_world_integration.py
- 3d_viz_demo.py
- flamegraph_enhanced_demo.py
- jupyter_standalone_demo.py

### By Purpose:

**Performance Analysis**:
- profiling_example.py
- flamegraph_example.py
- advanced_analysis_demo.py

**Comparison & Regression**:
- comparison_example.py
- advanced_analysis_demo.py

**Memory Analysis**:
- memory_leak_example.py
- advanced_analysis_demo.py

**Visualization**:
- flamegraph_example.py
- 3d_viz_demo.py
- advanaced_layout_demo.py
- flamegraph_enhanced_demo.py

**Integration**:
- async_example.py
- fast_apiexample.py
- jupyter_example.ipynb
- jupyter_standalone_demo.py

**CLI Usage**:
- cli_demo.py
- cli_comprehensive_demo.py
- cli_test_commands.sh/bat

---

## Output Structure

### Generated Files:
```
examples/
├── *.py (source files)
├── *.ipynb (Jupyter notebooks)
├── *.html (generated visualizations)
├── *.sh / *.bat (CLI scripts)
└── README files
```

### Typical Output:
```
flamegraph_example.html     # Interactive visualization
comparison_example1.html    # Comparison result
memory_leak_example1.html   # Memory analysis
3d_visualization_demo.html  # 3D view
```

---

## Tips & Tricks

### 1. Customize Visualization:
```python
from callflow_tracer import export_html

export_html(graph, 'output.html', 
    layout='circular',
    color_scheme='hot',
    show_stats=True
)
```

### 2. Compare Multiple Traces:
```python
from callflow_tracer.ai import compare_traces

result = compare_traces(baseline, current, threshold=0.1)
print(f"Regressions: {len(result['regressions'])}")
```

### 3. Analyze Performance:
```python
from callflow_tracer.code_quality import CodeQualityAnalyzer

analyzer = CodeQualityAnalyzer()
report = analyzer.analyze(graph)
print(f"Complexity: {report['avg_complexity']}")
```

### 4. Export Multiple Formats:
```python
from callflow_tracer import export_html, export_json

export_html(graph, 'output.html')
export_json(graph, 'output.json')
```

---

## Troubleshooting

### Issue: No output generated
- Check if trace was collected
- Verify graph structure
- Check file permissions

### Issue: Visualization not loading
- Check HTML file path
- Verify browser compatibility
- Check for JavaScript errors

### Issue: Memory issues
- Reduce sampling rate
- Use smaller traces
- Enable streaming export

---

## Summary

| Category | Count | Examples |
|----------|-------|----------|
| Basic | 4 | cli_demo, profiling, debug |
| Analysis | 4 | advanced_analysis, quality, comparison, memory |
| Visualization | 5 | flamegraph, 3d, layouts, enhanced |
| Integration | 5 | async, fastapi, sqlalchemy, jupyter |
| Specialized | 3 | CLI tests, flamegraph tests |
| **Total** | **21** | **Python scripts** |
| **HTML Outputs** | **50+** | **Generated visualizations** |

---

**All examples are production-ready and can be used as templates for your own analysis!**

