# Quick Start: Advanced Graph Layouts

Get started with the new advanced graph layouts in 5 minutes!

## 🚀 Quick Start

### 1. Run Your Code with Tracing

```python
from callflow_tracer import trace, trace_scope

@trace
def my_function():
    return "Hello, World!"

with trace_scope("output.html"):
    my_function()
```

### 2. Open the Generated HTML

```bash
# Open in your browser
firefox output.html
# or
google-chrome output.html
# or
open output.html  # macOS
```

### 3. Try Different Layouts

Use the **Layout** dropdown in the control panel to switch between:

1. **Hierarchical** - Traditional tree view
2. **Force-Directed** - Natural clustering
3. **Circular** - Equal node distribution
4. **Radial Tree** ⭐ NEW - Concentric circles by depth
5. **Grid** ⭐ NEW - Uniform grid pattern
6. **Tree (Vertical)** ⭐ NEW - Enhanced vertical tree
7. **Tree (Horizontal)** ⭐ NEW - Left-to-right tree
8. **Timeline** - Sorted by execution time
9. **Organic (Spring)** ⭐ NEW - Natural spring layout

### 4. Adjust Spacing

Use the **Node Spacing** dropdown:
- **Compact** - Dense layout for large graphs
- **Normal** - Default balanced spacing
- **Relaxed** - More breathing room
- **Wide** - Maximum spacing

---

## 🎯 Choose Your Layout in 10 Seconds

### I want to...

**Understand my call hierarchy**
→ Use **Hierarchical** or **Tree (Vertical)**

**Find performance bottlenecks**
→ Use **Timeline**

**See natural code patterns**
→ Use **Force-Directed** or **Organic**

**Compare all functions equally**
→ Use **Circular**

**Visualize call depth levels**
→ Use **Radial Tree**

**Get a systematic overview**
→ Use **Grid**

**View wide call graphs**
→ Use **Tree (Horizontal)**

**Create a beautiful presentation**
→ Use **Organic (Spring)**

---

## 💡 Pro Tips

### Tip 1: Start with Timeline
```
1. Open your HTML file
2. Select "Timeline" layout
3. Identify slow functions (they're on the right)
4. Switch to "Hierarchical" to trace their call path
```

### Tip 2: Use Spacing for Clarity
```
- Large graphs (50+ nodes): Start with "Compact"
- Medium graphs (20-50 nodes): Use "Normal"
- Small graphs (<20 nodes): Try "Relaxed" or "Wide"
```

### Tip 3: Combine with Module Filter
```
1. Select "Grid" layout
2. Choose a module from "Filter by module"
3. See organized view of that module's functions
```

### Tip 4: Export Your Favorite View
```
1. Arrange the layout you like
2. Click "Export as PNG" for images
3. Click "Export as JSON" for data
```

---

## 📊 Layout Cheat Sheet

| Layout | When to Use | Spacing |
|--------|-------------|---------|
| Hierarchical | Understanding hierarchy | Normal |
| Force-Directed | Finding patterns | Normal |
| Circular | Equal comparison | Relaxed |
| **Radial Tree** | **Visualizing depth** | **Normal** |
| **Grid** | **Systematic view** | **Compact** |
| **Tree (Vertical)** | **Call stacks** | **Normal** |
| **Tree (Horizontal)** | **Wide graphs** | **Normal** |
| Timeline | Performance analysis | Compact |
| **Organic** | **Presentations** | **Relaxed** |

---

## 🎬 Example Workflow

### Scenario: Debugging Slow API

```python
# 1. Trace your API call
from callflow_tracer import trace, trace_scope

@trace
def api_handler(request):
    data = fetch_from_db(request)
    result = process_data(data)
    return result

with trace_scope("api_debug.html"):
    api_handler(test_request)
```

```
# 2. Open api_debug.html

# 3. Select "Timeline" layout
#    → See that fetch_from_db is slow (250ms)

# 4. Select "Hierarchical" layout
#    → Trace the call path to fetch_from_db

# 5. Select "Radial Tree" layout
#    → See how deep the call stack goes

# 6. Adjust spacing to "Relaxed"
#    → Get clearer view of function names

# 7. Export as PNG
#    → Share with team
```

---

## 🔥 Advanced Features

### Real-Time Layout Switching
- No page reload needed
- Instant visual feedback
- Preserves zoom and pan state

### Dynamic Spacing
- Changes apply immediately
- Affects current layout
- Optimizes for your screen

### Interactive Controls
- **Scroll** to zoom
- **Drag** to pan
- **Double-click** to fit screen
- **Click node** to highlight

---

## 📱 Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Zoom In | Scroll Up |
| Zoom Out | Scroll Down |
| Pan | Click + Drag |
| Fit to Screen | Double Click |
| Select Node | Click |

---

## 🎨 Customization Examples

### Example 1: Presentation Mode
```
Layout: Organic (Spring)
Spacing: Wide
Physics: Enabled
Module Filter: None
```

### Example 2: Debug Mode
```
Layout: Hierarchical
Spacing: Normal
Physics: Disabled
Module Filter: Your module
```

### Example 3: Performance Analysis
```
Layout: Timeline
Spacing: Compact
Physics: Disabled
Module Filter: None
```

### Example 4: Code Review
```
Layout: Tree (Horizontal)
Spacing: Relaxed
Physics: Disabled
Module Filter: Specific module
```

---

## 🐛 Troubleshooting

### Problem: Nodes are overlapping
**Solution:** Increase spacing to "Relaxed" or "Wide"

### Problem: Graph is too spread out
**Solution:** Decrease spacing to "Compact" or "Normal"

### Problem: Can't see all nodes
**Solution:** Double-click to fit to screen

### Problem: Layout is too slow
**Solution:** Disable physics or use a static layout

### Problem: Too many nodes
**Solution:** Use module filter to focus on specific areas

---

## 📚 Learn More

- **Full Documentation:** `docs/ADVANCED_LAYOUTS.md`
- **Visual Comparison:** `docs/LAYOUT_COMPARISON.md`
- **Complete Example:** `examples/advanced_layouts_demo.py`
- **Changelog:** `CHANGELOG_LAYOUTS.md`

---

## 🎓 Next Steps

1. ✅ Run the demo: `python examples/advanced_layouts_demo.py`
2. ✅ Try different layouts on your own code
3. ✅ Experiment with spacing options
4. ✅ Combine layouts with module filtering
5. ✅ Export and share your visualizations

---

## 💬 Need Help?

- Check the full documentation: `docs/ADVANCED_LAYOUTS.md`
- Run the demo: `examples/advanced_layouts_demo.py`
- Open an issue on GitHub

---

## 🎉 Have Fun!

Explore your code's call flows with these powerful visualization tools. Each layout reveals different insights about your code's structure and performance.

**Happy Tracing! 🚀**
