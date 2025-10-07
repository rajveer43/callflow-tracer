# Visual Guide to Graph Layouts

A visual reference for choosing the right layout for your call flow visualization.

## 🎨 Layout Gallery

### 1. Hierarchical Layout
```
                    ┌─────────────┐
                    │   main()    │
                    └──────┬──────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
      ┌────▼────┐     ┌────▼────┐     ┌────▼────┐
      │ func_a()│     │ func_b()│     │ func_c()│
      └────┬────┘     └────┬────┘     └────┬────┘
           │               │               │
      ┌────▼────┐     ┌────▼────┐     ┌────▼────┐
      │ func_d()│     │ func_e()│     │ func_f()│
      └─────────┘     └─────────┘     └─────────┘
```
**Use for:** Understanding call hierarchy and dependencies

---

### 2. Force-Directed Layout
```
         ┌─────────┐
         │ func_a()│◄────┐
         └────┬────┘     │
              │          │
         ┌────▼────┐     │
    ┌───►│ func_b()│     │
    │    └────┬────┘     │
    │         │          │
┌───┴────┐    │     ┌────┴────┐
│func_d()│◄───┴────►│ func_c()│
└────────┘          └────┬────┘
                         │
                    ┌────▼────┐
                    │ func_e()│
                    └─────────┘
```
**Use for:** Discovering natural clusters and patterns

---

### 3. Circular Layout
```
              ┌─────────┐
              │ func_a()│
              └─────────┘
        ┌─────────┘ └─────────┐
   ┌────────┐             ┌────────┐
   │func_f()│             │func_b()│
   └────────┘             └────────┘
        │                     │
   ┌────────┐             ┌────────┐
   │func_e()│             │func_c()│
   └────────┘             └────────┘
        └─────────┐ ┌─────────┘
              ┌────────┐
              │func_d()│
              └────────┘
```
**Use for:** Comparing all functions equally

---

### 4. Radial Tree Layout ⭐ NEW
```
                  ┌─────────┐
                  │ main()  │ ← Level 0 (center)
                  └────┬────┘
         ┌─────────────┼─────────────┐
         │             │             │
    ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
    │ func_a()│   │ func_b()│   │ func_c()│ ← Level 1
    └────┬────┘   └────┬────┘   └────┬────┘
         │             │             │
    ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
    │ func_d()│   │ func_e()│   │ func_f()│ ← Level 2
    └─────────┘   └─────────┘   └─────────┘
```
**Use for:** Visualizing call depth and propagation

---

### 5. Grid Layout ⭐ NEW
```
┌─────────┐  ┌─────────┐  ┌─────────┐
│ func_a()│  │ func_b()│  │ func_c()│
└─────────┘  └─────────┘  └─────────┘

┌─────────┐  ┌─────────┐  ┌─────────┐
│ func_d()│  │ func_e()│  │ func_f()│
└─────────┘  └─────────┘  └─────────┘

┌─────────┐  ┌─────────┐  ┌─────────┐
│ func_g()│  │ func_h()│  │ func_i()│
└─────────┘  └─────────┘  └─────────┘
```
**Use for:** Systematic comparison and organized view

---

### 6. Tree (Vertical) Layout ⭐ NEW
```
                ┌─────────────┐
                │   main()    │
                └──────┬──────┘
                       │
       ┌───────────────┼───────────────┐
       │                               │
  ┌────▼────┐                     ┌────▼────┐
  │ func_a()│                     │ func_b()│
  └────┬────┘                     └────┬────┘
       │                               │
  ┌────┼────┐                     ┌────┼────┐
  │    │    │                     │    │    │
┌─▼─┐┌─▼─┐┌─▼─┐                 ┌─▼─┐┌─▼─┐┌─▼─┐
│ c ││ d ││ e │                 │ f ││ g ││ h │
└───┘└───┘└───┘                 └───┘└───┘└───┘
```
**Use for:** Traditional call stack with enhanced spacing

---

### 7. Tree (Horizontal) Layout ⭐ NEW
```
                    ┌─────────┐
          ┌────────►│ func_c()│
          │         └─────────┘
┌─────────┴─┐       ┌─────────┐
│  func_a() ├──────►│ func_d()│
└─────────┬─┘       └─────────┘
          │         ┌─────────┐
          └────────►│ func_e()│
                    └─────────┘
┌───────────┐       ┌─────────┐
│  main()   ├──────►│ func_f()│
└───────────┬┘       └─────────┘
            │        ┌─────────┐
            └───────►│ func_g()│
                     └─────────┘
```
**Use for:** Wide call graphs with many branches

---

### 8. Timeline Layout
```
Fast ─────────────────────────────────────────► Slow

┌────┐  ┌────┐  ┌────┐  ┌────┐  ┌────┐  ┌────┐
│ A  │  │ B  │  │ C  │  │ D  │  │ E  │  │ F  │
│5ms │  │12ms│  │45ms│  │89ms│  │150 │  │300 │
└────┘  └────┘  └────┘  └────┘  └──ms┘  └──ms┘
```
**Use for:** Performance analysis and bottleneck identification

---

### 9. Organic (Spring) Layout ⭐ NEW
```
       ┌─────────┐
   ┌──►│ func_a()│◄──┐
   │   └─────────┘   │
   │        │        │
┌──┴───┐    │    ┌───┴───┐
│func_b│◄───┼───►│func_c │
└──┬───┘    │    └───┬───┘
   │   ┌────▼────┐   │
   └──►│ func_d()│◄──┘
       └────┬────┘
            │
       ┌────▼────┐
       │ func_e()│
       └─────────┘
```
**Use for:** Natural, aesthetically pleasing visualizations

---

## 🎯 Layout Selection Flowchart

```
                    Start
                      │
                      ▼
        ┌─────────────────────────┐
        │ What's your main goal?  │
        └─────────────┬───────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │Understand│  │  Find    │  │ Discover │
  │Hierarchy │  │Bottleneck│  │ Patterns │
  └─────┬────┘  └─────┬────┘  └─────┬────┘
        │             │             │
        ▼             ▼             ▼
  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │Hierarchic│  │ Timeline │  │  Force   │
  │   or     │  │          │  │Directed  │
  │Tree (V)  │  │          │  │   or     │
  └──────────┘  └──────────┘  │ Organic  │
                               └──────────┘
```

---

## 📊 Spacing Comparison

### Compact (100px)
```
┌──┐┌──┐┌──┐
│A ││B ││C │
└──┘└──┘└──┘
┌──┐┌──┐┌──┐
│D ││E ││F │
└──┘└──┘└──┘
```
**Dense, more nodes visible**

### Normal (150px) - Default
```
┌───┐  ┌───┐  ┌───┐
│ A │  │ B │  │ C │
└───┘  └───┘  └───┘

┌───┐  ┌───┐  ┌───┐
│ D │  │ E │  │ F │
└───┘  └───┘  └───┘
```
**Balanced, clear labels**

### Relaxed (200px)
```
┌────┐    ┌────┐    ┌────┐
│ A  │    │ B  │    │ C  │
└────┘    └────┘    └────┘


┌────┐    ┌────┐    ┌────┐
│ D  │    │ E  │    │ F  │
└────┘    └────┘    └────┘
```
**Comfortable, easy to read**

### Wide (300px)
```
┌─────┐        ┌─────┐        ┌─────┐
│  A  │        │  B  │        │  C  │
└─────┘        └─────┘        └─────┘



┌─────┐        ┌─────┐        ┌─────┐
│  D  │        │  E  │        │  F  │
└─────┘        └─────┘        └─────┘
```
**Maximum clarity, presentations**

---

## 🎨 Color Coding

All layouts use the same color scheme for performance:

```
┌─────────┐
│  Fast   │  < 10ms   (Blue)
└─────────┘

┌─────────┐
│ Medium  │  10-100ms (Teal)
└─────────┘

┌─────────┐
│  Slow   │  > 100ms  (Red)
└─────────┘
```

---

## 🔄 Layout Transitions

### Switching Between Layouts

```
Hierarchical ──┐
               │
Force-Direct ──┼──► Select Layout ──► Instant Switch
               │
Radial Tree ───┤
               │
Grid ──────────┤
               │
Organic ───────┘
```

**All transitions are instant with no page reload!**

---

## 💡 Best Practices

### Small Graphs (<20 nodes)
```
Recommended Layouts:
├── Hierarchical (Clear structure)
├── Radial Tree (Beautiful depth view)
└── Organic (Aesthetic)

Recommended Spacing: Relaxed or Wide
```

### Medium Graphs (20-50 nodes)
```
Recommended Layouts:
├── Force-Directed (Pattern discovery)
├── Tree (Vertical) (Clear hierarchy)
└── Radial Tree (Depth visualization)

Recommended Spacing: Normal
```

### Large Graphs (>50 nodes)
```
Recommended Layouts:
├── Grid (Systematic view)
├── Timeline (Performance focus)
└── Circular (Equal comparison)

Recommended Spacing: Compact
```

---

## 🎯 Quick Reference

| Symbol | Meaning |
|--------|---------|
| ⭐ | New in this update |
| 📊 | Static layout |
| 🌀 | Physics-based |
| 🎨 | Customizable spacing |
| ⚡ | Fast rendering |
| 🐌 | Slower rendering |

---

## 📱 Interactive Features

All layouts support:
- ✅ Zoom (scroll wheel)
- ✅ Pan (click and drag)
- ✅ Node selection (click)
- ✅ Fit to screen (double-click)
- ✅ Export (PNG/JSON)
- ✅ Module filtering

---

## 🎬 Example Scenarios

### Scenario 1: API Debugging
```
1. Start with Timeline → Find slow function
2. Switch to Hierarchical → Trace call path
3. Adjust to Relaxed spacing → See details
4. Export as PNG → Share with team
```

### Scenario 2: Code Review
```
1. Start with Tree (Horizontal) → See flow
2. Filter by module → Focus on changes
3. Adjust to Normal spacing → Clear view
4. Export as JSON → Document structure
```

### Scenario 3: Performance Optimization
```
1. Start with Timeline → Identify bottlenecks
2. Switch to Radial Tree → See call depth
3. Use Compact spacing → See all functions
4. Export as PNG → Track improvements
```

---

## 🚀 Getting Started

```python
# 1. Trace your code
from callflow_tracer import trace, trace_scope

@trace
def my_function():
    return "Hello"

with trace_scope("output.html"):
    my_function()

# 2. Open output.html
# 3. Try different layouts from dropdown
# 4. Adjust spacing as needed
# 5. Export your favorite view
```

---

## 📚 Learn More

- **Full Guide:** `docs/ADVANCED_LAYOUTS.md`
- **Quick Start:** `docs/QUICK_START_LAYOUTS.md`
- **Comparison:** `docs/LAYOUT_COMPARISON.md`
- **Demo:** `examples/advanced_layouts_demo.py`

---

**Happy Visualizing! 🎨**
