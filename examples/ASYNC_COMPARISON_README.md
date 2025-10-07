# Async Tracing & Comparison Mode Guide

## 🎉 New Features

CallFlow Tracer now includes two powerful new features:

1. **⚡ Async/Await Support** - Full tracing for modern async Python code
2. **📊 Comparison Mode** - Side-by-side performance comparison

---

## ⚡ Async/Await Support

### Overview

Trace async functions, track concurrent execution, and analyze async performance patterns.

### Quick Start

```python
import asyncio
from callflow_tracer.async_tracer import trace_async, trace_scope_async

@trace_async
async def my_async_function():
    await asyncio.sleep(0.1)
    return "result"

async def main():
    async with trace_scope_async("output.html") as graph:
        result = await my_async_function()

asyncio.run(main())
```

### Key Features

#### 1. **@trace_async Decorator**

Trace individual async functions:

```python
@trace_async
async def fetch_user(user_id: int):
    await asyncio.sleep(0.1)
    return {'id': user_id, 'name': f'User{user_id}'}
```

#### 2. **trace_scope_async() Context Manager**

Trace entire async code blocks:

```python
async with trace_scope_async("trace.html") as graph:
    # All async calls here are traced
    await my_async_code()
```

#### 3. **gather_traced() - Concurrent Execution**

Track concurrent task execution:

```python
from callflow_tracer.async_tracer import gather_traced

tasks = [fetch_data(i) for i in range(10)]
results = await gather_traced(*tasks)
```

This tracks:
- Which tasks run concurrently
- Maximum concurrency level
- Timeline of task execution

#### 4. **Async Statistics**

Get detailed async performance metrics:

```python
from callflow_tracer.async_tracer import get_async_stats

stats = get_async_stats(graph)
print(f"Total async time: {stats['total_async_time']:.3f}s")
print(f"Total await time: {stats['total_await_time']:.3f}s")
print(f"Active time: {stats['total_active_time']:.3f}s")
print(f"Efficiency: {stats['efficiency']:.2f}%")
print(f"Max concurrent: {stats['max_concurrent_tasks']}")
```

### Examples

Run the async examples:

```bash
cd examples
python async_example.py
```

This generates 7 HTML files demonstrating:
1. Basic async function tracing
2. Concurrent execution with gather
3. Nested async calls
4. Real-world API patterns
5. Performance analysis
6. Error handling
7. Async data pipelines

### Use Cases

**1. API Performance Analysis**
```python
@trace_async
async def fetch_from_api(endpoint: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint) as response:
            return await response.json()

async with trace_scope_async("api_trace.html") as graph:
    tasks = [fetch_from_api(f"/api/data/{i}") for i in range(10)]
    results = await gather_traced(*tasks)
```

**2. Database Query Optimization**
```python
@trace_async
async def query_database(query: str):
    async with pool.acquire() as conn:
        return await conn.fetch(query)

async with trace_scope_async("db_trace.html") as graph:
    # Trace concurrent queries
    queries = [query_database(q) for q in query_list]
    results = await gather_traced(*queries)
```

**3. Microservices Communication**
```python
@trace_async
async def call_service(service_name: str, data: dict):
    # Trace service-to-service calls
    response = await service_client.post(service_name, json=data)
    return response.json()
```

---

## 📊 Comparison Mode

### Overview

Compare two call graphs side-by-side to validate optimizations and detect regressions.

### Quick Start

```python
from callflow_tracer import trace_scope
from callflow_tracer.comparison import export_comparison_html

# Trace "before" version
with trace_scope() as graph_before:
    old_implementation()

# Trace "after" version
with trace_scope() as graph_after:
    new_implementation()

# Generate comparison
export_comparison_html(
    graph_before, graph_after,
    "comparison.html",
    label1="Before",
    label2="After"
)
```

### Key Features

#### 1. **Side-by-Side Visualization**

- Two interactive call graphs displayed together
- Synchronized viewing for easy comparison
- Independent zoom and pan controls

#### 2. **Performance Metrics**

Automatic calculation of:
- **Time Saved**: Total time difference
- **Percentage Change**: Performance improvement/regression
- **Improvements**: Functions that got faster
- **Regressions**: Functions that got slower
- **Added Functions**: New functions in "after" version
- **Removed Functions**: Functions removed in "after" version

#### 3. **Detailed Comparison Table**

Function-by-function breakdown showing:
- Execution time before/after
- Call count before/after
- Time difference (absolute and percentage)
- Status (modified/added/removed)

#### 4. **Visual Indicators**

- 🟢 **Green rows**: Performance improvements
- 🔴 **Red rows**: Performance regressions
- **Color-coded badges**: Modified/Added/Removed status

### Examples

Run the comparison examples:

```bash
cd examples
python comparison_example.py
```

This generates 6 HTML files demonstrating:
1. Fibonacci optimization (recursion vs memoization)
2. List processing optimization
3. Caching improvement
4. Algorithm complexity (O(n²) vs O(n log n))
5. Data structure optimization (list vs set)
6. Real-world API optimization

### Use Cases

**1. Algorithm Optimization**
```python
# Before: O(n²) bubble sort
with trace_scope() as before:
    bubble_sort(data)

# After: O(n log n) built-in sort
with trace_scope() as after:
    sorted(data)

export_comparison_html(before, after, "sort_comparison.html")
```

**2. Caching Validation**
```python
# Before: No cache
with trace_scope() as before:
    for item in items:
        expensive_calculation(item)

# After: With cache
with trace_scope() as after:
    for item in items:
        cached_calculation(item)

export_comparison_html(before, after, "cache_comparison.html")
```

**3. Refactoring Validation**
```python
# Before refactoring
with trace_scope() as before:
    old_architecture()

# After refactoring
with trace_scope() as after:
    new_architecture()

# Ensure no regressions
comparison = compare_graphs(before, after)
assert comparison['summary']['regressions'] == 0
```

**4. A/B Testing**
```python
# Version A
with trace_scope() as version_a:
    algorithm_a(data)

# Version B
with trace_scope() as version_b:
    algorithm_b(data)

export_comparison_html(
    version_a, version_b,
    "ab_test.html",
    label1="Algorithm A",
    label2="Algorithm B"
)
```

---

## 🧪 Testing

### Run Async Tests

```bash
cd tests
python test_async_tracing.py
```

Tests include:
- Basic async function tracing
- Multiple async calls
- Concurrent execution
- Nested async calls
- Exception handling
- Export to HTML
- Async statistics
- Mixed sync/async
- Parameters handling
- Concurrent tracking

### Run Comparison Tests

```bash
cd tests
python test_comparison_mode.py
```

Tests include:
- Basic comparison
- Export to HTML
- Added functions detection
- Removed functions detection
- Comparison statistics
- Regression detection
- Large comparisons
- Identical graphs
- Custom labels
- Full workflow

---

## 📚 API Reference

### Async Tracing

#### `@trace_async`
```python
@trace_async
async def my_function():
    pass
```
Decorator for tracing async functions.

#### `trace_scope_async(output_file=None)`
```python
async with trace_scope_async("output.html") as graph:
    await my_async_code()
```
Async context manager for tracing code blocks.

#### `gather_traced(*awaitables)`
```python
results = await gather_traced(task1, task2, task3)
```
Traced version of `asyncio.gather()`.

#### `get_async_stats(graph)`
```python
stats = get_async_stats(graph)
```
Returns async-specific statistics.

**Returns:**
- `total_async_functions`: Number of async functions
- `total_async_time`: Total execution time
- `total_await_time`: Time spent waiting
- `total_active_time`: Active execution time
- `efficiency`: Percentage of active time
- `max_concurrent_tasks`: Maximum concurrency
- `timeline_events`: Number of timeline events

### Comparison Mode

#### `compare_graphs(graph1, graph2, label1="Before", label2="After")`
```python
comparison = compare_graphs(graph_before, graph_after)
```
Compare two call graphs and return statistics.

**Returns:**
```python
{
    'summary': {
        'total_time_before': float,
        'total_time_after': float,
        'time_saved': float,
        'time_saved_pct': float,
        'improvements': int,
        'regressions': int,
        'nodes_added': int,
        'nodes_removed': int,
        'nodes_modified': int
    },
    'node_comparisons': [...],
    'top_improvements': [...],
    'top_regressions': [...]
}
```

#### `export_comparison_html(graph1, graph2, output_path, label1="Before", label2="After", title="Comparison")`
```python
export_comparison_html(
    graph_before, graph_after,
    "comparison.html",
    label1="Version 1.0",
    label2="Version 2.0",
    title="Performance Comparison"
)
```
Export side-by-side comparison to HTML.

---

## 💡 Best Practices

### Async Tracing

1. **Use `@trace_async` for async functions only**
   - Use `@trace` for sync functions
   - Don't mix decorators

2. **Use `gather_traced()` for concurrent operations**
   - Provides better concurrency tracking
   - Shows timeline of execution

3. **Check async statistics**
   - Low efficiency? Too much await time
   - High concurrency? Good parallelization

### Comparison Mode

1. **Use consistent test data**
   - Same input for both versions
   - Ensures fair comparison

2. **Run multiple times**
   - Average results for accuracy
   - Reduce timing variance

3. **Check for regressions**
   - Not all changes are improvements
   - Validate before deploying

4. **Document optimizations**
   - Save comparison HTML files
   - Track performance over time

---

## 🎯 Tips & Tricks

### Async Tracing

**Tip 1: Identify Bottlenecks**
```python
stats = get_async_stats(graph)
if stats['efficiency'] < 50:
    print("Warning: Low efficiency - too much waiting!")
```

**Tip 2: Optimize Concurrency**
```python
# Before: Sequential
for item in items:
    await process(item)

# After: Concurrent
tasks = [process(item) for item in items]
await gather_traced(*tasks)
```

**Tip 3: Monitor Concurrency Limits**
```python
stats = get_async_stats(graph)
if stats['max_concurrent_tasks'] > 100:
    print("Warning: Too many concurrent tasks!")
```

### Comparison Mode

**Tip 1: Focus on Top Changes**
```python
comparison = compare_graphs(before, after)
for improvement in comparison['top_improvements'][:5]:
    print(f"{improvement['name']}: {improvement['time_diff']:.4f}s saved")
```

**Tip 2: Automated Regression Testing**
```python
comparison = compare_graphs(before, after)
assert comparison['summary']['time_saved'] > 0, "No improvement!"
assert comparison['summary']['regressions'] == 0, "Regressions detected!"
```

**Tip 3: Track Optimization History**
```python
# Save comparisons with timestamps
import datetime
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
export_comparison_html(
    before, after,
    f"comparison_{timestamp}.html"
)
```

---

## 🐛 Troubleshooting

### Async Tracing Issues

**Issue: "TypeError: object is not an async function"**
- Solution: Use `@trace_async` only on async functions
- Use `@trace` for regular functions

**Issue: Low efficiency reported**
- Cause: Too much time spent waiting
- Solution: Increase concurrency, optimize I/O

**Issue: Missing concurrent execution data**
- Cause: Not using `gather_traced()`
- Solution: Replace `asyncio.gather()` with `gather_traced()`

### Comparison Mode Issues

**Issue: Comparison shows no differences**
- Cause: Both versions are identical
- Solution: Verify you're tracing different code

**Issue: Unexpected regressions**
- Cause: Timing variance or actual regression
- Solution: Run multiple times, check for bugs

**Issue: Missing functions in comparison**
- Cause: Functions not called in one version
- Solution: Ensure consistent test coverage

---

## 📖 Additional Resources

- **Main README**: `../README.md`
- **API Documentation**: `../docs/API_DOCUMENTATION.md`
- **Testing Guide**: `../TESTING_GUIDE.md`
- **Flamegraph Guide**: `FLAMEGRAPH_README.md`
- **Jupyter Guide**: `JUPYTER_README.md`

---

## 🎉 Summary

### Async Tracing
✅ Trace async functions with `@trace_async`  
✅ Use `trace_scope_async()` for code blocks  
✅ Track concurrency with `gather_traced()`  
✅ Analyze performance with `get_async_stats()`  

### Comparison Mode
✅ Compare graphs with `compare_graphs()`  
✅ Export HTML with `export_comparison_html()`  
✅ Validate optimizations automatically  
✅ Detect regressions before deployment  

**Start optimizing your async code today! 🚀**
