# CallFlow Tracer v0.2.4 — Release Notes

Date: 2025-10-07

## 🚀 Highlights

- ⚡ Async/Await tracing with concurrency timeline and async stats
- 📊 Comparison Mode with side-by-side HTML, diff highlighting, and summary metrics
- 💾 Memory Leak Detection with object tracking, snapshots, growth analysis, and HTML reports
- 🎨 UI/UX fixes and improvements (module filtering, layouts, JSON export, CPU profiling panel)

---

## ⚡ Async/Await Tracing

### New APIs
- `trace_async` — Decorator to trace async functions
- `trace_scope_async()` — Async context manager to trace async code
- `gather_traced()` — Traced version of `asyncio.gather` with concurrency tracking
- `get_async_stats(graph)` — Compute async stats (max concurrency, efficiency)
- `AsyncCallGraph` — Extended call graph with async metadata

### Example
```python
import asyncio
from callflow_tracer.core.async_tracer import trace_async, trace_scope_async, gather_traced, get_async_stats

@trace_async
async def fetch(i):
    await asyncio.sleep(0.05)
    return i

async def main():
    async with trace_scope_async("async_trace.html") as graph:
        results = await gather_traced(*[fetch(i) for i in range(10)])
    stats = get_async_stats(graph)
    print(stats)

asyncio.run(main())
```

---

## 📊 Comparison Mode

### New APIs
- `compare_graphs(before, after)` — Compute function-level differences
- `export_comparison_html(before, after, output_file, label1, label2, title)` — Side-by-side HTML report

### Features
- Diff highlighting (green = improvements, red = regressions)
- Summary metrics (time saved, added/removed/modified functions)
- Detailed comparison table

### Example
```python
from callflow_tracer import trace_scope
from callflow_tracer.visualization.comparison import export_comparison_html

with trace_scope() as before:
    slow()
with trace_scope() as after:
    fast()

export_comparison_html(before, after, "comparison.html", label1="Before", label2="After")
```

---

## 💾 Memory Leak Detection

### New APIs
- `MemoryLeakDetector` — Orchestrates leak analysis and reporting
- `detect_leaks(output_file=None)` — Context manager for leak detection
- `@track_allocations` — Decorator to track allocations in a function
- `MemorySnapshot(label)` — Capture memory/object snapshots
- `find_reference_cycles()` — Detect cyclic references
- `get_memory_growth(interval, iterations)` — Monitor growth over time
- `get_top_memory_consumers(limit)` — Show top allocation sites

### Example
```python
from callflow_tracer.performance.memory_leak_detector import detect_leaks

with detect_leaks("leak_report.html") as detector:
    leaked = []
    for i in range(10):
        leaked.append([0] * 10000)
        detector.take_snapshot(f"Iter_{i}")
```

### Reports Include
- Memory growth chart (Chart.js)
- Object type distribution
- Snapshot comparisons (memory/objects diff)
- Suspected leaks and severity
- Recommendations

---

## 🎨 UI/UX Fixes in HTML Visualizations

- Module filter dropdown now functional (filters nodes/edges, smooth fit animation)
- Circular and timeline layouts fixed (correct positioning; physics toggled appropriately)
- JSON export fixed (no `network.getData()`; export uses original data with metadata)
- CPU profiling block restored with modern collapsible UI

---

## 🔧 Developer Notes

- Package version bumped to `0.2.4` in `pyproject.toml` and `callflow_tracer/__init__.py`
- New exports added to `callflow_tracer/__init__.py` for Async, Comparison, and Memory Leak APIs
- Added tests and examples for all new features

---

## 📚 Where To Start

- Async: `examples/async_example.py`
- Comparison: `examples/comparison_example.py`
- Memory Leaks: `examples/memory_leak_example.py`
- API Reference: `docs/API_DOCUMENTATION.md`

---

## ✅ Summary

v0.2.4 focuses on modern Python workloads (async), comparative performance analysis, and robustness via memory leak detection — all with polished visualization and documentation.
