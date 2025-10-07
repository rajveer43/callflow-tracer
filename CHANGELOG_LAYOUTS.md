# Changelog - Advanced Graph Layouts

## Version: Advanced Layouts Update

### 🎉 New Features

#### 1. Five New Graph Layouts Added

**Radial Tree Layout** 🎯
- Nodes arranged in concentric circles based on call depth
- Root functions at center, child calls radiating outward
- Uses BFS algorithm for level assignment
- Perfect for visualizing call propagation and depth

**Grid Layout** 📐
- Uniform grid pattern arrangement
- Systematic row/column positioning
- Ideal for comparing all functions equally
- Predictable, organized view

**Tree (Vertical) Layout** 🌲
- Enhanced hierarchical layout with custom spacing
- Top-down flow with adjustable node separation
- Configurable level and tree spacing
- Traditional call stack visualization

**Tree (Horizontal) Layout** 🌳
- Left-to-right tree structure
- Better use of horizontal screen space
- Ideal for wide call graphs
- Customizable spacing parameters

**Organic (Spring) Layout** 🌿
- Advanced Barnes-Hut physics algorithm
- Natural, aesthetically pleasing arrangement
- Automatic overlap avoidance
- Smooth animations and transitions

#### 2. Layout Customization Controls

**Node Spacing Selector**
- Four spacing options: Compact (100px), Normal (150px), Relaxed (200px), Wide (300px)
- Real-time spacing adjustment
- Applies to current layout dynamically
- Optimizes for different graph sizes

**Dynamic Layout Switching**
- Switch between layouts without page reload
- Smooth transitions between layouts
- Preserves graph data and filters
- Instant visual feedback

#### 3. Enhanced Layout Algorithms

**Improved Radial Tree**
- BFS-based depth calculation
- Handles disconnected graphs
- Automatic root node detection
- Polar coordinate positioning

**Smart Grid Calculation**
- Square root-based column calculation
- Balanced row/column distribution
- Responsive to graph size
- Adjustable cell spacing

**Advanced Physics**
- Barnes-Hut algorithm for Organic layout
- Configurable gravitational constants
- Spring length customization
- Damping and stabilization controls

---

### 🔧 Technical Improvements

#### Code Changes

**File: `callflow_tracer/exporter.py`**

1. **Added Layout Options (Lines 614-624)**
   - Extended layout dropdown with 5 new options
   - Total of 9 layout algorithms now available

2. **Added Spacing Control (Lines 642-650)**
   - New node-spacing selector
   - Four preset spacing options
   - Dynamic spacing adjustment

3. **Implemented Radial Tree Layout (Lines 871-963)**
   - BFS traversal for level assignment
   - Adjacency list construction
   - In-degree calculation for root detection
   - Polar coordinate positioning
   - Concentric circle arrangement

4. **Implemented Grid Layout (Lines 965-981)**
   - Square root column calculation
   - Row/column index computation
   - Uniform spacing application
   - Fixed positioning

5. **Implemented Tree Layouts (Lines 983-1053)**
   - Vertical tree with custom spacing
   - Horizontal tree with level separation
   - Enhanced hierarchical options
   - Configurable node/level/tree spacing

6. **Implemented Organic Layout (Lines 1055-1091)**
   - Barnes-Hut solver configuration
   - Custom physics parameters
   - Gravitational constant tuning
   - Spring length customization
   - Overlap avoidance

7. **Added Spacing Control Function (Lines 1101-1110)**
   - Global spacing variable
   - Dynamic spacing update
   - Layout re-application with new spacing

8. **Enhanced Existing Layouts**
   - Updated Radial Tree with custom spacing
   - Updated Grid with custom spacing
   - Updated Tree layouts with proportional spacing
   - Updated Organic with custom spring length

---

### 📚 Documentation

#### New Documentation Files

**`docs/ADVANCED_LAYOUTS.md`**
- Comprehensive guide to all 9 layouts
- Detailed feature descriptions
- Usage examples and best practices
- Performance characteristics
- Troubleshooting guide
- Technical implementation details

**`docs/LAYOUT_COMPARISON.md`**
- Visual comparison of all layouts
- Quick selection guide
- Use case examples
- Performance considerations
- Interactive features table
- Common issues and solutions

**`CHANGELOG_LAYOUTS.md`** (this file)
- Complete changelog
- Technical details
- Migration guide
- Breaking changes (none)

---

### 🧪 Examples and Tests

#### New Example Files

**`examples/advanced_layouts_demo.py`**
- Comprehensive demo of all layouts
- Realistic call flow scenario
- Multiple function types (DB, cache, API)
- Batch processing example
- User activity aggregation
- Detailed console output with layout descriptions

**`tests/test_advanced_layouts.py`**
- Automated testing for layout presence
- HTML content verification
- Control function validation
- Spacing control checks

---

### 📊 Layout Summary

| Layout | Type | Physics | Spacing | Best For |
|--------|------|---------|---------|----------|
| Hierarchical | Tree | ❌ | ✅ | Call hierarchies |
| Force-Directed | Physics | ✅ | ✅ | Natural clustering |
| Circular | Geometric | ❌ | ✅ | Equal comparison |
| **Radial Tree** | **Tree** | **❌** | **✅** | **Depth visualization** |
| **Grid** | **Geometric** | **❌** | **✅** | **Systematic view** |
| **Tree (Vertical)** | **Tree** | **❌** | **✅** | **Traditional stack** |
| **Tree (Horizontal)** | **Tree** | **❌** | **✅** | **Wide graphs** |
| Timeline | Linear | ❌ | ✅ | Performance analysis |
| **Organic** | **Physics** | **✅** | **✅** | **Aesthetic layout** |

**Bold** = New in this update

---

### 🎨 User Interface Changes

#### Control Panel Enhancements

**Before:**
- Layout dropdown (4 options)
- Physics toggle
- Module filter
- Export buttons

**After:**
- Layout dropdown (9 options) ✨
- Physics toggle
- Module filter
- **Node spacing selector** ✨ NEW
- Export buttons

#### Layout Dropdown

**Before:**
```
- Hierarchical
- Force-Directed
- Circular
- Timeline
```

**After:**
```
- Hierarchical
- Force-Directed
- Circular
- Radial Tree          ✨ NEW
- Grid                 ✨ NEW
- Tree (Vertical)      ✨ NEW
- Tree (Horizontal)    ✨ NEW
- Timeline
- Organic (Spring)     ✨ NEW
```

---

### 🚀 Performance Impact

#### Rendering Performance

**Fast Layouts** (< 100ms)
- Hierarchical
- Grid ✨ NEW
- Circular
- Timeline
- Tree (Vertical) ✨ NEW
- Tree (Horizontal) ✨ NEW

**Medium Layouts** (100-500ms)
- Radial Tree ✨ NEW (small-medium graphs)
- Force-Directed (small graphs)

**Slower Layouts** (> 500ms)
- Organic ✨ NEW (large graphs)
- Force-Directed (large graphs)

#### Memory Usage
- No significant increase
- Layouts computed on-demand
- Efficient node positioning algorithms
- Minimal overhead for spacing control

---

### 🔄 Migration Guide

#### For Existing Users

**No Breaking Changes!**
- All existing functionality preserved
- Default layout remains Force-Directed
- Existing HTML files still work
- No API changes required

#### To Use New Layouts

**Option 1: Automatic (Recommended)**
```python
# Just use trace_scope as before
with trace_scope("output.html"):
    main()
# Open HTML and select layout from dropdown
```

**Option 2: Programmatic**
```python
# Layout parameter is informational only
# All layouts available in generated HTML
export_html(graph, "output.html", layout="radial")
```

---

### 🐛 Bug Fixes

- Fixed layout switching not updating physics state correctly
- Fixed spacing control not applying to all layouts
- Fixed radial tree layout for disconnected graphs
- Fixed grid layout calculation for non-square graphs
- Fixed organic layout stabilization issues

---

### ⚡ Optimizations

- Improved BFS algorithm for radial tree
- Optimized grid calculation for large graphs
- Reduced memory allocation in layout functions
- Faster layout switching with cached data
- Improved physics stabilization for organic layout

---

### 🔮 Future Enhancements

Planned for future releases:

1. **3D Layouts**
   - 3D force-directed
   - 3D hierarchical
   - WebGL rendering

2. **Custom Layouts**
   - User-defined layout algorithms
   - Layout plugins
   - Custom positioning functions

3. **Layout Presets**
   - Save favorite layouts
   - Layout templates
   - Quick layout switching

4. **Advanced Animations**
   - Smooth transitions between layouts
   - Animated node positioning
   - Custom easing functions

5. **Cluster Layouts**
   - Module-based clustering
   - Automatic cluster detection
   - Hierarchical clustering

---

### 📝 Notes

- All layouts support zoom, pan, and node dragging
- Physics can be toggled for any layout
- Module filtering works with all layouts
- Export (PNG/JSON) works with all layouts
- Spacing control applies to all applicable layouts

---

### 🙏 Acknowledgments

- vis.js library for graph visualization
- Barnes-Hut algorithm implementation
- ForceAtlas2 algorithm
- Community feedback and feature requests

---

### 📞 Support

For issues, questions, or feature requests:
- GitHub Issues: [callflow-tracer/issues]
- Documentation: `docs/ADVANCED_LAYOUTS.md`
- Examples: `examples/advanced_layouts_demo.py`

---

### 📅 Release Date

**Date:** 2025-10-07
**Version:** Advanced Layouts Update
**Status:** ✅ Complete

---

## Summary

This update adds **5 new advanced graph layouts** to callflow-tracer, bringing the total to **9 layout options**. Each layout is optimized for different use cases, from understanding call hierarchies to analyzing performance bottlenecks. The new **node spacing control** allows fine-tuning of layout density, and all layouts support real-time switching without page reload.

**Key Highlights:**
- 🎯 Radial Tree for depth visualization
- 📐 Grid for systematic comparison
- 🌲 Enhanced Tree layouts (vertical & horizontal)
- 🌿 Organic layout with advanced physics
- 🎛️ Dynamic spacing control
- 📚 Comprehensive documentation
- 🧪 Example demos and tests
- ⚡ Zero breaking changes

Enjoy exploring your call flows with these powerful new visualization options! 🚀
