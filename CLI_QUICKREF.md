# CallFlow Tracer CLI - Quick Reference

## Installation
```bash
pip install callflow-tracer
```

## Commands Overview

| Command | Purpose | Example |
|---------|---------|---------|
| `trace` | Trace function calls | `callflow trace script.py -o output.html` |
| `flamegraph` | Generate flamegraph | `callflow flamegraph script.py` |
| `profile` | Performance profiling | `callflow profile script.py --memory` |
| `memory-leak` | Detect memory leaks | `callflow memory-leak script.py --threshold 10` |
| `compare` | Compare two traces | `callflow compare v1.json v2.json` |
| `export` | Convert formats | `callflow export trace.json -o out.html --format html` |
| `info` | Show trace stats | `callflow info trace.json --detailed` |

## Common Options

- `-o, --output FILE` - Output file path
- `--format FORMAT` - Output format (html/json/text/3d)
- `--title TITLE` - Custom title
- `--no-browser` - Don't open browser
- `--help` - Show help

## Quick Examples

### Basic Tracing
```bash
# HTML visualization
callflow trace script.py

# JSON output
callflow trace script.py --format json -o trace.json

# 3D visualization
callflow trace script.py --3d

# With script arguments
callflow trace script.py arg1 arg2 --flag
```

### Performance Analysis
```bash
# Flamegraph
callflow flamegraph script.py

# Full profiling
callflow profile script.py --memory --cpu

# Memory leak detection
callflow memory-leak script.py --threshold 5
```

### Comparison Workflow
```bash
# 1. Baseline
callflow trace script.py --format json -o before.json

# 2. After changes
callflow trace script.py --format json -o after.json

# 3. Compare
callflow compare before.json after.json --label1 "Before" --label2 "After"
```

### Information & Export
```bash
# Show trace info
callflow info trace.json --detailed

# Convert JSON to HTML
callflow export trace.json -o trace.html --format html

# Convert to 3D
callflow export trace.json -o trace3d.html --format 3d
```

## Common Patterns

### Debug Performance Issues
```bash
callflow flamegraph script.py --min-time 5.0
callflow profile script.py --memory --cpu
```

### Monitor Memory
```bash
callflow memory-leak script.py --threshold 10 --interval 0.1 --top 20
```

### A/B Testing
```bash
callflow trace script.py scenario_a --format json -o a.json
callflow trace script.py scenario_b --format json -o b.json
callflow compare a.json b.json --label1 "Scenario A" --label2 "Scenario B"
```

### CI/CD Integration
```bash
# Generate baseline
callflow trace tests/perf_test.py --format json -o baseline.json

# In CI: compare with baseline
callflow trace tests/perf_test.py --format json -o current.json
callflow compare baseline.json current.json -o report.html
```

## Aliases

Both commands work identically:
```bash
callflow-tracer trace script.py
callflow trace script.py  # Shorter alias
```

## Help

```bash
callflow --help                    # General help
callflow trace --help              # Command help
callflow --version                 # Version info
```

## Output Files

| Format | Extension | Use Case |
|--------|-----------|----------|
| HTML | `.html` | Interactive visualization |
| JSON | `.json` | Comparison, export, analysis |
| Text | `.txt` | Simple reports |
| 3D | `.html` | 3D graph visualization |

## Tips

1. **Use JSON for workflows**: `--format json` enables comparison
2. **Filter flamegraphs**: `--min-time 10` shows only slow functions
3. **Adjust thresholds**: `--threshold 20` for memory leak detection
4. **Check info first**: `callflow info trace.json` before opening large files
5. **Pass script args**: Everything after script name goes to your script

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Command not found | `pip install --upgrade --force-reinstall callflow-tracer` |
| Script fails | Test with `python script.py` first |
| Large files | Use JSON format, convert selectively |
| False positives | Adjust `--threshold` for memory leak detection |

---

**Full Documentation**: See `CLI_GUIDE.md`
**GitHub**: https://github.com/rajveer43/callflow-tracer
