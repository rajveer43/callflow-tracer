# CallFlow Tracer - Command Line Interface Guide

## Installation

After installing the package, the CLI is available via two commands:
```bash
callflow-tracer [command] [options]
# or shorter alias:
callflow [command] [options]
```

## Available Commands

### 1. `trace` - Trace Function Calls

Execute a Python script and trace all function calls, generating interactive visualizations.

**Basic Usage:**
```bash
callflow-tracer trace script.py -o output.html
```

**Options:**
- `script` - Python script to trace (required)
- `script_args` - Arguments to pass to the script
- `-o, --output` - Output file path (default: callflow_trace.html)
- `--format` - Output format: html, json, or both (default: html)
- `--3d` - Generate 3D visualization
- `--title` - Custom title for the visualization
- `--include-args` - Include function arguments in trace
- `--no-browser` - Don't open browser after generating HTML

**Examples:**
```bash
# Basic trace with HTML output
callflow-tracer trace my_script.py

# Trace with custom output and title
callflow-tracer trace my_script.py -o my_trace.html --title "My Application Flow"

# Generate both HTML and JSON
callflow-tracer trace my_script.py --format both -o trace

# 3D visualization
callflow-tracer trace my_script.py --3d -o trace_3d.html

# Trace script with arguments
callflow-tracer trace my_script.py arg1 arg2 --flag

# Include function arguments in trace
callflow-tracer trace my_script.py --include-args
```

---

### 2. `flamegraph` - Generate Flamegraph

Create a flamegraph visualization showing function execution time hierarchy.

**Basic Usage:**
```bash
callflow-tracer flamegraph script.py -o flamegraph.html
```

**Options:**
- `script` - Python script to trace (required)
- `script_args` - Arguments to pass to the script
- `-o, --output` - Output HTML file path (default: flamegraph.html)
- `--title` - Custom title for the flamegraph
- `--min-time` - Minimum time threshold in milliseconds (default: 0.0)
- `--no-browser` - Don't open browser after generating HTML

**Examples:**
```bash
# Basic flamegraph
callflow-tracer flamegraph my_script.py

# Filter out fast functions (< 5ms)
callflow-tracer flamegraph my_script.py --min-time 5.0

# Custom title
callflow-tracer flamegraph my_script.py --title "Performance Analysis"

# Flamegraph with script arguments
callflow-tracer flamegraph my_script.py --input data.csv --verbose
```

---

### 3. `profile` - Performance Profiling

Execute a script with comprehensive performance profiling including CPU and memory analysis.

**Basic Usage:**
```bash
callflow-tracer profile script.py -o profile.html
```

**Options:**
- `script` - Python script to profile (required)
- `script_args` - Arguments to pass to the script
- `-o, --output` - Output file path (default: profile.html)
- `--format` - Output format: html, json, or text (default: html)
- `--memory` - Include memory profiling
- `--cpu` - Include CPU profiling
- `--no-browser` - Don't open browser after generating HTML

**Examples:**
```bash
# Basic profiling
callflow-tracer profile my_script.py

# Profile with memory analysis
callflow-tracer profile my_script.py --memory

# Profile with both CPU and memory
callflow-tracer profile my_script.py --memory --cpu

# Export as JSON
callflow-tracer profile my_script.py --format json -o profile.json

# Export as plain text
callflow-tracer profile my_script.py --format text -o profile.txt

# Profile script with arguments
callflow-tracer profile my_script.py --config config.json --verbose
```

---

### 4. `memory-leak` - Detect Memory Leaks

Analyze a script for potential memory leaks and excessive memory consumption.

**Basic Usage:**
```bash
callflow-tracer memory-leak script.py
```

**Options:**
- `script` - Python script to analyze (required)
- `script_args` - Arguments to pass to the script
- `-o, --output` - Output file path (default: memory_leak_report.html)
- `--threshold` - Memory growth threshold in MB (default: 5.0)
- `--interval` - Sampling interval in seconds (default: 0.1)
- `--top` - Number of top memory consumers to show (default: 10)
- `--no-browser` - Don't open browser after generating HTML

**Examples:**
```bash
# Basic memory leak detection
callflow-tracer memory-leak my_script.py

# Custom threshold (alert if memory grows > 10MB)
callflow-tracer memory-leak my_script.py --threshold 10

# Faster sampling (every 50ms)
callflow-tracer memory-leak my_script.py --interval 0.05

# Show top 20 memory consumers
callflow-tracer memory-leak my_script.py --top 20

# Analyze long-running script
callflow-tracer memory-leak server.py --threshold 50 --interval 1.0
```

---

### 5. `compare` - Compare Trace Files

Compare two trace files to identify differences in execution patterns and performance.

**Basic Usage:**
```bash
callflow-tracer compare trace1.json trace2.json -o comparison.html
```

**Options:**
- `file1` - First trace file (JSON) (required)
- `file2` - Second trace file (JSON) (required)
- `-o, --output` - Output HTML file path (default: comparison.html)
- `--label1` - Label for first trace (default: "Trace 1")
- `--label2` - Label for second trace (default: "Trace 2")
- `--no-browser` - Don't open browser after generating HTML

**Examples:**
```bash
# Basic comparison
callflow-tracer compare before.json after.json

# Custom labels
callflow-tracer compare v1.json v2.json --label1 "Version 1.0" --label2 "Version 2.0"

# Compare optimization results
callflow-tracer compare baseline.json optimized.json \
  --label1 "Baseline" \
  --label2 "Optimized" \
  -o optimization_comparison.html
```

**Workflow Example:**
```bash
# 1. Generate baseline trace
callflow-tracer trace my_script.py --format json -o baseline.json

# 2. Make code changes...

# 3. Generate new trace
callflow-tracer trace my_script.py --format json -o optimized.json

# 4. Compare
callflow-tracer compare baseline.json optimized.json
```

---

### 6. `export` - Convert Trace Formats

Convert trace files between different formats.

**Basic Usage:**
```bash
callflow-tracer export input.json -o output.html --format html
```

**Options:**
- `input` - Input trace file (JSON) (required)
- `-o, --output` - Output file path (required)
- `--format` - Output format: html, json, or 3d (required)
- `--title` - Custom title for the visualization

**Examples:**
```bash
# Convert JSON to HTML
callflow-tracer export trace.json -o trace.html --format html

# Convert to 3D visualization
callflow-tracer export trace.json -o trace_3d.html --format 3d

# Re-export JSON with custom title
callflow-tracer export old_trace.json -o new_trace.json --format json --title "Updated Trace"
```

---

### 7. `info` - Trace File Information

Display statistics and information about a trace file.

**Basic Usage:**
```bash
callflow-tracer info trace.json
```

**Options:**
- `file` - Trace file to analyze (JSON) (required)
- `--detailed` - Show detailed statistics including top functions and modules

**Examples:**
```bash
# Basic info
callflow-tracer info trace.json

# Detailed statistics
callflow-tracer info trace.json --detailed
```

**Output Example:**
```
=== Trace Information ===
File: trace.json
Total nodes: 45
Total edges: 67
Total function calls: 1234
Total execution time: 2.456789s

=== Top 10 Functions by Time ===
1. main.process_data
   Calls: 100, Time: 1.234567s
2. utils.calculate
   Calls: 500, Time: 0.567890s
...

=== Module Statistics ===
main: 15 functions, 1.500000s
utils: 20 functions, 0.800000s
helpers: 10 functions, 0.156789s
```

---

## Complete Workflow Examples

### Example 1: Performance Analysis Workflow

```bash
# 1. Initial trace to understand call flow
callflow-tracer trace my_app.py -o initial_trace.html

# 2. Generate flamegraph to identify hotspots
callflow-tracer flamegraph my_app.py -o hotspots.html

# 3. Detailed profiling
callflow-tracer profile my_app.py --memory --cpu -o profile.html

# 4. Check for memory leaks
callflow-tracer memory-leak my_app.py --threshold 10
```

### Example 2: Before/After Optimization

```bash
# Before optimization
callflow-tracer trace my_app.py --format json -o before.json
callflow-tracer profile my_app.py -o before_profile.html

# ... make optimizations ...

# After optimization
callflow-tracer trace my_app.py --format json -o after.json
callflow-tracer profile my_app.py -o after_profile.html

# Compare results
callflow-tracer compare before.json after.json \
  --label1 "Before" \
  --label2 "After" \
  -o optimization_results.html
```

### Example 3: Debugging Memory Issues

```bash
# 1. Run with memory leak detection
callflow-tracer memory-leak problematic_script.py \
  --threshold 5 \
  --interval 0.1 \
  --top 20 \
  -o memory_report.html

# 2. Profile to see memory usage patterns
callflow-tracer profile problematic_script.py \
  --memory \
  -o memory_profile.html

# 3. Trace to understand call patterns
callflow-tracer trace problematic_script.py \
  --include-args \
  -o call_trace.html
```

### Example 4: API Performance Testing

```bash
# Test different scenarios
callflow-tracer trace api_test.py light_load --format json -o light.json
callflow-tracer trace api_test.py heavy_load --format json -o heavy.json

# Compare performance
callflow-tracer compare light.json heavy.json \
  --label1 "Light Load" \
  --label2 "Heavy Load"

# Generate flamegraphs for both
callflow-tracer flamegraph api_test.py light_load -o light_flame.html
callflow-tracer flamegraph api_test.py heavy_load -o heavy_flame.html
```

---

## Tips and Best Practices

### 1. **Use JSON format for comparison workflows**
```bash
# Always use --format json when you plan to compare traces
callflow-tracer trace script.py --format json -o trace.json
```

### 2. **Combine with script arguments**
```bash
# Pass any arguments your script needs
callflow-tracer trace my_script.py --input data.csv --verbose --workers 4
```

### 3. **Filter flamegraphs for clarity**
```bash
# Use --min-time to focus on significant functions
callflow-tracer flamegraph script.py --min-time 10.0  # Only show functions > 10ms
```

### 4. **Memory leak detection for long-running processes**
```bash
# Adjust threshold and interval for your use case
callflow-tracer memory-leak server.py --threshold 100 --interval 1.0
```

### 5. **Quick info check**
```bash
# Before opening large HTML files, check the trace info
callflow-tracer info trace.json --detailed
```

### 6. **Batch processing**
```bash
# Process multiple scripts
for script in tests/*.py; do
    callflow-tracer trace "$script" -o "traces/$(basename $script .py).html"
done
```

---

## Environment Variables

You can set these environment variables to customize behavior:

```bash
# Disable automatic browser opening globally
export CALLFLOW_NO_BROWSER=1

# Set default output directory
export CALLFLOW_OUTPUT_DIR=./traces
```

---

## Troubleshooting

### Issue: "Command not found"
**Solution:** Reinstall the package:
```bash
pip install --upgrade --force-reinstall callflow-tracer
```

### Issue: Script fails to execute
**Solution:** Ensure the script runs normally first:
```bash
python script.py  # Test without tracing
callflow-tracer trace script.py  # Then trace
```

### Issue: Large HTML files
**Solution:** Use JSON format and convert selectively:
```bash
callflow-tracer trace script.py --format json -o trace.json
callflow-tracer export trace.json -o trace.html --format html
```

### Issue: Memory leak detection shows false positives
**Solution:** Adjust the threshold:
```bash
callflow-tracer memory-leak script.py --threshold 20  # Increase threshold
```

---

## Getting Help

```bash
# General help
callflow-tracer --help

# Command-specific help
callflow-tracer trace --help
callflow-tracer flamegraph --help
callflow-tracer profile --help
callflow-tracer memory-leak --help
callflow-tracer compare --help
callflow-tracer export --help
callflow-tracer info --help

# Version information
callflow-tracer --version
```

---

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Performance Testing

on: [push, pull_request]

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install callflow-tracer
          pip install -r requirements.txt
      
      - name: Run performance tests
        run: |
          callflow-tracer trace tests/performance_test.py --format json -o current.json
          
      - name: Compare with baseline
        if: github.event_name == 'pull_request'
        run: |
          curl -o baseline.json https://example.com/baseline.json
          callflow-tracer compare baseline.json current.json -o comparison.html
          
      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: performance-results
          path: |
            current.json
            comparison.html
```

---

## Advanced Usage

### Custom Scripts Integration

You can also use the CLI programmatically:

```python
from callflow_tracer.cli import CallflowCLI

cli = CallflowCLI()
exit_code = cli.run(['trace', 'script.py', '-o', 'output.html'])
```

### Combining with Other Tools

```bash
# Combine with pytest
callflow-tracer trace -m pytest tests/ -o test_trace.html

# Profile specific test
callflow-tracer profile -m pytest tests/test_slow.py -o slow_test_profile.html

# Memory leak detection in tests
callflow-tracer memory-leak -m pytest tests/test_memory.py
```

---

For more information and updates, visit:
- GitHub: https://github.com/rajveer43/callflow-tracer
- Documentation: https://github.com/rajveer43/callflow-tracer/wiki
- Issues: https://github.com/rajveer43/callflow-tracer/issues
