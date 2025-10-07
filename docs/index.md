# CallFlow Tracer - Documentation Index

Complete documentation index for CallFlow Tracer.

---

## 📚 Documentation Structure

### 🆕 Latest Release Notes
- See v0.2.4 release notes: [v0_2_4_features.md](v0_2_4_features.md)

### 🚀 Getting Started
1. **[README.md](../README.md)** - Main introduction and quick start
2. **[INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)** - Installation and setup
3. **[USER_GUIDE.md](USER_GUIDE.md)** - Complete user guide
4. **[QUICK_TEST.md](../QUICK_TEST.md)** - Quick testing reference

### 📖 Core Documentation
5. **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Complete API reference
6. **[FEATURES_COMPLETE.md](FEATURES_COMPLETE.md)** - All features explained
7. **[CHANGELOG.md](../CHANGELOG.md)** - Version history and changes

### 🔥 Feature-Specific Guides
8. **[FLAMEGRAPH_README.md](../examples/FLAMEGRAPH_README.md)** - Flamegraph guide
9. **[ENHANCED_FEATURES.md](../ENHANCED_FEATURES.md)** - Enhanced features
10. **[FLAMEGRAPH_SUMMARY.md](../FLAMEGRAPH_SUMMARY.md)** - Flamegraph summary
11. **[JUPYTER_README.md](../examples/JUPYTER_README.md)** - Jupyter integration

### 🧪 Testing Documentation
12. **[TESTING_GUIDE.md](../TESTING_GUIDE.md)** - Comprehensive testing guide
13. **Test Files**: `tests/test_*.py` - Automated test suites

### 💡 Examples
14. **Example Files**: `examples/*.py` - Runnable examples
15. **Jupyter Notebook**: `examples/jupyter_example.ipynb` - Interactive examples

---

## 📋 Quick Navigation

### By Topic

#### **Tracing**
- [Basic Tracing](USER_GUIDE.md#basic-tracing)
- [Decorator vs Context Manager](USER_GUIDE.md#method-1-context-manager-recommended)
- [API Reference](API_DOCUMENTATION.md#core-tracing-api)

#### **Profiling**
- [CPU Profiling](USER_GUIDE.md#cpu-profiling)
- [Memory Profiling](USER_GUIDE.md#memory-profiling)
- [I/O Wait Time](USER_GUIDE.md#io-wait-time)
- [Combined Profiling](USER_GUIDE.md#combined-profiling)
- [API Reference](API_DOCUMENTATION.md#profiling-api)

#### **Flamegraphs**
- [Basic Flamegraph](USER_GUIDE.md#basic-flamegraph)
- [Enhanced Flamegraph](USER_GUIDE.md#enhanced-flamegraph-recommended)
- [Color Schemes](ENHANCED_FEATURES.md#3-multiple-color-schemes)
- [Statistics Panel](ENHANCED_FEATURES.md#1-statistics-panel)
- [Search Functionality](ENHANCED_FEATURES.md#2-search-functionality)
- [Complete Guide](../examples/FLAMEGRAPH_README.md)
- [API Reference](API_DOCUMENTATION.md#flamegraph-api)

#### **Call Graphs**
- [Call Graph Visualization](USER_GUIDE.md#call-graph-visualization)
- [Layout Options](USER_GUIDE.md#using-different-layouts)
- [Module Filtering](USER_GUIDE.md#module-filtering)
- [API Reference](API_DOCUMENTATION.md#export-api)
#### **Jupyter Integration**
- [Setup](USER_GUIDE.md#setup)
- [Inline Visualization](USER_GUIDE.md#inline-visualization)
- [Magic Commands](USER_GUIDE.md#magic-commands)
- [Complete Guide](../examples/JUPYTER_README.md)

#### **Export**
- [HTML Export](API_DOCUMENTATION.md#export_html)
- [JSON Export](API_DOCUMENTATION.md#export_json)
- [SVG Export](ENHANCED_FEATURES.md#4-export-to-svg)

#### **New in v0.2.4**
- [Async/Await Tracing](v0_2_4_features.md#-asyncawait-tracing)
- [Comparison Mode](v0_2_4_features.md#-comparison-mode)
- [Memory Leak Detection](v0_2_4_features.md#-memory-leak-detection)
- [v0.2.4 Release Notes](v0_2_4_features.md)

---

##  By Use Case

### Finding Performance Bottlenecks
{{ ... }}
1. [Quick Performance Check](USER_GUIDE.md#workflow-1-quick-performance-check)
2. [Flamegraph Analysis](USER_GUIDE.md#flamegraph-analysis)
3. [Performance Color Scheme](ENHANCED_FEATURES.md#performance--recommended)
4. [Statistics Panel](ENHANCED_FEATURES.md#1-statistics-panel)

### Understanding Code Flow
1. [Basic Tracing](USER_GUIDE.md#basic-tracing)
2. [Call Graph Visualization](USER_GUIDE.md#call-graph-visualization)
3. [Layout Options](USER_GUIDE.md#using-different-layouts)
4. [Module Filtering](USER_GUIDE.md#module-filtering)

### Optimizing Performance
1. [Before/After Comparison](USER_GUIDE.md#workflow-3-beforeafter-comparison)
2. [Comprehensive Analysis](USER_GUIDE.md#workflow-2-comprehensive-analysis)
3. [Profiling Guide](USER_GUIDE.md#performance-profiling)

### Interactive Development
1. [Jupyter Setup](USER_GUIDE.md#jupyter-notebooks)
2. [Inline Visualization](USER_GUIDE.md#inline-visualization)
3. [Magic Commands](USER_GUIDE.md#magic-commands)
4. [Interactive Workflow](USER_GUIDE.md#workflow-4-jupyter-interactive-analysis)

### Creating Reports
1. [Export Options](USER_GUIDE.md#tip-2-export-svg-for-presentations)
2. [Custom Titles](USER_GUIDE.md#tip-5-use-descriptive-titles)
3. [Automated Reporting](USER_GUIDE.md#automated-reporting)

---

## 🔍 By Feature

### Core Features
- [Function Call Tracing](FEATURES_COMPLETE.md#1-function-call-tracing)
- [Call Graph Analysis](FEATURES_COMPLETE.md#2-call-graph-analysis)

### Visualization Features
- [Interactive Call Graph](FEATURES_COMPLETE.md#1-interactive-call-graph)
- [Multiple Layout Options](FEATURES_COMPLETE.md#2-multiple-layout-options)
- [Module Filtering](FEATURES_COMPLETE.md#3-module-filtering)

### Profiling Features
- [CPU Profiling](FEATURES_COMPLETE.md#1-cpu-profiling-cprofile-integration)
- [Memory Profiling](FEATURES_COMPLETE.md#2-memory-profiling)
- [I/O Wait Time](FEATURES_COMPLETE.md#3-io-wait-time-tracking)
- [Combined Profiling](FEATURES_COMPLETE.md#4-combined-profiling)

### Flamegraph Features
- [Basic Flamegraph](FEATURES_COMPLETE.md#1-basic-flamegraph)
- [Enhanced Flamegraph](FEATURES_COMPLETE.md#2-enhanced-flamegraph-new)
- [Color Schemes](FEATURES_COMPLETE.md#3-color-schemes)
- [Search Functionality](FEATURES_COMPLETE.md#4-search-functionality)
- [SVG Export](FEATURES_COMPLETE.md#5-svg-export)

### Jupyter Features
- [Magic Commands](FEATURES_COMPLETE.md#1-magic-commands)
- [Inline Visualization](FEATURES_COMPLETE.md#2-inline-visualization)
- [Full Feature Support](FEATURES_COMPLETE.md#3-full-feature-support)

### Export Features
- [HTML Export](FEATURES_COMPLETE.md#1-html-export)
- [JSON Export](FEATURES_COMPLETE.md#2-json-export)
- [SVG Export](FEATURES_COMPLETE.md#3-svg-export-flamegraph)

### UI/UX Features
- [Modern Design](FEATURES_COMPLETE.md#1-modern-design)
- [Responsive Design](FEATURES_COMPLETE.md#2-responsive-design)
- [Interactive Controls](FEATURES_COMPLETE.md#3-interactive-controls)
- [Rich Tooltips](FEATURES_COMPLETE.md#4-rich-tooltips)

---

## 📊 By Skill Level

### Beginner
1. Start with [README.md](../README.md)
2. Follow [Quick Start](../README.md#quick-start)
3. Run [Basic Examples](../examples/flamegraph_example.py)
4. Read [User Guide](USER_GUIDE.md)

### Intermediate
1. Read [API Documentation](API_DOCUMENTATION.md)
2. Explore [All Features](FEATURES_COMPLETE.md)
3. Try [Enhanced Features](ENHANCED_FEATURES.md)
4. Run [All Examples](../examples/)

### Advanced
1. Study [Source Code](../callflow_tracer/)
2. Read [Testing Guide](../TESTING_GUIDE.md)
3. Contribute features
4. Integrate with CI/CD

---

## 🎓 Learning Path

### Week 1: Basics
- [ ] Install package
- [ ] Run first trace
- [ ] Generate first visualization
- [ ] Understand call graphs

### Week 2: Profiling
- [ ] Learn CPU profiling
- [ ] Track memory usage
- [ ] Measure I/O wait
- [ ] Combine metrics

### Week 3: Flamegraphs
- [ ] Generate basic flamegraph
- [ ] Try all color schemes
- [ ] Use search functionality
- [ ] Export as SVG

### Week 4: Advanced
- [ ] Jupyter integration
- [ ] Programmatic analysis
- [ ] Automated workflows
- [ ] Custom integrations

---

## 📖 Documentation Files

### Main Documentation (Root)
| File | Description | Lines |
|------|-------------|-------|
| `README.md` | Main introduction | 674 |
| `CHANGELOG.md` | Version history | 500+ |
| `TESTING_GUIDE.md` | Testing guide | 500+ |
| `QUICK_TEST.md` | Quick reference | 165 |
| `ENHANCED_FEATURES.md` | Enhanced features | 300+ |
| `FLAMEGRAPH_SUMMARY.md` | Flamegraph overview | 400+ |

### Documentation Directory (docs/)
| File | Description | Lines |
|------|-------------|-------|
| `API_DOCUMENTATION.md` | Complete API reference | 600+ |
| `FEATURES_COMPLETE.md` | All features | 800+ |
| `INSTALLATION_GUIDE.md` | Installation guide | 400+ |
| `USER_GUIDE.md` | User guide | 700+ |
| `INDEX.md` | This file | 500+ |

### Examples Directory (examples/)
| File | Description | Lines |
|------|-------------|-------|
| `FLAMEGRAPH_README.md` | Flamegraph guide | 400+ |
| `JUPYTER_README.md` | Jupyter guide | 400+ |
| `flamegraph_example.py` | 7 examples | 500+ |
| `flamegraph_enhanced_demo.py` | 12 examples | 700+ |
| `jupyter_example.ipynb` | Notebook | - |
| `jupyter_standalone_demo.py` | Standalone demos | 600+ |

### Tests Directory (tests/)
| File | Description | Tests |
|------|-------------|-------|
| `test_flamegraph.py` | Flamegraph tests | 10 |
| `test_flamegraph_enhanced.py` | Enhanced tests | 10 |
| `test_jupyter_integration.py` | Jupyter tests | 7 |
| `test_cprofile_fix.py` | CPU profiling tests | 2 |

---

## 🔗 External Resources

### Official Links
- **GitHub**: https://github.com/rajveer43/callflow-tracer
- **PyPI**: https://pypi.org/project/callflow-tracer/
- **Issues**: https://github.com/rajveer43/callflow-tracer/issues
- **Discussions**: https://github.com/rajveer43/callflow-tracer/discussions

### Dependencies
- **vis.js**: https://visjs.org/
- **D3.js**: https://d3js.org/
- **NetworkX**: https://networkx.org/

---

## 📊 Statistics

### Documentation Coverage
- **Total Documentation Files**: 15+
- **Total Lines of Documentation**: 6000+
- **Total Examples**: 30+
- **Total Tests**: 39+
- **Code Coverage**: High

### Package Statistics
- **Total Modules**: 7
- **Total Functions**: 50+
- **Total Classes**: 5+
- **Lines of Code**: 3000+

---

## 🎯 Quick Links

### Most Important Documents
1. **[README.md](../README.md)** - Start here!
2. **[USER_GUIDE.md](USER_GUIDE.md)** - Complete usage guide
3. **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - API reference
4. **[ENHANCED_FEATURES.md](../ENHANCED_FEATURES.md)** - New features

### Most Useful Examples
1. **[flamegraph_enhanced_demo.py](../examples/flamegraph_enhanced_demo.py)** - All features
2. **[jupyter_example.ipynb](../examples/jupyter_example.ipynb)** - Jupyter examples
3. **[flamegraph_example.py](../examples/flamegraph_example.py)** - Basic examples

### Most Important Tests
1. **[test_flamegraph_enhanced.py](../tests/test_flamegraph_enhanced.py)** - Enhanced features
2. **[test_cprofile_fix.py](../tests/test_cprofile_fix.py)** - CPU profiling
3. **[test_jupyter_integration.py](../tests/test_jupyter_integration.py)** - Jupyter

---

## 🎓 Recommended Reading Order

### For New Users
1. [README.md](../README.md) - Overview
2. [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) - Setup
3. [USER_GUIDE.md](USER_GUIDE.md) - Usage
4. Run examples
5. [QUICK_TEST.md](../QUICK_TEST.md) - Verify

### For Developers
1. [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - API
2. [FEATURES_COMPLETE.md](FEATURES_COMPLETE.md) - Features
3. [TESTING_GUIDE.md](../TESTING_GUIDE.md) - Testing
4. Source code
5. Contribute

### For Performance Analysis
1. [ENHANCED_FEATURES.md](../ENHANCED_FEATURES.md) - New features
2. [FLAMEGRAPH_README.md](../examples/FLAMEGRAPH_README.md) - Flamegraphs
3. [USER_GUIDE.md](USER_GUIDE.md#flamegraph-analysis) - Analysis guide
4. Run examples

### For Jupyter Users
1. [JUPYTER_README.md](../examples/JUPYTER_README.md) - Jupyter guide
2. [jupyter_example.ipynb](../examples/jupyter_example.ipynb) - Notebook
3. [USER_GUIDE.md](USER_GUIDE.md#jupyter-notebooks) - Jupyter section
4. Run demos

---

## 🔍 Search by Keyword

### Tracing
- [trace_scope](API_DOCUMENTATION.md#trace_scopeoutput_filenone)
- [@trace decorator](API_DOCUMENTATION.md#trace)
- [get_current_graph](API_DOCUMENTATION.md#get_current_graph)

### Profiling
- [profile_function](API_DOCUMENTATION.md#profile_function)
- [profile_section](API_DOCUMENTATION.md#profile_sectionname)
- [CPU profiling](FEATURES_COMPLETE.md#1-cpu-profiling-cprofile-integration)
- [Memory profiling](FEATURES_COMPLETE.md#2-memory-profiling)

### Flamegraph
- [generate_flamegraph](API_DOCUMENTATION.md#generate_flamegraph)
- [Color schemes](ENHANCED_FEATURES.md#3-multiple-color-schemes)
- [Statistics panel](ENHANCED_FEATURES.md#1-statistics-panel)
- [Search](ENHANCED_FEATURES.md#2-search-functionality)

### Visualization
- [export_html](API_DOCUMENTATION.md#export_html)
- [Layouts](FEATURES_COMPLETE.md#2-multiple-layout-options)
- [Module filter](FEATURES_COMPLETE.md#3-module-filtering)

### Jupyter
- [display_callgraph](API_DOCUMENTATION.md#display_callgraph)
- [Magic commands](FEATURES_COMPLETE.md#1-magic-commands)
- [Inline display](FEATURES_COMPLETE.md#2-inline-visualization)

### Export
- [HTML export](FEATURES_COMPLETE.md#1-html-export)
- [JSON export](FEATURES_COMPLETE.md#2-json-export)
- [SVG export](FEATURES_COMPLETE.md#3-svg-export-flamegraph)

---

## 📦 Package Contents

### Source Code (callflow_tracer/)
```
callflow_tracer/
├── __init__.py              # Main API exports
├── tracer.py                # Core tracing (CallTracer, CallGraph, CallNode)
├── exporter.py              # HTML/JSON export functions
├── profiling.py             # Performance profiling (CPU, memory, I/O)
├── flamegraph.py            # Flamegraph generation
├── flamegraph_enhanced.py   # Enhanced flamegraph UI
└── jupyter.py               # Jupyter integration (magic commands, display)
```

### Examples (examples/)
```
examples/
├── flamegraph_example.py           # 7 basic flamegraph examples
├── flamegraph_enhanced_demo.py     # 12 enhanced feature demos
├── jupyter_example.ipynb           # Interactive Jupyter notebook
├── jupyter_standalone_demo.py      # 5 standalone Jupyter demos
├── FLAMEGRAPH_README.md            # Complete flamegraph guide
└── JUPYTER_README.md               # Complete Jupyter guide
```

### Tests (tests/)
```
tests/
├── test_flamegraph.py              # 10 flamegraph tests
├── test_flamegraph_enhanced.py     # 10 enhanced feature tests
├── test_jupyter_integration.py     # 7 Jupyter integration tests
└── test_cprofile_fix.py            # CPU profiling fix tests
```

### Documentation (docs/)
```
docs/
├── API_DOCUMENTATION.md            # Complete API reference
├── FEATURES_COMPLETE.md            # All features documented
├── INSTALLATION_GUIDE.md           # Installation and setup
├── USER_GUIDE.md                   # Complete user guide
└── INDEX.md                        # This file
```

---

## 🎨 Visual Guide

### What Each Visualization Shows

#### Call Graph (export_html)
```
┌─────────────────────────────────────┐
│         main()                      │
│    (100ms, 1 call)                 │
└──────────┬──────────────────────────┘
           │
     ┌─────┴─────┬─────────────┐
     │           │             │
┌────▼────┐ ┌───▼────┐  ┌────▼────┐
│ load()  │ │process()│  │ save()  │
│ 20ms    │ │  60ms   │  │  20ms   │
└─────────┘ └─────────┘  └─────────┘
```
**Shows**: Function relationships and call hierarchy

#### Flamegraph (generate_flamegraph)
```
┌─────────────────────────────────────┐
│         main() - 100ms              │
├──────────────┬──────────────────────┤
│  load()      │    process()         │
│   20ms       │     60ms             │
├──────┬───────┼──────┬───────────────┤
│ db   │ cache │ step1│    step2      │
│ 15ms │  5ms  │ 20ms │     40ms      │
└──────┴───────┴──────┴───────────────┘
```
**Shows**: Time distribution and bottlenecks (width = time)

---

## 🚀 Quick Commands

### Installation
```bash
pip install callflow-tracer
```

### Run Tests
```bash
python tests/test_flamegraph_enhanced.py
```

### Run Examples
```bash
python examples/flamegraph_enhanced_demo.py
```

### Generate Documentation
```bash
# All documentation is already generated!
# Just read the markdown files
```

---

## 📞 Getting Help

### Documentation
1. Check this index for relevant docs
2. Read the specific guide
3. Try the examples
4. Run the tests

### Community
1. Search GitHub issues
2. Ask in Discussions
3. Create new issue
4. Email support

### Support Channels
- 📧 Email: rathodrajveer1311@gmail.com
- 🐛 Issues: https://github.com/rajveer43/callflow-tracer/issues
- 💬 Discussions: https://github.com/rajveer43/callflow-tracer/discussions

---

## ✅ Documentation Checklist

### For Users
- [x] Installation guide
- [x] Quick start
- [x] User guide
- [x] API documentation
- [x] Examples
- [x] Troubleshooting

### For Developers
- [x] API reference
- [x] Testing guide
- [x] Feature documentation
- [x] Source code comments
- [x] Type hints
- [x] Docstrings

### For Contributors
- [x] Contributing guidelines
- [x] Code structure
- [x] Testing procedures
- [x] Development setup

---

## 🎉 Summary

CallFlow Tracer includes:

- **15+ Documentation Files** covering all aspects
- **30+ Examples** demonstrating features
- **39+ Tests** ensuring quality
- **7 Modules** with complete functionality
- **6000+ Lines** of documentation

Everything you need to:
- ✅ Trace function calls
- ✅ Profile performance
- ✅ Generate flamegraphs
- ✅ Visualize call graphs
- ✅ Use in Jupyter
- ✅ Find bottlenecks
- ✅ Optimize code

---

*Documentation Index - Last Updated: 2025-10-05*

**Start with [README.md](../README.md) and explore from there!** 🚀
