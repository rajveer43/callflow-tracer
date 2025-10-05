# Enhanced Flamegraph Features

## 🎉 New Features Added

The flamegraph module has been significantly enhanced with powerful new features to make performance analysis easier and more insightful!

---

## 📊 **1. Statistics Panel**

Automatically calculates and displays key metrics:

- **Total Functions**: Number of unique functions called
- **Total Calls**: Total number of function invocations
- **Total Time**: Cumulative execution time
- **Avg Time/Call**: Average time per function call
- **Call Depth**: Maximum call stack depth
- **🔥 Slowest Function**: Identifies the biggest bottleneck
- **📞 Most Called Function**: Shows which function is called most

### Usage:
```python
generate_flamegraph(
    graph,
    "output.html",
    show_stats=True  # Enable statistics panel
)
```

---

## 🔍 **2. Search Functionality**

Quickly find specific functions in large flamegraphs:

- Real-time search box
- Highlights matching functions
- Case-insensitive search
- Clear button to reset

### Usage:
```python
generate_flamegraph(
    graph,
    "output.html",
    search_enabled=True  # Enable search
)
```

**Try searching for**: `"api"`, `"database"`, `"cache"`, etc.

---

## 🎨 **3. Multiple Color Schemes**

Choose from 5 different color schemes:

### **Default**
- Red-Yellow-Green gradient
- Balanced view for general analysis

### **Hot** 🔥
- Red-Orange colors
- Emphasizes hot spots
- Great for highlighting slow areas

### **Cool** ❄️
- Blue-Green colors
- Easy on eyes for long analysis
- Calming color palette

### **Rainbow** 🌈
- Full spectrum colors
- Best for distinguishing many functions
- Visually appealing

### **Performance** ⚡ (Recommended!)
- **Green** = Fast functions
- **Red** = Slow functions
- **Perfect for finding bottlenecks!**

### Usage:
```python
generate_flamegraph(
    graph,
    "output.html",
    color_scheme="performance"  # or 'hot', 'cool', 'rainbow', 'default'
)
```

---

## 💾 **4. Export to SVG**

Export flamegraphs as high-quality vector graphics:

- Click the "💾 Export SVG" button
- Saves as scalable vector format
- Perfect for presentations and reports
- Preserves all colors and details
- No quality loss when zooming

---

## ✨ **5. Enhanced UI**

Modern, professional interface:

- **Gradient backgrounds** for visual appeal
- **Responsive design** works on all screen sizes
- **Hover effects** for better interactivity
- **Better tooltips** with percentage of total time
- **Smooth animations** for zoom and transitions
- **Mobile-friendly** layout

---

## 💡 **6. Built-in Optimization Tips**

Includes helpful guidance:

- How to read the flamegraph
- What to look for when optimizing
- Tips for finding bottlenecks
- Explanation of width and height meaning

---

## 🎯 **7. Custom Titles**

Set meaningful titles for your flamegraphs:

```python
generate_flamegraph(
    graph,
    "output.html",
    title="My Application Performance Analysis"
)
```

---

## 📏 **8. Minimum Width Threshold**

Hide functions that take less than a certain percentage:

```python
generate_flamegraph(
    graph,
    "output.html",
    min_width=0.5  # Hide functions < 0.5% of total time
)
```

Useful for focusing on significant functions in large graphs.

---

## 🚀 **Complete Example**

```python
from callflow_tracer import trace_scope
from callflow_tracer.flamegraph import generate_flamegraph

# Trace your code
with trace_scope() as graph:
    my_application()

# Generate enhanced flamegraph with ALL features
generate_flamegraph(
    graph,
    "performance_analysis.html",
    title="My App Performance Analysis",
    color_scheme="performance",  # Green=fast, Red=slow
    show_stats=True,             # Show statistics panel
    search_enabled=True,         # Enable search
    min_width=0.1,              # Hide functions < 0.1%
    width=1600,                 # Wider for more detail
    height=1000                 # Taller for deep stacks
)
```

---

## 📖 **How to Use**

### **Quick Start**

```bash
# Run the demo to see all features
cd examples
python flamegraph_enhanced_demo.py

# Run the tests
cd tests
python test_flamegraph_enhanced.py
```

### **Generated Files**

The demo creates 12 example files:
1. `flamegraph_basic_comparison.html` - Old style
2. `flamegraph_enhanced_comparison.html` - New style
3. `flamegraph_color_default.html`
4. `flamegraph_color_hot.html`
5. `flamegraph_color_cool.html`
6. `flamegraph_color_rainbow.html`
7. `flamegraph_color_performance.html` ⭐ **Recommended**
8. `flamegraph_search_demo.html`
9. `flamegraph_statistics_demo.html`
10. `flamegraph_performance_analysis.html`
11. `flamegraph_export_demo.html`
12. `flamegraph_ultimate_demo.html` - All features!

---

## 🎓 **Best Practices**

### **For Finding Bottlenecks**
```python
generate_flamegraph(
    graph,
    "bottlenecks.html",
    color_scheme="performance",  # Red = slow
    show_stats=True,
    search_enabled=True
)
```
- Look for **wide RED bars**
- Check the **statistics panel** for slowest function
- Use **search** to find specific functions

### **For Presentations**
```python
generate_flamegraph(
    graph,
    "presentation.html",
    title="Q4 Performance Analysis",
    color_scheme="rainbow",
    show_stats=True,
    width=1600,
    height=1000
)
```
- Use **custom title**
- Choose **rainbow** or **hot** color scheme
- Export as **SVG** for slides

### **For Deep Analysis**
```python
generate_flamegraph(
    graph,
    "deep_analysis.html",
    color_scheme="default",
    show_stats=True,
    search_enabled=True,
    min_width=0.05,  # Show more detail
    width=1800,
    height=1200
)
```
- Enable **all features**
- Use **lower min_width** to see more functions
- Larger **dimensions** for better visibility

---

## 🔄 **Backward Compatibility**

All old code still works! The new features are optional:

```python
# Old way - still works
generate_flamegraph(graph, "output.html")

# New way - with features
generate_flamegraph(
    graph, 
    "output.html",
    color_scheme="performance",
    show_stats=True
)
```

---

## 📊 **Comparison: Old vs New**

| Feature | Old | New |
|---------|-----|-----|
| **Statistics** | ❌ None | ✅ Full panel with metrics |
| **Search** | ❌ No | ✅ Real-time search |
| **Color Schemes** | 1 default | ✅ 5 schemes |
| **Export** | ❌ No | ✅ SVG export |
| **UI** | Basic | ✅ Modern, responsive |
| **Tooltips** | Basic | ✅ With percentages |
| **Tips** | ❌ No | ✅ Built-in guide |
| **Custom Title** | ❌ No | ✅ Yes |

---

## 🎯 **Use Cases**

### **1. Finding Performance Bottlenecks**
```python
# Use performance color scheme
generate_flamegraph(graph, "bottlenecks.html", color_scheme="performance")
# Wide RED bars = your targets!
```

### **2. Comparing Before/After Optimization**
```python
# Before
with trace_scope() as before:
    unoptimized_code()
generate_flamegraph(before, "before.html", color_scheme="performance")

# After
with trace_scope() as after:
    optimized_code()
generate_flamegraph(after, "after.html", color_scheme="performance")

# Compare the two files side by side
```

### **3. Analyzing Microservices**
```python
# Search for specific services
generate_flamegraph(
    graph, 
    "microservices.html",
    search_enabled=True,
    show_stats=True
)
# Search for: "service_a", "service_b", etc.
```

### **4. Creating Reports**
```python
# Export as SVG for presentations
generate_flamegraph(
    graph,
    "report.html",
    title="Q4 Performance Report",
    color_scheme="rainbow",
    show_stats=True
)
# Click "Export SVG" button in the browser
```

---

## 🐛 **Troubleshooting**

### **Issue: Enhanced features not showing**

**Solution**: Make sure you're using the new parameters:
```python
generate_flamegraph(
    graph,
    "output.html",
    show_stats=True,  # This triggers enhanced mode
    color_scheme="performance"
)
```

### **Issue: Colors don't match expectations**

**Solution**: Try different color schemes:
- `"performance"` - Best for optimization
- `"hot"` - Emphasizes slow areas
- `"cool"` - Easy on eyes

### **Issue: Too many small functions**

**Solution**: Use min_width threshold:
```python
generate_flamegraph(
    graph,
    "output.html",
    min_width=0.5  # Hide functions < 0.5%
)
```

---

## 📚 **Additional Resources**

- **Demo**: `examples/flamegraph_enhanced_demo.py`
- **Tests**: `tests/test_flamegraph_enhanced.py`
- **Original Guide**: `examples/FLAMEGRAPH_README.md`
- **Testing Guide**: `TESTING_GUIDE.md`

---

## ✨ **Summary**

The enhanced flamegraph module now provides:

✅ **Statistics Panel** - See metrics at a glance  
✅ **Search** - Find functions quickly  
✅ **5 Color Schemes** - Choose the best view  
✅ **Performance Colors** - Green=fast, Red=slow  
✅ **SVG Export** - For presentations  
✅ **Modern UI** - Professional and responsive  
✅ **Better Tooltips** - With percentages  
✅ **Optimization Tips** - Built-in guidance  
✅ **Backward Compatible** - Old code still works  

**Try it now and find your bottlenecks faster! 🔥**
