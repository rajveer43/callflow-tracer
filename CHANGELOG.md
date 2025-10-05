# Changelog

All notable changes to CallFlow Tracer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Latest] - 2025-10-05

### 🎉 Major Features Added

#### Enhanced Flamegraph Visualization
- **Statistics Panel**: Comprehensive metrics dashboard
  - Total functions, calls, execution time
  - Average time per call
  - Call depth visualization
  - Slowest function identification (bottleneck!)
  - Most called function tracking
  
- **5 Color Schemes**: Choose the best view for your analysis
  - `default`: Red-Yellow-Green gradient
  - `hot`: Red-Orange (highlights hot spots)
  - `cool`: Blue-Green (easy on eyes)
  - `rainbow`: Full spectrum
  - `performance`: Green=fast, Red=slow (RECOMMENDED!)

- **Search Functionality**: Find functions quickly
  - Real-time search box
  - Highlights matching functions
  - Case-insensitive search
  - Clear button to reset

- **SVG Export**: High-quality vector graphics
  - One-click export
  - Perfect for presentations
  - Preserves all colors and details

- **Modern UI**: Professional and responsive
  - Gradient backgrounds
  - Smooth animations
  - Hover effects
  - Mobile-friendly design

- **Optimization Tips**: Built-in guidance
  - How to read flamegraphs
  - What to look for
  - Performance optimization tips

#### Jupyter Notebook Integration
- **Magic Commands**:
  - `%callflow_trace` - Line magic for single lines
  - `%%callflow_cell_trace` - Cell magic for entire cells

- **Inline Visualization**:
  - `display_callgraph()` - Display interactive graphs in notebooks
  - Custom dimensions and layouts
  - Full interactivity

- **Full Feature Support**:
  - All tracing features work in Jupyter
  - Profiling integration
  - Export capabilities

### 🐛 Critical Fixes

#### CPU Profiling Fix
- **Problem**: CPU profile always showed 0.000s execution time, 0 function calls, 0 hot spots
- **Root Cause**: Profiler reference was stored but not the actual profiling data snapshot
- **Solution**: 
  - Added `cpu_profile_stats` field to store `pstats.Stats` snapshot
  - Create snapshot before profiler stops
  - Updated `_get_cpu_stats()` to use the snapshot
- **Impact**: ✅ CPU profiling now shows actual execution times and accurate statistics

#### Module Filter Fix
- **Problem**: Module filter dropdown was populated but had no functionality
- **Root Cause**: No event listener attached to handle filter changes
- **Solution**:
  - Added change event listener to filter dropdown
  - Implemented node and edge filtering logic
  - Added smooth zoom animation
  - Handle empty modules as "Main Module"
- **Impact**: ✅ Module filtering now works correctly with visual feedback

#### Layout Fixes
- **Problem**: Circular and Timeline layouts were not working
- **Root Cause**: Used incorrect `network.moveNode()` API which doesn't exist in vis.js
- **Solution**:
  - Replaced with proper node updates using `data.nodes.clear()` and `data.nodes.add()`
  - Fixed Circular layout with trigonometry calculations
  - Fixed Timeline layout with proper sorting by execution time
  - Added position management (fixed vs dynamic)
  - Removed duplicate layout handlers
- **Impact**: ✅ All 4 layouts (Hierarchical, Force, Circular, Timeline) now work correctly

#### JSON Export Fix
- **Problem**: "network.getData is not a function" error when clicking "Export as JSON"
- **Root Cause**: `network.getData()` method is not available in vis.js networks
- **Solution**:
  - Use original `nodes` and `edges` arrays instead
  - Added detailed error handling and logging
  - Enhanced metadata structure
  - Added success feedback
- **Impact**: ✅ JSON export now works reliably

#### Tracer Stability Fix
- **Problem**: Test programs would stop executing after the first few print statements
- **Root Cause**: 
  - Insufficient error handling in `_trace_calls` method
  - Conflicts between `@trace` decorator and `trace_scope` context manager
  - Missing exception handling caused silent failures
- **Solution**:
  - Enhanced error handling in `_trace_calls` with try-except blocks
  - Added filtering to skip internal callflow-tracer functions
  - Fixed `@trace` decorator integration with active trace_scope contexts
  - Improved caller name detection using `sys._getframe(3)`
  - Better global state management
- **Impact**: ✅ Programs now run to completion, generating complete visualizations

### ✨ Enhancements

#### Enhanced HTML Exporter
- **CPU Profile Section**:
  - Collapsible section with gradient header
  - Fire emoji icon (🔥) for visual appeal
  - Hover effects and smooth transitions
  - Dark code theme for profile data
  - Toggle functionality

- **Improved UI**:
  - Modern card-based layouts
  - Professional color schemes
  - Better spacing and typography
  - Responsive design improvements

#### Flamegraph Enhancements
- Custom titles support
- Configurable dimensions (width, height)
- Minimum width threshold to hide small functions
- Better tooltip information with percentages
- Responsive window resizing
- Auto-fit functionality

#### Export Enhancements
- Better metadata in JSON exports
- Timestamp and version information
- Structured export format
- Error handling and validation

### 📚 Documentation

#### New Documentation Files
- `README_NEW.md` - Comprehensive updated README
- `docs/API_DOCUMENTATION.md` - Complete API reference
- `docs/FEATURES_COMPLETE.md` - All features documented
- `ENHANCED_FEATURES.md` - Enhanced features guide
- `FLAMEGRAPH_SUMMARY.md` - Flamegraph overview
- `CHANGELOG.md` - This file

#### Updated Documentation
- `TESTING_GUIDE.md` - Added flamegraph testing section
- `QUICK_TEST.md` - Added flamegraph quick tests
- `examples/FLAMEGRAPH_README.md` - Complete flamegraph guide
- `examples/JUPYTER_README.md` - Jupyter integration guide

### 🧪 Testing

#### New Test Files
- `tests/test_flamegraph_enhanced.py` - 10 comprehensive tests for enhanced features
- `tests/test_jupyter_integration.py` - 7 tests for Jupyter integration
- `tests/test_cprofile_fix.py` - Tests for CPU profiling fix
- `tests/test_flamegraph.py` - 10 tests for basic flamegraph

#### New Example Files
- `examples/flamegraph_enhanced_demo.py` - 7 demos of enhanced features
- `examples/jupyter_example.ipynb` - Interactive Jupyter notebook
- `examples/jupyter_standalone_demo.py` - Standalone Jupyter demo
- `examples/flamegraph_example.py` - 7 flamegraph examples

### 📦 New Modules
- `callflow_tracer/flamegraph_enhanced.py` - Enhanced flamegraph HTML generation
- `callflow_tracer/jupyter.py` - Jupyter notebook integration

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
✅ Enhanced flamegraph with statistics  
✅ 5 color schemes  
✅ Search functionality  
✅ SVG export  
✅ Jupyter integration  
✅ Magic commands  
✅ Fixed CPU profiling  
✅ Fixed module filtering  
✅ Fixed all layouts  
✅ Fixed JSON export  
✅ Modern UI  
✅ Responsive design  

### 0.2.2 Features
✅ Stable tracing  
✅ Better error handling  
✅ Improved exports  
✅ UI enhancements  

### 0.2.0 Features
✅ Performance profiling  
✅ Memory tracking  
✅ Basic flamegraph  
✅ cProfile integration  

### 0.1.0 Features
✅ Call tracing  
✅ Call graph  
✅ HTML/JSON export  
✅ Interactive viz  

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

*Last Updated: 2025-10-05*
