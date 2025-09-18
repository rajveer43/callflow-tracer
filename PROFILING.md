# Performance Profiling with CallFlow Tracer

This guide explains how to use the performance profiling features of CallFlow Tracer.

## Table of Contents
- [Function Profiling](#function-profiling)
- [Code Section Profiling](#code-section-profiling)
- [Memory Usage Tracking](#memory-usage-tracking)
- [Example](#example)

## Function Profiling

Use the `@profile_function` decorator to profile individual functions:

```python
from callflow_tracer import profile_function

@profile_function
def my_function():
    # Your code here
    pass

# Call the function
my_function()

# Access performance data
print(my_function.performance_stats.to_dict())
```

## Code Section Profiling

Use the `profile_section` context manager to profile specific code blocks:

```python
from callflow_tracer import profile_section

with profile_section("my_code_section"):
    # Code to profile
    result = some_expensive_operation()
```

## Memory Usage Tracking

Track memory usage at any point in your code:

```python
from callflow_tracer import get_memory_usage

# Get current memory usage
mem = get_memory_usage()
print(f"Current memory: {mem['current_mb']:.2f}MB")
print(f"Peak memory: {mem['peak_mb']:.2f}MB")
```

## Example

Here's a complete example that demonstrates all features:

```python
from callflow_tracer import profile_function, profile_section, get_memory_usage
import time
import random

@profile_function
def process_data(size):
    data = [random.random() for _ in range(size)]
    time.sleep(0.1)  # Simulate I/O
    return sum(x * x for x in data)

def main():
    with profile_section("Data Processing"):
        # Process small dataset
        result1 = process_data(1000)
        
        # Check memory
        mem = get_memory_usage()
        print(f"Memory after small dataset: {mem['current_mb']:.2f}MB")
        
        # Process larger dataset
        result2 = process_data(10000)
    
    print("Profiling complete!")

if __name__ == "__main__":
    main()
```

## Performance Considerations

- The profiler adds some overhead. Use it for development and testing, not in production.
- For production, consider using the sampling profiler or disabling certain metrics.
- Memory tracking is approximate and may vary between Python implementations.

## Troubleshooting

- If you see `ModuleNotFoundError: No module named 'tracemalloc'`, ensure you're using Python 3.4 or later.
- For large applications, consider increasing the frame limit with `tracemalloc.start(25)`.

---

For more information, see the [main documentation](README.md).
