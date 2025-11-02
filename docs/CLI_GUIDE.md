# Command-Line Interface (CLI) Guide

Complete documentation for the CallFlow Tracer CLI module.

**Location**: `callflow_tracer/cli.py` (850 lines)

---

## Overview

The CLI provides a comprehensive command-line interface for all CallFlow Tracer features without writing Python code.

## Available Commands

### 1. trace - Trace Function Calls
```bash
callflow-tracer trace script.py -o output.html
callflow-tracer trace script.py arg1 arg2 --3d --title "My Trace"
```

**Options**:
- `script` - Python script to trace
- `script_args` - Arguments to pass to script
- `-o, --output` - Output file (default: `callflow_trace.html`)
- `--format` - Format: `html`, `json`, `both` (default: `html`)
- `--3d` - Generate 3D visualization
- `--title` - Custom title
- `--include-args` - Include function arguments
- `--no-browser` - Don't open browser

### 2. flamegraph - Generate Flamegraph
```bash
callflow-tracer flamegraph script.py -o flamegraph.html
callflow-tracer flamegraph script.py --min-time 0.5 --title "Performance"
```

**Options**:
- `script` - Python script
- `-o, --output` - Output file (default: `flamegraph.html`)
- `--title` - Custom title
- `--min-time` - Minimum time threshold (ms)
- `--no-browser` - Don't open browser

### 3. profile - Profile Performance
```bash
callflow-tracer profile script.py -o profile.html
callflow-tracer profile script.py --memory --cpu --format json
```

**Options**:
- `script` - Python script
- `-o, --output` - Output file (default: `profile.html`)
- `--format` - Format: `html`, `json`, `text` (default: `html`)
- `--memory` - Include memory profiling
- `--cpu` - Include CPU profiling
- `--no-browser` - Don't open browser

### 4. memory-leak - Detect Memory Leaks
```bash
callflow-tracer memory-leak script.py -o report.html
callflow-tracer memory-leak script.py --threshold 10 --top 20
```

**Options**:
- `script` - Python script
- `-o, --output` - Output file (default: `memory_leak_report.html`)
- `--threshold` - Memory growth threshold (MB)
- `--interval` - Sampling interval (seconds)
- `--top` - Top memory consumers (default: 10)
- `--no-browser` - Don't open browser

### 5. compare - Compare Traces
```bash
callflow-tracer compare trace1.json trace2.json -o comparison.html
callflow-tracer compare trace1.json trace2.json --label1 "Before" --label2 "After"
```

**Options**:
- `file1` - First trace file (JSON)
- `file2` - Second trace file (JSON)
- `-o, --output` - Output file (default: `comparison.html`)
- `--label1` - Label for first trace
- `--label2` - Label for second trace
- `--no-browser` - Don't open browser

### 6. export - Export Traces
```bash
callflow-tracer export trace.json -o output.html --format html
callflow-tracer export trace.json -o output.html --format 3d
```

**Options**:
- `input` - Input trace file (JSON)
- `-o, --output` - Output file (required)
- `--format` - Format: `html`, `json`, `3d` (required)
- `--title` - Custom title

### 7. info - Show Trace Information
```bash
callflow-tracer info trace.json
callflow-tracer info trace.json --detailed
```

**Options**:
- `file` - Trace file (JSON)
- `--detailed` - Show detailed statistics

### 8. quality - Analyze Code Quality
```bash
callflow-tracer quality . -o quality_report.html
callflow-tracer quality . --track-trends --format json
```

**Options**:
- `directory` - Directory to analyze (default: current)
- `-o, --output` - Output file (default: `quality_report.html`)
- `--format` - Format: `html`, `json` (default: `html`)
- `--track-trends` - Track trends over time
- `--no-browser` - Don't open browser

### 9. predict - Predict Performance Issues
```bash
callflow-tracer predict history.json -o predictions.html
callflow-tracer predict history.json --format json
```

**Options**:
- `trace_history` - JSON file with trace history
- `-o, --output` - Output file (default: `predictions.html`)
- `--format` - Format: `html`, `json` (default: `html`)
- `--no-browser` - Don't open browser

### 10. churn - Analyze Code Churn
```bash
callflow-tracer churn . -o churn_report.html
callflow-tracer churn . --days 90 --format json
```

**Options**:
- `directory` - Repository directory (default: current)
- `-o, --output` - Output file (default: `churn_report.html`)
- `--days` - Days of history (default: 90)
- `--format` - Format: `html`, `json` (default: `html`)
- `--no-browser` - Don't open browser

## Usage Examples

### Basic Tracing
```bash
callflow-tracer trace my_script.py -o my_trace.html
```

### Flamegraph with Title
```bash
callflow-tracer flamegraph my_script.py --title "Performance Analysis" -o perf.html
```

### Memory Leak Detection
```bash
callflow-tracer memory-leak my_script.py --threshold 10 --top 15
```

### Compare Two Traces
```bash
callflow-tracer compare before.json after.json --label1 "Before" --label2 "After"
```

### Quality Analysis
```bash
callflow-tracer quality ./src --track-trends --format html
```

### Predictive Analysis
```bash
callflow-tracer predict trace_history.json --format html
```

### Code Churn Analysis
```bash
callflow-tracer churn . --days 180 --format html
```

## Exit Codes

- `0` - Success
- `1` - Error (see stderr for details)

## Environment Variables

- `CALLFLOW_OUTPUT_DIR` - Default output directory
- `CALLFLOW_NO_BROWSER` - Set to 1 to disable browser auto-open
