"""
Comprehensive demo script showcasing all callflow-tracer CLI capabilities.

This script includes various patterns that demonstrate:
- Function call hierarchies
- Performance bottlenecks
- Memory allocation patterns
- Recursive calls
- Nested function calls

CLI Usage Examples:
-------------------

1. Basic Trace:
   callflow-tracer trace cli_comprehensive_demo.py

2. Flamegraph:
   callflow-tracer flamegraph cli_comprehensive_demo.py

3. Performance Profile:
   callflow-tracer profile cli_comprehensive_demo.py --memory --cpu

4. Memory Leak Detection:
   callflow-tracer memory-leak cli_comprehensive_demo.py --threshold 5

5. Generate JSON for Comparison:
   callflow-tracer trace cli_comprehensive_demo.py --format json -o trace.json

6. 3D Visualization:
   callflow-tracer trace cli_comprehensive_demo.py --3d

7. With Script Arguments:
   callflow-tracer trace cli_comprehensive_demo.py --iterations 5 --verbose
"""

import time
import random
import sys
import argparse


class DataProcessor:
    """Example class with various methods."""
    
    def __init__(self, name):
        self.name = name
        self.data = []
    
    def add_data(self, value):
        """Add data to the processor."""
        self.data.append(value)
    
    def process(self):
        """Process all data."""
        results = []
        for item in self.data:
            result = self._transform(item)
            results.append(result)
        return results
    
    def _transform(self, value):
        """Transform a single value."""
        # Simulate some computation
        return value ** 2 + random.random()


def fast_operation():
    """A fast operation that completes quickly."""
    return sum(range(100))


def slow_operation():
    """A slow operation that takes noticeable time."""
    time.sleep(0.05)
    total = 0
    for i in range(500):
        total += i ** 2
    return total


def very_slow_operation():
    """A very slow operation."""
    time.sleep(0.2)
    result = 0
    for i in range(1000):
        result += slow_computation(i)
    return result


def slow_computation(n):
    """Simulate slow computation."""
    return sum(range(n)) / max(n, 1)


def recursive_factorial(n):
    """Recursive factorial calculation."""
    if n <= 1:
        return 1
    return n * recursive_factorial(n - 1)


def fibonacci_recursive(n):
    """Recursive Fibonacci (intentionally inefficient)."""
    if n <= 1:
        return n
    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)


def fibonacci_iterative(n):
    """Iterative Fibonacci (efficient)."""
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b


def memory_allocator(size_mb):
    """Allocate memory."""
    # Allocate approximately size_mb megabytes
    num_elements = int(size_mb * 1024 * 1024 / 8)  # 8 bytes per float
    data = [random.random() for _ in range(num_elements)]
    return sum(data) / len(data)


def nested_function_calls():
    """Demonstrate nested function calls."""
    result1 = level1_function()
    result2 = level1_function()
    return result1 + result2


def level1_function():
    """Level 1 of nested calls."""
    return level2_function() + level2_function()


def level2_function():
    """Level 2 of nested calls."""
    return level3_function() * 2


def level3_function():
    """Level 3 of nested calls."""
    return fast_operation()


def data_processing_pipeline(data_size):
    """Simulate a data processing pipeline."""
    # Stage 1: Generate data
    data = generate_data(data_size)
    
    # Stage 2: Transform data
    transformed = transform_data(data)
    
    # Stage 3: Aggregate data
    result = aggregate_data(transformed)
    
    return result


def generate_data(size):
    """Generate random data."""
    return [random.random() for _ in range(size)]


def transform_data(data):
    """Transform data."""
    return [x ** 2 + x for x in data]


def aggregate_data(data):
    """Aggregate data."""
    return {
        'sum': sum(data),
        'mean': sum(data) / len(data),
        'min': min(data),
        'max': max(data)
    }


def mixed_workload(iterations):
    """Run a mixed workload."""
    results = []
    
    for i in range(iterations):
        # Fast operations
        results.append(fast_operation())
        
        # Slow operations
        if i % 2 == 0:
            results.append(slow_operation())
        
        # Very slow operations (less frequent)
        if i % 5 == 0:
            results.append(very_slow_operation())
        
        # Recursive calls
        if i % 3 == 0:
            results.append(recursive_factorial(10))
        
        # Memory allocation
        if i % 4 == 0:
            results.append(memory_allocator(1))
    
    return sum(results)


def class_based_processing():
    """Demonstrate class-based processing."""
    processor = DataProcessor("demo")
    
    # Add data
    for i in range(50):
        processor.add_data(random.random() * 100)
    
    # Process data
    results = processor.process()
    
    return sum(results)


def comparison_demo():
    """Compare recursive vs iterative approaches."""
    print("  Comparing Fibonacci implementations...")
    
    # Recursive (slow)
    start = time.time()
    result_recursive = fibonacci_recursive(15)
    time_recursive = time.time() - start
    
    # Iterative (fast)
    start = time.time()
    result_iterative = fibonacci_iterative(15)
    time_iterative = time.time() - start
    
    print(f"    Recursive: {result_recursive} in {time_recursive:.6f}s")
    print(f"    Iterative: {result_iterative} in {time_iterative:.6f}s")
    
    return result_recursive, result_iterative


def main(args):
    """Main function orchestrating the demo."""
    print("=" * 60)
    print("CallFlow Tracer - Comprehensive CLI Demo")
    print("=" * 60)
    print()
    
    iterations = args.iterations if args else 3
    verbose = args.verbose if args else False
    
    print(f"Running with {iterations} iterations...")
    print()
    
    # 1. Fast operations
    if verbose:
        print("1. Running fast operations...")
    for _ in range(10):
        fast_operation()
    
    # 2. Slow operations
    if verbose:
        print("2. Running slow operations...")
    for _ in range(3):
        slow_operation()
    
    # 3. Very slow operations
    if verbose:
        print("3. Running very slow operations...")
    very_slow_operation()
    
    # 4. Recursive operations
    if verbose:
        print("4. Running recursive operations...")
    factorial_result = recursive_factorial(10)
    if verbose:
        print(f"   Factorial(10) = {factorial_result}")
    
    # 5. Nested function calls
    if verbose:
        print("5. Running nested function calls...")
    nested_result = nested_function_calls()
    
    # 6. Data processing pipeline
    if verbose:
        print("6. Running data processing pipeline...")
    pipeline_result = data_processing_pipeline(100)
    if verbose:
        print(f"   Pipeline result: {pipeline_result}")
    
    # 7. Mixed workload
    if verbose:
        print("7. Running mixed workload...")
    mixed_result = mixed_workload(iterations)
    if verbose:
        print(f"   Mixed workload result: {mixed_result}")
    
    # 8. Class-based processing
    if verbose:
        print("8. Running class-based processing...")
    class_result = class_based_processing()
    
    # 9. Comparison demo
    if verbose:
        print("9. Running comparison demo...")
    comparison_demo()
    
    # 10. Memory allocation
    if verbose:
        print("10. Running memory allocation test...")
    memory_result = memory_allocator(5)
    
    print()
    print("=" * 60)
    print("Demo Complete!")
    print("=" * 60)
    print()
    print("Try these CLI commands:")
    print("  callflow-tracer trace cli_comprehensive_demo.py")
    print("  callflow-tracer flamegraph cli_comprehensive_demo.py")
    print("  callflow-tracer profile cli_comprehensive_demo.py --memory")
    print("  callflow-tracer memory-leak cli_comprehensive_demo.py")
    print()
    
    return {
        'factorial': factorial_result,
        'nested': nested_result,
        'pipeline': pipeline_result,
        'mixed': mixed_result,
        'class': class_result,
        'memory': memory_result
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Comprehensive CLI demo")
    parser.add_argument('--iterations', type=int, default=3, help='Number of iterations')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    result = main(args)
    print(f"Final result: {result}")
