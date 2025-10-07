# Graph Layout Visual Comparison

This document provides a visual guide to help you choose the right layout for your call flow visualization.

## Quick Selection Guide

### 🎯 Choose by Goal

| Your Goal | Recommended Layout | Why? |
|-----------|-------------------|------|
| Understand call hierarchy | Hierarchical, Tree (Vertical) | Clear parent-child relationships |
| Find performance bottlenecks | Timeline | Sorted by execution time |
| Discover code patterns | Force-Directed, Organic | Natural clustering reveals patterns |
| Compare all functions equally | Circular | No hierarchy bias |
| Visualize call depth | Radial Tree | Concentric circles show depth |
| Systematic analysis | Grid | Uniform, predictable positioning |
| Wide call graphs | Tree (Horizontal) | Better horizontal space usage |
| Aesthetic presentation | Organic (Spring) | Most natural appearance |

---

## Layout Characteristics

### 1. Hierarchical Layout
```
         [Root]
           |
    +------+------+
    |      |      |
  [A]    [B]    [C]
   |      |
  [D]    [E]
```

**Visual Pattern:** Traditional tree structure, top-down
**Node Distribution:** Organized in levels
**Edge Pattern:** Straight lines, no crossings
**Best View:** Portrait orientation

---

### 2. Force-Directed Layout
```
    [A]----[B]
     |  \   |
     |   \ [C]
    [D]   \|
           [E]
```

**Visual Pattern:** Organic clusters
**Node Distribution:** Physics-based spacing
**Edge Pattern:** Natural curves, minimal crossings
**Best View:** Square canvas

---

### 3. Circular Layout
```
        [A]
    [E]     [B]
    
    [D]     [C]
```

**Visual Pattern:** Perfect circle
**Node Distribution:** Equal angular spacing
**Edge Pattern:** Chords across circle
**Best View:** Square canvas

---

### 4. Radial Tree Layout
```
        [Root]
      /   |   \
    [A]  [B]  [C]
    / \   |
  [D] [E][F]
```

**Visual Pattern:** Concentric circles
**Node Distribution:** Depth-based rings
**Edge Pattern:** Radial spokes
**Best View:** Square canvas

---

### 5. Grid Layout
```
[A]  [B]  [C]
[D]  [E]  [F]
[G]  [H]  [I]
```

**Visual Pattern:** Uniform grid
**Node Distribution:** Row/column matrix
**Edge Pattern:** Varied directions
**Best View:** Any orientation

---

### 6. Tree (Vertical) Layout
```
         [Root]
           |
    +------+------+
    |             |
  [A]           [B]
   |             |
+--+--+       +--+--+
|     |       |     |
[C]  [D]     [E]  [F]
```

**Visual Pattern:** Enhanced hierarchical
**Node Distribution:** Customizable spacing
**Edge Pattern:** Straight, organized
**Best View:** Portrait orientation

---

### 7. Tree (Horizontal) Layout
```
[Root]--+--[A]--+--[C]
        |       |
        |       +--[D]
        |
        +--[B]--+--[E]
                |
                +--[F]
```

**Visual Pattern:** Left-to-right tree
**Node Distribution:** Horizontal levels
**Edge Pattern:** Horizontal flow
**Best View:** Landscape orientation

---

### 8. Timeline Layout
```
[Fast]--[Medium]--[Slow]--[Slower]--[Slowest]
  5ms     15ms     50ms     120ms     250ms
```

**Visual Pattern:** Linear sequence
**Node Distribution:** Sorted by time
**Edge Pattern:** Varied connections
**Best View:** Landscape orientation

---

### 9. Organic (Spring) Layout
```
    [A]~~~[B]
     |  ~~  |
     | ~  [C]
    [D]~~  |
         ~~[E]
```

**Visual Pattern:** Natural, flowing
**Node Distribution:** Barnes-Hut algorithm
**Edge Pattern:** Smooth curves
**Best View:** Square canvas

---

## Spacing Comparison

### Compact (100px)
- Dense visualization
- More nodes visible
- Harder to read labels
- Good for: Large graphs (50+ nodes)

### Normal (150px) - Default
- Balanced density
- Clear labels
- Good edge visibility
- Good for: Medium graphs (20-50 nodes)

### Relaxed (200px)
- Comfortable spacing
- Easy to read
- Clear relationships
- Good for: Small-medium graphs (10-30 nodes)

### Wide (300px)
- Maximum clarity
- Excellent readability
- Best for presentations
- Good for: Small graphs (<20 nodes)

---

## Use Case Examples

### Example 1: Web API Call Flow
**Best Layout:** Hierarchical or Tree (Vertical)
**Why:** Clear request → handler → service → database flow
**Spacing:** Normal or Relaxed

### Example 2: Microservices Communication
**Best Layout:** Force-Directed or Organic
**Why:** Reveals service clusters and communication patterns
**Spacing:** Normal

### Example 3: Database Query Optimization
**Best Layout:** Timeline
**Why:** Immediately shows which queries are slow
**Spacing:** Compact or Normal

### Example 4: Recursive Algorithm
**Best Layout:** Radial Tree
**Why:** Shows recursion depth clearly
**Spacing:** Normal or Relaxed

### Example 5: Event Processing Pipeline
**Best Layout:** Tree (Horizontal)
**Why:** Natural left-to-right flow matches event processing
**Spacing:** Normal

### Example 6: Large Codebase Analysis
**Best Layout:** Grid + Module Filter
**Why:** Systematic view with ability to focus on modules
**Spacing:** Compact

---

## Performance Considerations

### Fast Rendering (< 100ms)
- Hierarchical
- Grid
- Circular
- Timeline
- Tree layouts

### Medium Rendering (100-500ms)
- Radial Tree
- Force-Directed (small graphs)

### Slower Rendering (> 500ms)
- Force-Directed (large graphs)
- Organic (large graphs)

**Tip:** For large graphs, start with a static layout (Grid, Hierarchical) then switch to physics-based layouts if needed.

---

## Interactive Features by Layout

| Layout | Physics | Draggable | Auto-fit | Zoom |
|--------|---------|-----------|----------|------|
| Hierarchical | ❌ | ✅ | ✅ | ✅ |
| Force-Directed | ✅ | ✅ | ✅ | ✅ |
| Circular | ❌ | ✅ | ✅ | ✅ |
| Radial Tree | ❌ | ✅ | ✅ | ✅ |
| Grid | ❌ | ✅ | ✅ | ✅ |
| Tree (Vertical) | ❌ | ✅ | ✅ | ✅ |
| Tree (Horizontal) | ❌ | ✅ | ✅ | ✅ |
| Timeline | ❌ | ✅ | ✅ | ✅ |
| Organic | ✅ | ✅ | ✅ | ✅ |

---

## Tips for Choosing

### For Presentations
1. Start with **Organic** or **Force-Directed** for visual appeal
2. Use **Relaxed** or **Wide** spacing
3. Enable smooth animations
4. Export as high-resolution PNG

### For Debugging
1. Use **Hierarchical** or **Tree (Vertical)** for clarity
2. Use **Normal** spacing
3. Disable physics for stability
4. Use module filtering to focus

### For Documentation
1. Use **Tree (Horizontal)** for wide diagrams
2. Use **Normal** spacing
3. Export as PNG or JSON
4. Include legend and stats

### For Analysis
1. Start with **Timeline** to find bottlenecks
2. Switch to **Force-Directed** to find patterns
3. Use **Radial Tree** to understand depth
4. Use **Grid** for systematic comparison

---

## Keyboard Shortcuts (in HTML viewer)

- **Scroll:** Zoom in/out
- **Click + Drag:** Pan view
- **Double Click:** Fit to screen
- **Ctrl + Click:** Select node
- **Shift + Click:** Multi-select

---

## Advanced Tips

### Combining Layouts
1. Start with **Timeline** to identify slow functions
2. Switch to **Hierarchical** to trace call path
3. Use **Force-Directed** to see related functions
4. Export each view for comparison

### Module Filtering
- Use with **Grid** layout for organized module view
- Use with **Radial Tree** to see module depth
- Combine with **Timeline** for module performance

### Spacing Optimization
- Large graphs: Start **Compact**, increase if needed
- Small graphs: Start **Relaxed**, adjust for screen
- Presentations: Use **Wide** for maximum clarity
- Analysis: Use **Normal** for balanced view

---

## Common Issues and Solutions

### Issue: Nodes overlap
**Solution:** 
- Increase spacing to Relaxed or Wide
- Try Grid or Radial Tree layout
- Enable physics temporarily to auto-space

### Issue: Graph too spread out
**Solution:**
- Decrease spacing to Compact or Normal
- Use Fit to Screen (double-click)
- Try Circular layout for compact view

### Issue: Can't see relationships
**Solution:**
- Use Hierarchical or Tree layout
- Enable edge labels
- Zoom in on specific areas

### Issue: Too many nodes
**Solution:**
- Use module filtering
- Try Grid layout with Compact spacing
- Export to JSON and analyze subsets

---

## Conclusion

The best layout depends on your specific use case:

- **Understanding:** Hierarchical, Tree layouts
- **Performance:** Timeline layout
- **Patterns:** Force-Directed, Organic
- **Presentation:** Organic, Radial Tree
- **Analysis:** Grid, Timeline

Experiment with different layouts and spacing to find what works best for your specific call flow!
