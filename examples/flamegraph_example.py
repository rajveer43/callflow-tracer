"""
Comprehensive examples demonstrating flamegraph visualization with callflow-tracer.

Flame graphs are useful for:
- Identifying performance bottlenecks
- Understanding call hierarchies
- Visualizing time spent in different functions
- Analyzing recursive function behavior
"""

import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from callflow_tracer import trace_scope
from callflow_tracer.flamegraph import generate_flamegraph


def example_1_simple_flamegraph():
    """Example 1: Simple function call hierarchy."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Simple Function Call Hierarchy")
    print("=" * 70)
    
    def process_step_1():
        """First processing step."""
        time.sleep(0.02)
        return [i for i in range(100)]
    
    def process_step_2():
        """Second processing step."""
        time.sleep(0.03)
        return [i ** 2 for i in range(100)]
    
    def process_step_3():
        """Third processing step."""
        time.sleep(0.01)
        return sum(range(100))
    
    def main_process():
        """Main processing function."""
        result1 = process_step_1()
        result2 = process_step_2()
        result3 = process_step_3()
        return len(result1) + len(result2) + result3
    
    # Trace the execution
    print("\nRunning simple workflow...")
    with trace_scope() as graph:
        result = main_process()
        print(f"Result: {result}")
    
    print(f"\nCaptured {len(graph.nodes)} nodes and {len(graph.edges)} edges")
    
    # Generate flamegraph
    output_file = "flamegraph_1_simple.html"
    generate_flamegraph(graph, output_file, width=1200, height=600)
    print(f"✓ Flamegraph saved to: {output_file}")
    print("  Open this file in your browser to see the visualization")


def example_2_recursive_functions():
    """Example 2: Recursive function visualization."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Recursive Function Visualization")
    print("=" * 70)
    
    def fibonacci(n):
        """Calculate fibonacci number recursively."""
        if n <= 1:
            return n
        return fibonacci(n - 1) + fibonacci(n - 2)
    
    def factorial(n):
        """Calculate factorial recursively."""
        if n <= 1:
            return 1
        return n * factorial(n - 1)
    
    def power(base, exp):
        """Calculate power recursively."""
        if exp == 0:
            return 1
        return base * power(base, exp - 1)
    
    def recursive_demo():
        """Demonstrate various recursive functions."""
        fib = fibonacci(10)
        fact = factorial(6)
        pow_result = power(2, 5)
        return fib + fact + pow_result
    
    # Trace recursive calls
    print("\nRunning recursive functions...")
    with trace_scope() as graph:
        result = recursive_demo()
        print(f"Result: {result}")
    
    print(f"\nCaptured {len(graph.nodes)} nodes (many recursive calls)")
    print(f"Call relationships: {len(graph.edges)} edges")
    
    # Generate flamegraph
    output_file = "flamegraph_2_recursive.html"
    generate_flamegraph(graph, output_file, width=1400, height=800)
    print(f"✓ Flamegraph saved to: {output_file}")
    print("  The flame graph will show the recursive call patterns")


def example_3_nested_calls():
    """Example 3: Deeply nested function calls."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Deeply Nested Function Calls")
    print("=" * 70)
    
    def level_4_operation():
        """Deepest level operation."""
        time.sleep(0.01)
        return sum(range(50))
    
    def level_3_process():
        """Level 3 processing."""
        result = level_4_operation()
        time.sleep(0.01)
        return result * 2
    
    def level_2_transform():
        """Level 2 transformation."""
        result = level_3_process()
        time.sleep(0.02)
        return result + 100
    
    def level_1_validate():
        """Level 1 validation."""
        result = level_2_transform()
        time.sleep(0.01)
        return result > 0
    
    def top_level_main():
        """Top level main function."""
        is_valid = level_1_validate()
        return "Valid" if is_valid else "Invalid"
    
    # Trace nested calls
    print("\nRunning deeply nested functions...")
    with trace_scope() as graph:
        result = top_level_main()
        print(f"Result: {result}")
    
    print(f"\nCaptured {len(graph.nodes)} nodes in hierarchy")
    
    # Generate flamegraph
    output_file = "flamegraph_3_nested.html"
    generate_flamegraph(graph, output_file, width=1200, height=700)
    print(f"✓ Flamegraph saved to: {output_file}")
    print("  The flame graph shows the call depth clearly")


def example_4_parallel_branches():
    """Example 4: Multiple parallel execution branches."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Multiple Parallel Execution Branches")
    print("=" * 70)
    
    def branch_a_step1():
        time.sleep(0.01)
        return "A1"
    
    def branch_a_step2():
        time.sleep(0.02)
        return "A2"
    
    def branch_a():
        """Branch A processing."""
        r1 = branch_a_step1()
        r2 = branch_a_step2()
        return r1 + r2
    
    def branch_b_step1():
        time.sleep(0.015)
        return "B1"
    
    def branch_b_step2():
        time.sleep(0.025)
        return "B2"
    
    def branch_b():
        """Branch B processing."""
        r1 = branch_b_step1()
        r2 = branch_b_step2()
        return r1 + r2
    
    def branch_c():
        """Branch C processing."""
        time.sleep(0.03)
        return "C"
    
    def parallel_main():
        """Execute multiple branches."""
        result_a = branch_a()
        result_b = branch_b()
        result_c = branch_c()
        return result_a + result_b + result_c
    
    # Trace parallel branches
    print("\nRunning parallel branches...")
    with trace_scope() as graph:
        result = parallel_main()
        print(f"Result: {result}")
    
    print(f"\nCaptured {len(graph.nodes)} nodes across branches")
    
    # Generate flamegraph
    output_file = "flamegraph_4_parallel.html"
    generate_flamegraph(graph, output_file, width=1400, height=700)
    print(f"✓ Flamegraph saved to: {output_file}")
    print("  The flame graph shows different execution branches side by side")


def example_5_performance_hotspots():
    """Example 5: Identifying performance hotspots."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Identifying Performance Hotspots")
    print("=" * 70)
    
    def fast_operation():
        """Quick operation."""
        return sum(range(10))
    
    def slow_operation():
        """Slow operation - this is a hotspot!"""
        time.sleep(0.1)  # Simulate slow operation
        return sum(range(1000))
    
    def medium_operation():
        """Medium speed operation."""
        time.sleep(0.03)
        return sum(range(100))
    
    def analyze_data():
        """Analyze data with mixed performance."""
        results = []
        
        # Fast operations
        for _ in range(5):
            results.append(fast_operation())
        
        # Medium operations
        for _ in range(3):
            results.append(medium_operation())
        
        # Slow operation (hotspot)
        results.append(slow_operation())
        
        return sum(results)
    
    # Trace to find hotspots
    print("\nRunning performance analysis...")
    with trace_scope() as graph:
        result = analyze_data()
        print(f"Result: {result}")
    
    print(f"\nCaptured {len(graph.nodes)} nodes")
    print("The flamegraph will highlight the slow_operation as a hotspot")
    
    # Generate flamegraph
    output_file = "flamegraph_5_hotspots.html"
    generate_flamegraph(graph, output_file, width=1400, height=700)
    print(f"✓ Flamegraph saved to: {output_file}")
    print("  Look for the widest bars - those are your performance bottlenecks!")


def example_6_real_world_pipeline():
    """Example 6: Real-world data processing pipeline."""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Real-World Data Processing Pipeline")
    print("=" * 70)
    
    def load_data(source):
        """Simulate loading data."""
        time.sleep(0.02)
        return list(range(100))
    
    def validate_data(data):
        """Validate data integrity."""
        time.sleep(0.01)
        return all(isinstance(x, int) for x in data)
    
    def clean_data(data):
        """Clean and normalize data."""
        time.sleep(0.015)
        return [x for x in data if x >= 0]
    
    def transform_data(data):
        """Transform data."""
        time.sleep(0.025)
        return [x * 2 for x in data]
    
    def aggregate_data(data):
        """Aggregate results."""
        time.sleep(0.01)
        return {
            'sum': sum(data),
            'count': len(data),
            'avg': sum(data) / len(data) if data else 0
        }
    
    def save_results(results):
        """Save results."""
        time.sleep(0.02)
        return f"Saved {results['count']} records"
    
    def data_pipeline(source):
        """Complete data processing pipeline."""
        # Load
        raw_data = load_data(source)
        
        # Validate
        if not validate_data(raw_data):
            raise ValueError("Invalid data")
        
        # Clean
        clean = clean_data(raw_data)
        
        # Transform
        transformed = transform_data(clean)
        
        # Aggregate
        results = aggregate_data(transformed)
        
        # Save
        status = save_results(results)
        
        return status
    
    # Trace the pipeline
    print("\nRunning data processing pipeline...")
    with trace_scope() as graph:
        result = data_pipeline("database")
        print(f"Result: {result}")
    
    print(f"\nCaptured {len(graph.nodes)} pipeline stages")
    
    # Generate flamegraph
    output_file = "flamegraph_6_pipeline.html"
    generate_flamegraph(graph, output_file, width=1400, height=800)
    print(f"✓ Flamegraph saved to: {output_file}")
    print("  The flame graph shows the complete pipeline flow")


def example_7_complex_algorithm():
    """Example 7: Complex algorithm with multiple paths."""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Complex Algorithm with Multiple Paths")
    print("=" * 70)
    
    def quicksort(arr):
        """Quicksort algorithm."""
        if len(arr) <= 1:
            return arr
        pivot = arr[len(arr) // 2]
        left = [x for x in arr if x < pivot]
        middle = [x for x in arr if x == pivot]
        right = [x for x in arr if x > pivot]
        return quicksort(left) + middle + quicksort(right)
    
    def binary_search(arr, target, low, high):
        """Binary search algorithm."""
        if low > high:
            return -1
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] > target:
            return binary_search(arr, target, low, mid - 1)
        else:
            return binary_search(arr, target, mid + 1, high)
    
    def merge_sort(arr):
        """Merge sort algorithm."""
        if len(arr) <= 1:
            return arr
        mid = len(arr) // 2
        left = merge_sort(arr[:mid])
        right = merge_sort(arr[mid:])
        return merge(left, right)
    
    def merge(left, right):
        """Merge two sorted arrays."""
        result = []
        i = j = 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        result.extend(left[i:])
        result.extend(right[j:])
        return result
    
    def algorithm_demo():
        """Demonstrate various algorithms."""
        # Quicksort
        unsorted = [64, 34, 25, 12, 22, 11, 90]
        sorted_quick = quicksort(unsorted.copy())
        
        # Merge sort
        sorted_merge = merge_sort(unsorted.copy())
        
        # Binary search
        target = 25
        index = binary_search(sorted_quick, target, 0, len(sorted_quick) - 1)
        
        return len(sorted_quick) + len(sorted_merge) + index
    
    # Trace algorithms
    print("\nRunning complex algorithms...")
    with trace_scope() as graph:
        result = algorithm_demo()
        print(f"Result: {result}")
    
    print(f"\nCaptured {len(graph.nodes)} nodes (recursive algorithms)")
    
    # Generate flamegraph
    output_file = "flamegraph_7_algorithms.html"
    generate_flamegraph(graph, output_file, width=1600, height=900)
    print(f"✓ Flamegraph saved to: {output_file}")
    print("  The flame graph shows the recursive nature of sorting algorithms")


def main():
    """Run all flamegraph examples."""
    print("\n" + "=" * 70)
    print(" " * 20 + "FLAMEGRAPH EXAMPLES")
    print(" " * 15 + "Callflow-Tracer Visualization")
    print("=" * 70)
    
    print("\nThis script demonstrates various use cases for flame graphs:")
    print("  1. Simple function hierarchies")
    print("  2. Recursive function patterns")
    print("  3. Deeply nested calls")
    print("  4. Parallel execution branches")
    print("  5. Performance hotspot identification")
    print("  6. Real-world data pipelines")
    print("  7. Complex algorithms")
    
    try:
        # Run all examples
        example_1_simple_flamegraph()
        example_2_recursive_functions()
        example_3_nested_calls()
        example_4_parallel_branches()
        example_5_performance_hotspots()
        example_6_real_world_pipeline()
        example_7_complex_algorithm()
        
        # Summary
        print("\n" + "=" * 70)
        print("ALL EXAMPLES COMPLETED!")
        print("=" * 70)
        
        print("\nGenerated flamegraph files:")
        print("  1. flamegraph_1_simple.html - Simple hierarchy")
        print("  2. flamegraph_2_recursive.html - Recursive patterns")
        print("  3. flamegraph_3_nested.html - Deep nesting")
        print("  4. flamegraph_4_parallel.html - Parallel branches")
        print("  5. flamegraph_5_hotspots.html - Performance hotspots")
        print("  6. flamegraph_6_pipeline.html - Data pipeline")
        print("  7. flamegraph_7_algorithms.html - Complex algorithms")
        
        print("\n📊 How to read flame graphs:")
        print("  - Width = Time spent in function")
        print("  - Height = Call stack depth")
        print("  - Click on a bar to zoom in")
        print("  - Hover to see details")
        print("  - Wider bars = Performance bottlenecks")
        
        print("\n✓ Open any .html file in your browser to explore!")
        return True
        
    except Exception as e:
        print(f"\n✗ Error during examples: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
