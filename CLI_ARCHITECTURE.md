# CallFlow Tracer CLI - Architecture

## Command Structure

```
callflow-tracer (or callflow)
│
├── trace              # Trace function calls
│   ├── --output, -o
│   ├── --format [html|json|both]
│   ├── --3d
│   ├── --title
│   ├── --include-args
│   └── --no-browser
│
├── flamegraph         # Generate flamegraph
│   ├── --output, -o
│   ├── --title
│   ├── --min-time
│   └── --no-browser
│
├── profile            # Performance profiling
│   ├── --output, -o
│   ├── --format [html|json|text]
│   ├── --memory
│   ├── --cpu
│   └── --no-browser
│
├── memory-leak        # Detect memory leaks
│   ├── --output, -o
│   ├── --threshold
│   ├── --interval
│   ├── --top
│   └── --no-browser
│
├── compare            # Compare two traces
│   ├── --output, -o
│   ├── --label1
│   ├── --label2
│   └── --no-browser
│
├── export             # Convert formats
│   ├── --output, -o (required)
│   ├── --format [html|json|3d] (required)
│   └── --title
│
└── info               # Show trace statistics
    └── --detailed
```

## Data Flow

```
┌─────────────────┐
│  User Command   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  CLI Parser     │  (argparse)
│  (cli.py)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Command Handler │  (_handle_trace, _handle_profile, etc.)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Execute Script  │  (with tracing enabled)
│ + Collect Data  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  CallGraph      │  (tracer.py)
│  Data Structure │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Exporter      │  (exporter.py, flamegraph.py, etc.)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Output File    │  (HTML, JSON, Text)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Browser/User   │  (optional auto-open)
└─────────────────┘
```

## Module Dependencies

```
cli.py
├── tracer.py
│   ├── CallGraph
│   ├── CallNode
│   ├── CallEdge
│   └── trace_scope
│
├── exporter.py
│   ├── export_html
│   ├── export_json
│   └── export_html_3d
│
├── flamegraph.py
│   └── generate_flamegraph
│
├── comparison.py
│   ├── compare_graphs
│   └── export_comparison_html
│
├── memory_leak_detector.py
│   ├── MemoryLeakDetector
│   └── get_top_memory_consumers
│
├── memory_leak_visualizer.py
│   └── generate_memory_leak_html
│
└── profiling.py
    └── get_memory_usage
```

## Command Workflow Examples

### 1. Trace Command Workflow

```
User: callflow trace script.py -o output.html
  │
  ├─► Parse arguments (script, output, format)
  │
  ├─► Prepare script execution environment
  │     └─► Set sys.argv with script arguments
  │
  ├─► Start trace_scope context
  │     └─► Enable Python trace function
  │
  ├─► Execute script
  │     └─► Collect call data in CallGraph
  │
  ├─► Export to HTML
  │     └─► Generate interactive visualization
  │
  ├─► Print summary statistics
  │
  └─► Open browser (unless --no-browser)
```

### 2. Flamegraph Command Workflow

```
User: callflow flamegraph script.py --min-time 5.0
  │
  ├─► Parse arguments
  │
  ├─► Execute script with tracing
  │     └─► Build CallGraph
  │
  ├─► Generate flamegraph
  │     ├─► Filter by min-time threshold
  │     ├─► Build hierarchical structure
  │     └─► Create interactive HTML
  │
  └─► Save and open result
```

### 3. Compare Command Workflow

```
User: callflow compare v1.json v2.json
  │
  ├─► Load first JSON trace
  │     └─► Reconstruct CallGraph
  │
  ├─► Load second JSON trace
  │     └─► Reconstruct CallGraph
  │
  ├─► Compare graphs
  │     ├─► Identify added nodes
  │     ├─► Identify removed nodes
  │     ├─► Identify changed nodes
  │     └─► Calculate differences
  │
  ├─► Generate comparison HTML
  │     └─► Side-by-side visualization
  │
  └─► Display summary statistics
```

## Class Structure

```
CallflowCLI
├── __init__()
│   └── _create_parser()
│
├── _create_parser()
│   ├── _add_trace_parser()
│   ├── _add_flamegraph_parser()
│   ├── _add_profile_parser()
│   ├── _add_memory_leak_parser()
│   ├── _add_compare_parser()
│   ├── _add_export_parser()
│   └── _add_info_parser()
│
├── run(args)
│   └── Route to appropriate handler
│
├── _handle_trace(args)
├── _handle_flamegraph(args)
├── _handle_profile(args)
├── _handle_memory_leak(args)
├── _handle_compare(args)
├── _handle_export(args)
├── _handle_info(args)
│
├── _execute_script(script_path, script_args)
├── _open_browser(filepath)
└── _load_graph_from_json(filepath)
```

## File Organization

```
callflow-tracer/
│
├── callflow_tracer/
│   ├── __init__.py           # Package exports
│   ├── cli.py                # CLI implementation ⭐ NEW
│   ├── tracer.py             # Core tracing
│   ├── exporter.py           # HTML/JSON export
│   ├── flamegraph.py         # Flamegraph generation
│   ├── comparison.py         # Graph comparison
│   ├── memory_leak_detector.py
│   ├── memory_leak_visualizer.py
│   └── profiling.py
│
├── examples/
│   ├── cli_demo.py           # Simple demo ⭐ NEW
│   ├── cli_comprehensive_demo.py  # Full demo ⭐ NEW
│   ├── cli_test_commands.sh  # Test script (Unix) ⭐ NEW
│   └── cli_test_commands.bat # Test script (Win) ⭐ NEW
│
├── setup.py                  # Entry points ⭐ UPDATED
├── CLI_README.md            # User guide ⭐ NEW
├── CLI_GUIDE.md             # Comprehensive docs ⭐ NEW
├── CLI_QUICKREF.md          # Quick reference ⭐ NEW
├── CLI_IMPLEMENTATION_SUMMARY.md  ⭐ NEW
└── CLI_ARCHITECTURE.md      # This file ⭐ NEW
```

## Entry Point Registration

```python
# In setup.py
entry_points={
    'console_scripts': [
        'callflow-tracer=callflow_tracer.cli:main',
        'callflow=callflow_tracer.cli:main',
    ],
}
```

When user runs `callflow-tracer`:
1. Python looks up entry point in installed packages
2. Finds `callflow_tracer.cli:main`
3. Imports `callflow_tracer.cli` module
4. Calls `main()` function
5. `main()` creates `CallflowCLI` instance and runs it

## Error Handling Strategy

```
User Command
    │
    ├─► Argument Parsing Error
    │   └─► Show usage help
    │
    ├─► File Not Found Error
    │   └─► User-friendly message
    │
    ├─► Script Execution Error
    │   ├─► Show error message
    │   └─► Print traceback (if --debug)
    │
    ├─► Export Error
    │   └─► Show error with context
    │
    └─► Success
        ├─► Show summary
        └─► Open browser (optional)
```

## Output Format Matrix

| Command | HTML | JSON | Text | 3D |
|---------|------|------|------|-----|
| trace | ✅ | ✅ | ❌ | ✅ |
| flamegraph | ✅ | ❌ | ❌ | ❌ |
| profile | ✅ | ✅ | ✅ | ❌ |
| memory-leak | ✅ | ❌ | ❌ | ❌ |
| compare | ✅ | ❌ | ❌ | ❌ |
| export | ✅ | ✅ | ❌ | ✅ |
| info | ❌ | ❌ | ✅ (stdout) | ❌ |

## Browser Integration

```
Generate Output File
    │
    ├─► Check --no-browser flag
    │   ├─► True: Skip browser
    │   └─► False: Continue
    │
    ├─► Get absolute file path
    │
    ├─► Open with webbrowser module
    │   └─► file:///absolute/path/to/file.html
    │
    └─► User sees visualization
```

## Script Argument Forwarding

```
User: callflow trace script.py arg1 arg2 --flag

CLI receives:
  script = "script.py"
  script_args = ["arg1", "arg2", "--flag"]

Before execution:
  original_argv = sys.argv
  sys.argv = ["script.py", "arg1", "arg2", "--flag"]

Execute script:
  script sees sys.argv as if run directly

After execution:
  sys.argv = original_argv
```

## Performance Considerations

1. **Script Execution**: Runs in same process, minimal overhead
2. **Tracing**: Uses Python's built-in trace mechanism
3. **Memory**: Graphs stored in memory during execution
4. **Export**: Streaming for large outputs (where applicable)
5. **Browser**: Non-blocking open in separate process

## Security Considerations

1. **Script Execution**: Runs with user's permissions
2. **File Paths**: Validated before use
3. **Argument Injection**: Properly escaped
4. **Output Files**: Created with user's umask
5. **No Remote Code**: All execution is local

## Testing Strategy

```
Unit Tests (Future)
├── Test argument parsing
├── Test each command handler
├── Test error handling
└── Test output generation

Integration Tests (Current)
├── cli_test_commands.sh
├── cli_test_commands.bat
└── Manual testing with examples

End-to-End Tests (Current)
├── Run on example scripts
├── Verify output files
└── Check browser opening
```

## Extension Points

Future developers can extend the CLI by:

1. **Adding New Commands**:
   ```python
   def _add_new_parser(self, subparsers):
       parser = subparsers.add_parser('new-command')
       # Add arguments
   
   def _handle_new(self, args):
       # Implementation
   ```

2. **Adding New Output Formats**:
   ```python
   if args.format == 'new-format':
       export_new_format(graph, args.output)
   ```

3. **Adding New Options**:
   ```python
   parser.add_argument('--new-option', help='...')
   ```

## Summary

The CLI architecture is:
- ✅ **Modular**: Each command is independent
- ✅ **Extensible**: Easy to add new commands
- ✅ **Robust**: Comprehensive error handling
- ✅ **User-friendly**: Clear help and feedback
- ✅ **Cross-platform**: Works everywhere Python does
- ✅ **Well-documented**: Multiple documentation levels
- ✅ **Testable**: Example scripts and test suites
