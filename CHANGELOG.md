# Changelog

All notable changes to CallFlow Tracer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.5] - 2025-10-24

### New Features
- **Enhanced FastAPI Integration**
  - Modern FastAPI example with production-ready patterns
  - Pydantic models for request/response validation
  - Comprehensive error handling and HTTP exception handlers
  - CORS middleware configuration
  - Health check endpoint
  - Multiple endpoint examples (CRUD, search, calculator)
  - Proper async/await patterns with lifespan management
  - Request/response logging middleware
  - OpenAPI documentation with detailed examples

### Framework Integrations
- **FastAPI Integration**: Enhanced with modern patterns, validation, and error handling
- **Flask Integration**: Middleware for automatic request tracing
- **Django Integration**: Middleware and decorators for Django views
- **SQLAlchemy Integration**: Database query tracing and performance monitoring
- **Psycopg2 Integration**: PostgreSQL query tracing with execution time tracking

### VSCode Extension
- **Interactive Visualization**: View call graphs directly in VS Code editor
- **One-Click Tracing**: Trace files or functions with a single command
- **3D Visualization**: Explore call graphs in 3D space
- **Multiple Layouts**: Hierarchical, force-directed, circular, and timeline layouts
- **Export Options**: PNG and JSON export from the editor
- **Performance Profiling**: Built-in CPU profiling integration
- **Module Filtering**: Filter visualizations by Python modules
- **Real-time Updates**: Automatic trace updates on file changes (optional)

### Examples
- Updated `fast_apiexample.py` with:
  - Modern lifespan management (replacing deprecated startup/shutdown events)
  - Pydantic models with validation
  - Multiple HTTP methods (GET, POST)
  - Query parameters and path parameters
  - Error handling with proper HTTP status codes
  - In-memory database example
  - Search functionality
  - Calculator endpoint for demonstration
  - Comprehensive docstrings and comments

### Improvements
- Better async/await support in FastAPI integration
- Improved error messages and logging
- Enhanced code organization and type hints
- Production-ready example patterns
- Better separation of concerns

### Documentation
- Updated README with framework integration examples
- Enhanced FastAPI example documentation
- Added usage examples for all integrations
- Improved installation instructions

### Compatibility
- Fully backward compatible with v0.2.4
- Python 3.8+ support maintained
- All existing features continue to work

---

## [0.2.4] - 2025-10-07

### New
- **Async/Await Tracing**
  - `@trace_async`, `trace_scope_async()` for async code
  - `gather_traced()` to track concurrent task execution
  - `AsyncCallGraph` and `get_async_stats()` for timeline and concurrency metrics
- **Comparison Mode**
  - `compare_graphs()` to compute before/after diffs
  - `export_comparison_html()` split-screen HTML with improvements/regressions
- **Memory Leak Detection**
  - `MemoryLeakDetector`, `detect_leaks()` context manager
  - `@track_allocations` decorator and `MemorySnapshot`
  - `find_reference_cycles()`, `get_memory_growth()`, `get_top_memory_consumers()`
  - Beautiful HTML leak reports with Chart.js (growth, type distribution, snapshots, recommendations)

### Improvements
- HTML UI/UX: Fixed module filtering (with smooth fit animation), corrected Circular/Timeline layouts, improved JSON export (no `network.getData()`), modern CPU profile panel (collapsible)
- Documentation: Added `docs/v0_2_4_features.md`, expanded `docs/API_DOCUMENTATION.md`, updated `docs/index.md`

### Internal
- Version bumped to `0.2.4` in `pyproject.toml` and `callflow_tracer/__init__.py`
- Added tests and examples for new features

### Compatibility
- Backward compatible. New features are additive and opt‑in.

---

## [0.2.3] - 2025-09-28

### Fixed
- Stability fixes in tracer core
- Hardened error handling in `CallTracer._trace_calls`
- Resolved conflicts between `@trace` decorator and `trace_scope`
- Improved caller detection and global state management

### Added
- Improved JSON export with richer metadata
- Better error handling in export functions

### Changed
- UI enhancements in HTML exporter
- Added collapsible CPU profiling section
- Implemented working module filter
- Restored Circular and Timeline layouts

---

## [0.2.2] - 2025-09-28

### Fixed
- Stability fixes in tracer core
- Hardened error handling in `CallTracer._trace_calls`
- Resolved conflicts between `@trace` decorator and `trace_scope`
- Improved caller detection and global state management

### Added
- Improved JSON export with richer metadata
- Better error handling in export functions

### Changed
- UI enhancements in HTML exporter
- Added collapsible CPU profiling section
- Implemented working module filter
- Restored Circular and Timeline layouts

---

## [0.2.0] - Earlier

### Added
- Performance profiling features
- Memory tracking with tracemalloc
- I/O wait time measurement
- Basic flamegraph support
- cProfile integration

### Changed
- Improved HTML visualization
- Better color coding for performance
- Enhanced tooltips

---

## [0.1.0] - Initial Release

### Added
- Basic function call tracing
- Call graph generation
- HTML export with vis.js
- JSON export
- Decorator and context manager API
- Interactive visualizations

---

## Feature Summary by Version

### Latest Version Features
- Enhanced flamegraph with statistics  
- 5 color schemes  
- Search functionality  
- SVG export  
- Jupyter integration  
- Magic commands  
- Fixed CPU profiling  
- Fixed module filtering  
- Fixed all layouts  
- Fixed JSON export  
- Modern UI  
- Responsive design  

### 0.2.2 Features
- Stable tracing  
- Better error handling  
- Improved exports  
- UI enhancements  

### 0.2.0 Features
- Performance profiling  
- Memory tracking  
- Basic flamegraph  
- cProfile integration  

### 0.1.0 Features
- Call tracing  
- Call graph  
- HTML/JSON export  
- Interactive viz  

---

## Migration Guide

### From 0.2.2 to Latest

#### No Breaking Changes!
All existing code continues to work. New features are opt-in.

#### New Features Available

**Enhanced Flamegraph**:
```python
# Old way (still works)
generate_flamegraph(graph, "output.html")

# New way (with all features)
generate_flamegraph(
    graph,
    "output.html",
    color_scheme="performance",  # NEW!
    show_stats=True,             # NEW!
    search_enabled=True          # NEW!
)
```

**Jupyter Integration**:
```python
# NEW! Use in Jupyter notebooks
from callflow_tracer.jupyter import display_callgraph

with trace_scope() as graph:
    my_function()

display_callgraph(graph.to_dict())
```

**Fixed Features**:
- CPU profiling now shows actual times (no code changes needed)
- Module filter now works (just use it in HTML)
- All layouts work (select in HTML)
- JSON export works (no code changes needed)

---

## Known Issues

### None Currently!

All major issues have been fixed in the latest version.

---

## Upcoming Features

### Planned for Next Release
- [ ] Comparison mode (compare two traces)
- [ ] Diff visualization
- [ ] Performance regression detection
- [ ] Custom color schemes
- [ ] More export formats (PDF, PNG)
- [ ] CLI tool
- [ ] Configuration file support
- [ ] Plugin system

### Under Consideration
- [ ] Real-time tracing
- [ ] Remote tracing
- [ ] Database storage
- [ ] Web dashboard
- [ ] Team collaboration features
- [ ] CI/CD integration
- [ ] Performance budgets
- [ ] Automated recommendations

---

## Contributing

We welcome contributions! See the main README for guidelines.

### Areas for Contribution
- New visualization layouts
- Additional color schemes
- Performance improvements
- Documentation improvements
- Bug fixes
- New features

---

## Acknowledgments

### Contributors
- Core team
- Community contributors
- Bug reporters
- Feature requesters

### Dependencies
- NetworkX - Graph operations
- vis.js - Interactive visualizations
- D3.js - Flamegraph rendering
- cProfile - CPU profiling
- tracemalloc - Memory tracking

---

*Last Updated: 2025-10-07*
