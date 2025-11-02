# CallFlow Tracer - Command Line Interface

A powerful command-line interface for tracing, profiling, and visualizing Python function calls.

## 🚀 Quick Start

### Installation

```bash
pip install callflow-tracer
```

After installation, the CLI is available via:
```bash
callflow-tracer [command] [options]
# or use the shorter alias:
callflow [command] [options]
```

### Your First Trace

```bash
# Trace any Python script
callflow-tracer trace your_script.py

# This will:
# 1. Execute your script
# 2. Trace all function calls
# 3. Generate an interactive HTML visualization
# 4. Open it in your browser
```

## 📋 Available Commands

| Command | Description |
|---------|-------------|
| **trace** | Trace function calls and generate visualizations |
| **flamegraph** | Generate flamegraph showing execution time hierarchy |
| **profile** | Comprehensive performance profiling (CPU + memory) |
| **memory-leak** | Detect memory leaks and excessive memory usage |
| **compare** | Compare two trace files side-by-side |
| **export** | Convert trace files between formats |
| **info** | Display statistics about a trace file |

## 💡 Common Use Cases

### 1. Understand Code Flow
```bash
# Generate interactive call graph
callflow-tracer trace my_app.py -o callgraph.html
```

### 2. Find Performance Bottlenecks
```bash
# Generate flamegraph to identify slow functions
callflow-tracer flamegraph my_app.py

# Or use full profiling
callflow-tracer profile my_app.py --memory --cpu
```

### 3. Detect Memory Leaks
```bash
# Monitor memory usage and detect leaks
callflow-tracer memory-leak my_app.py --threshold 10
```

### 4. Compare Before/After Optimization
```bash
# Before optimization
callflow-tracer trace my_app.py --format json -o before.json

# ... make your optimizations ...

# After optimization
callflow-tracer trace my_app.py --format json -o after.json

# Compare the results
callflow-tracer compare before.json after.json
```

### 5. Quick Analysis
```bash
# Get quick stats about a trace
callflow-tracer info trace.json --detailed
```

## 🎯 Command Examples

### Trace Command

```bash
# Basic trace
callflow-tracer trace script.py

# Trace with custom output
callflow-tracer trace script.py -o my_trace.html

# Generate JSON for later analysis
callflow-tracer trace script.py --format json -o trace.json

# 3D visualization
callflow-tracer trace script.py --3d

# Pass arguments to your script
callflow-tracer trace script.py arg1 arg2 --flag

# Include function arguments in trace
callflow-tracer trace script.py --include-args
```

### Flamegraph Command

```bash
# Basic flamegraph
callflow-tracer flamegraph script.py

# Filter out fast functions (< 5ms)
callflow-tracer flamegraph script.py --min-time 5.0

# Custom output and title
callflow-tracer flamegraph script.py -o perf.html --title "Performance Analysis"
```

### Profile Command

```bash
# Basic profiling
callflow-tracer profile script.py

# Include memory profiling
callflow-tracer profile script.py --memory

# Full profiling (CPU + memory)
callflow-tracer profile script.py --memory --cpu

# Export as JSON
callflow-tracer profile script.py --format json -o profile.json

# Export as text report
callflow-tracer profile script.py --format text -o profile.txt
```

### Memory Leak Command

```bash
# Basic memory leak detection
callflow-tracer memory-leak script.py

# Custom threshold (alert if memory grows > 20MB)
callflow-tracer memory-leak script.py --threshold 20

# Faster sampling (every 50ms)
callflow-tracer memory-leak script.py --interval 0.05

# Show top 20 memory consumers
callflow-tracer memory-leak script.py --top 20
```

### Compare Command

```bash
# Compare two traces
callflow-tracer compare trace1.json trace2.json

# With custom labels
callflow-tracer compare old.json new.json \
  --label1 "Version 1.0" \
  --label2 "Version 2.0"

# Custom output location
callflow-tracer compare before.json after.json -o results/comparison.html
```

### Export Command

```bash
# Convert JSON to HTML
callflow-tracer export trace.json -o trace.html --format html

# Convert to 3D visualization
callflow-tracer export trace.json -o trace_3d.html --format 3d

# Re-export with custom title
callflow-tracer export trace.json -o new.html --format html --title "My Analysis"
```

### Info Command

```bash
# Basic info
callflow-tracer info trace.json

# Detailed statistics
callflow-tracer info trace.json --detailed
```

## 🔧 Common Options

Most commands support these options:

- `-o, --output FILE` - Specify output file path
- `--format FORMAT` - Choose output format (html/json/text/3d)
- `--title TITLE` - Set custom title for visualization
- `--no-browser` - Don't automatically open browser
- `--help` - Show command-specific help

## 📊 Output Formats

### HTML (Default)
- Interactive visualization
- Click nodes to see details
- Multiple layout options
- Export capabilities
- Best for: Exploration and presentation

### JSON
- Machine-readable format
- Enables comparison
- Can be re-exported to other formats
- Best for: Automation and analysis

### 3D
- Three-dimensional graph visualization
- Interactive rotation and zoom
- Best for: Complex call graphs

### Text
- Simple text reports
- Easy to read in terminal
- Best for: Quick checks and CI/CD

## 🎓 Complete Workflows

### Performance Optimization Workflow

```bash
# 1. Understand the code flow
callflow-tracer trace app.py -o flow.html

# 2. Identify bottlenecks
callflow-tracer flamegraph app.py -o hotspots.html

# 3. Deep dive with profiling
callflow-tracer profile app.py --memory --cpu -o profile.html

# 4. Check for memory issues
callflow-tracer memory-leak app.py --threshold 10

# 5. Make optimizations...

# 6. Compare before/after
callflow-tracer trace app.py --format json -o after.json
callflow-tracer compare before.json after.json
```

### CI/CD Integration Workflow

```bash
# In your CI pipeline:

# 1. Generate trace
callflow-tracer trace tests/performance_test.py --format json -o current.json

# 2. Compare with baseline
callflow-tracer compare baseline.json current.json -o report.html

# 3. Get statistics
callflow-tracer info current.json --detailed > stats.txt

# 4. Archive results
# Upload report.html and stats.txt as artifacts
```

### Debugging Workflow

```bash
# 1. Trace with arguments included
callflow-tracer trace buggy_script.py --include-args -o debug_trace.html

# 2. Check memory usage
callflow-tracer memory-leak buggy_script.py --threshold 5

# 3. Profile to find slow sections
callflow-tracer profile buggy_script.py --memory -o debug_profile.html
```

## 🐛 Troubleshooting

### Command not found
```bash
# Reinstall the package
pip install --upgrade --force-reinstall callflow-tracer

# Verify installation
callflow-tracer --version
```

### Script fails to execute
```bash
# First test your script runs normally
python script.py

# Then trace it
callflow-tracer trace script.py
```

### Large output files
```bash
# Use JSON format and convert selectively
callflow-tracer trace script.py --format json -o trace.json
callflow-tracer info trace.json --detailed  # Check size first
callflow-tracer export trace.json -o trace.html --format html  # Convert if needed
```

### Memory leak false positives
```bash
# Increase threshold
callflow-tracer memory-leak script.py --threshold 20

# Adjust sampling interval
callflow-tracer memory-leak script.py --interval 0.5
```

## 📚 Documentation

- **Quick Reference**: See `CLI_QUICKREF.md` for a one-page cheat sheet
- **Full Guide**: See `CLI_GUIDE.md` for comprehensive documentation
- **Examples**: Check the `examples/` directory for demo scripts
- **GitHub**: https://github.com/rajveer43/callflow-tracer

## 🧪 Testing the CLI

We provide test scripts to verify all CLI features:

**Linux/Mac:**
```bash
cd examples
chmod +x cli_test_commands.sh
./cli_test_commands.sh
```

**Windows:**
```cmd
cd examples
cli_test_commands.bat
```

## 💻 Programmatic Usage

You can also use the CLI programmatically:

```python
from callflow_tracer.cli import CallflowCLI

cli = CallflowCLI()
exit_code = cli.run(['trace', 'script.py', '-o', 'output.html'])
```

## 🤝 Contributing

Found a bug or have a feature request? Please open an issue on GitHub!

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Support

- **Issues**: https://github.com/rajveer43/callflow-tracer/issues
- **Discussions**: https://github.com/rajveer43/callflow-tracer/discussions
- **Email**: rathodrajveer1311@gmail.com

---

**Happy Tracing! 🚀**
