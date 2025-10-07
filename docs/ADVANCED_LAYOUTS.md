# Advanced Graph Layouts

CallFlow Tracer now supports **9 advanced graph layout algorithms** to visualize your function call flows in different ways. Each layout offers unique insights into your code's execution patterns.

## Available Layouts

### 1. 📊 Hierarchical Layout
**Best for:** Understanding call hierarchies and dependencies

Traditional top-down tree structure that clearly shows parent-child relationships between function calls.

**Features:**
- Clear hierarchy visualization
- Automatic level-based positioning
- No overlapping nodes
- Static layout (no physics)

**Use when:** You want to see the clear call stack and function hierarchy.

---

### 2. 🌀 Force-Directed Layout
**Best for:** Discovering natural clusters and relationships

Physics-based layout using the ForceAtlas2 algorithm. Nodes repel each other while edges act as springs, creating organic groupings.

**Features:**
- Automatic clustering of related functions
- Dynamic physics simulation
- Natural spacing
- Interactive repositioning

**Use when:** You want to discover hidden patterns and natural groupings in your code.

---

### 3. ⭕ Circular Layout
**Best for:** Comparing all functions equally

Arranges all nodes in a perfect circle, giving equal visual weight to each function.

**Features:**
- Equal spacing around circumference
- Clear edge patterns
- Symmetrical layout
- Static positioning

**Use when:** You want to see all functions at once without hierarchy bias.

---

### 4. 🎯 Radial Tree Layout
**Best for:** Visualizing depth levels and call propagation

Arranges nodes in concentric circles based on their depth in the call tree. Root functions are at the center, with child calls radiating outward.

**Features:**
- Depth-based concentric circles
- Clear level separation
- Radial symmetry
- BFS-based positioning

**Use when:** You want to see how calls propagate through different depth levels.

---

### 5. 📐 Grid Layout
**Best for:** Systematic comparison and uniform spacing

Arranges nodes in a uniform grid pattern, making it easy to scan and compare functions systematically.

**Features:**
- Uniform row/column spacing
- Predictable positioning
- Easy scanning
- Adjustable density

**Use when:** You need a systematic, organized view of all functions.

---

### 6. 🌲 Tree (Vertical) Layout
**Best for:** Traditional call stack visualization

Enhanced vertical tree with customizable spacing between nodes and levels.

**Features:**
- Top-down flow
- Customizable node spacing
- Level separation control
- Tree spacing adjustment

**Use when:** You want a traditional call stack view with fine-tuned spacing.

---

### 7. 🌳 Tree (Horizontal) Layout
**Best for:** Wide call graphs with many branches

Left-to-right tree layout ideal for graphs with many horizontal branches.

**Features:**
- Left-to-right flow
- Better use of screen width
- Customizable spacing
- Ideal for wide graphs

**Use when:** Your call graph is wide rather than deep.

---

### 8. ⏱️ Timeline Layout
**Best for:** Performance analysis and execution order

Arranges functions horizontally based on their total execution time, creating a performance timeline.

**Features:**
- Sorted by execution time
- Linear arrangement
- Performance comparison
- Time-based ordering

**Use when:** You want to identify performance bottlenecks at a glance.

---

### 9. 🌿 Organic (Spring) Layout
**Best for:** Natural, aesthetically pleasing visualizations

Uses Barnes-Hut algorithm for a natural, spring-based layout with advanced physics simulation.

**Features:**
- Advanced physics (Barnes-Hut)
- Natural node distribution
- Overlap avoidance
- Smooth animations

**Use when:** You want the most natural-looking and aesthetically pleasing layout.

---

## Layout Customization

### Node Spacing Options

All layouts support customizable node spacing:

- **Compact (100px):** Dense layout for large graphs
- **Normal (150px):** Default balanced spacing
- **Relaxed (200px):** More breathing room
- **Wide (300px):** Maximum spacing for detailed analysis

### Physics Control

Toggle physics simulation on/off:
- **Enabled:** Dynamic, interactive positioning
- **Disabled:** Static, fixed positioning

---

## Usage Examples

### Basic Usage

```python
from callflow_tracer import trace_scope

with trace_scope("output.html"):
    # Your traced code here
    main()
```

The generated HTML will include all layout options in the dropdown menu.

### Programmatic Layout Selection

```python
from callflow_tracer import export_html, get_current_graph

# Get the current call graph
graph = get_current_graph()

# Export with specific layout (default)
export_html(graph, "output.html", layout="hierarchical")
```

### Interactive Controls

When you open the generated HTML file, you'll find:

1. **Layout Dropdown:** Switch between all 9 layouts
2. **Node Spacing:** Adjust spacing (Compact/Normal/Relaxed/Wide)
3. **Physics Toggle:** Enable/disable physics simulation
4. **Module Filter:** Filter by specific modules
5. **Export Options:** Save as PNG or JSON

---

## Layout Comparison Table

| Layout | Physics | Best For | Complexity | Performance |
|--------|---------|----------|------------|-------------|
| Hierarchical | ❌ | Call hierarchies | Low | Fast |
| Force-Directed | ✅ | Natural clustering | Medium | Medium |
| Circular | ❌ | Equal comparison | Low | Fast |
| Radial Tree | ❌ | Depth visualization | Medium | Fast |
| Grid | ❌ | Systematic view | Low | Fast |
| Tree (Vertical) | ❌ | Traditional stack | Low | Fast |
| Tree (Horizontal) | ❌ | Wide graphs | Low | Fast |
| Timeline | ❌ | Performance analysis | Low | Fast |
| Organic (Spring) | ✅ | Aesthetic layout | High | Slower |

---

## Tips and Best Practices

### For Small Graphs (< 20 nodes)
- **Recommended:** Hierarchical, Tree (Vertical), or Radial Tree
- Use **Normal** or **Relaxed** spacing
- Physics can be enabled for interactivity

### For Medium Graphs (20-50 nodes)
- **Recommended:** Force-Directed, Radial Tree, or Organic
- Use **Normal** spacing
- Enable physics for Force-Directed and Organic

### For Large Graphs (> 50 nodes)
- **Recommended:** Grid, Circular, or Force-Directed
- Use **Compact** spacing
- Disable physics for better performance
- Use module filtering to focus on specific areas

### For Performance Analysis
- **Recommended:** Timeline layout
- Sort functions by execution time
- Quickly identify bottlenecks

### For Understanding Dependencies
- **Recommended:** Hierarchical or Tree layouts
- Clear parent-child relationships
- Easy to trace call paths

---

## Advanced Features

### Dynamic Layout Switching
Switch between layouts in real-time without reloading:
- All layouts are computed on-the-fly
- Smooth transitions between layouts
- No data loss when switching

### Responsive Spacing
Spacing adjustments apply to current layout:
- Instantly see the effect
- Fine-tune for your screen size
- Optimize for presentation or analysis

### Export Capabilities
Export any layout as:
- **PNG:** High-resolution image (2x scale)
- **JSON:** Complete graph data with metadata

---

## Technical Details

### Layout Algorithms

**Hierarchical:** Uses vis.js hierarchical layout with directed sorting

**Force-Directed:** ForceAtlas2 algorithm with configurable gravity

**Circular:** Mathematical circle positioning with equal angular spacing

**Radial Tree:** BFS traversal with polar coordinate positioning

**Grid:** Square root-based column calculation for balanced grid

**Tree Layouts:** Enhanced hierarchical with custom spacing parameters

**Timeline:** Sorted linear arrangement based on execution metrics

**Organic:** Barnes-Hut algorithm with n-body simulation

### Performance Characteristics

- **Static layouts** (Grid, Circular, Timeline): O(n) complexity
- **Tree layouts** (Hierarchical, Tree, Radial): O(n log n) complexity
- **Physics layouts** (Force, Organic): O(n²) complexity with optimization

---

## Browser Compatibility

All layouts work in modern browsers:
- ✅ Chrome/Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Opera 76+

---

## Examples

See `examples/advanced_layouts_demo.py` for a comprehensive demonstration of all layouts.

```bash
cd examples
python advanced_layouts_demo.py
```

This will generate an interactive HTML file showcasing all layout options with a realistic call graph.

---

## Troubleshooting

### Layout appears cluttered
- Try increasing node spacing to "Relaxed" or "Wide"
- Use module filtering to reduce visible nodes
- Switch to Grid or Circular layout for uniform spacing

### Physics layouts are slow
- Disable physics after stabilization
- Reduce node count with filtering
- Use static layouts for large graphs

### Nodes overlap
- Increase spacing
- Try Radial Tree or Grid layout
- Enable overlap avoidance in Organic layout

---

## Future Enhancements

Planned features for future releases:
- Custom layout algorithms
- Layout presets and saving
- Animation between layouts
- 3D layout options
- Cluster-based layouts

---

## Contributing

Have ideas for new layouts? Open an issue or submit a PR!

Repository: [callflow-tracer](https://github.com/yourusername/callflow-tracer)
