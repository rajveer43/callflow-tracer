"""
Comparison Mode Examples

This file demonstrates the comparison mode for analyzing performance
improvements between different versions of code.

Examples include:
1. Basic before/after comparison
2. Algorithm optimization comparison
3. Caching improvement comparison
4. Data structure optimization
5. Real-world optimization scenarios
"""

import time
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from callflow_tracer import trace_scope
from callflow_tracer.comparison import compare_graphs, export_comparison_html


# Example 1: Basic Fibonacci Optimization
print("="*70)
print("EXAMPLE 1: Fibonacci Optimization (Recursion vs Memoization)")
print("="*70)

# Before: Naive recursion
def fibonacci_slow(n):
    """Slow recursive fibonacci."""
    if n <= 1:
        return n
    return fibonacci_slow(n-1) + fibonacci_slow(n-2)


# After: Memoized version
_fib_cache = {}

def fibonacci_fast(n):
    """Fast memoized fibonacci."""
    if n in _fib_cache:
        return _fib_cache[n]
    if n <= 1:
        return n
    result = fibonacci_fast(n-1) + fibonacci_fast(n-2)
    _fib_cache[n] = result
    return result


def example1_fibonacci():
    """Compare fibonacci implementations."""
    print("\nTracing slow version...")
    with trace_scope() as graph_before:
        result = fibonacci_slow(15)
        print(f"  fibonacci_slow(15) = {result}")
    
    print("Tracing fast version...")
    with trace_scope() as graph_after:
        result = fibonacci_fast(15)
        print(f"  fibonacci_fast(15) = {result}")
    
    # Export comparison
    export_comparison_html(
        graph_before, graph_after,
        "comparison_example1_fibonacci.html",
        label1="Naive Recursion",
        label2="Memoization",
        title="Fibonacci Optimization Comparison"
    )
    
    # Print statistics
    comparison = compare_graphs(graph_before, graph_after)
    summary = comparison['summary']
    
    print(f"\n📊 Results:")
    print(f"  Time saved: {summary['time_saved']:.4f}s ({summary['time_saved_pct']:.1f}%)")
    print(f"  Improvements: {summary['improvements']}")
    print(f"✓ Output: comparison_example1_fibonacci.html\n")


# Example 2: List Processing Optimization
print("="*70)
print("EXAMPLE 2: List Processing Optimization")
print("="*70)

# Before: Manual iteration
def process_list_slow(data):
    """Slow list processing with manual loops."""
    result = []
    for item in data:
        time.sleep(0.001)  # Simulate processing
        if item % 2 == 0:
            result.append(item * 2)
    return result


def sum_list_slow(data):
    """Slow sum calculation."""
    total = 0
    for item in data:
        time.sleep(0.0005)
        total += item
    return total


# After: Built-in functions
def process_list_fast(data):
    """Fast list processing with list comprehension."""
    return [item * 2 for item in data if item % 2 == 0]


def sum_list_fast(data):
    """Fast sum using built-in."""
    return sum(data)


def example2_list_processing():
    """Compare list processing implementations."""
    test_data = list(range(50))
    
    print("\nTracing slow version...")
    with trace_scope() as graph_before:
        processed = process_list_slow(test_data)
        total = sum_list_slow(processed)
        print(f"  Processed {len(processed)} items, sum = {total}")
    
    print("Tracing fast version...")
    with trace_scope() as graph_after:
        processed = process_list_fast(test_data)
        total = sum_list_fast(processed)
        print(f"  Processed {len(processed)} items, sum = {total}")
    
    export_comparison_html(
        graph_before, graph_after,
        "comparison_example2_list_processing.html",
        label1="Manual Loops",
        label2="Built-in Functions",
        title="List Processing Optimization"
    )
    
    comparison = compare_graphs(graph_before, graph_after)
    summary = comparison['summary']
    
    print(f"\n📊 Results:")
    print(f"  Time saved: {summary['time_saved']:.4f}s ({summary['time_saved_pct']:.1f}%)")
    print(f"✓ Output: comparison_example2_list_processing.html\n")


# Example 3: Caching Improvement
print("="*70)
print("EXAMPLE 3: Caching Improvement")
print("="*70)

# Before: No caching
def expensive_calculation(n):
    """Expensive calculation without caching."""
    time.sleep(0.02)  # Simulate expensive operation
    return n ** 2


def process_with_no_cache(data):
    """Process data without caching."""
    results = []
    for item in data:
        result = expensive_calculation(item)
        results.append(result)
    return results


# After: With caching
_calc_cache = {}

def expensive_calculation_cached(n):
    """Expensive calculation with caching."""
    if n in _calc_cache:
        return _calc_cache[n]
    time.sleep(0.02)  # Simulate expensive operation
    result = n ** 2
    _calc_cache[n] = result
    return result


def process_with_cache(data):
    """Process data with caching."""
    results = []
    for item in data:
        result = expensive_calculation_cached(item)
        results.append(result)
    return results


def example3_caching():
    """Compare caching implementations."""
    # Use repeated data to show cache benefits
    test_data = [1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2, 3]
    
    print("\nTracing without cache...")
    with trace_scope() as graph_before:
        results = process_with_no_cache(test_data)
        print(f"  Processed {len(results)} items")
    
    print("Tracing with cache...")
    _calc_cache.clear()  # Clear cache before test
    with trace_scope() as graph_after:
        results = process_with_cache(test_data)
        print(f"  Processed {len(results)} items (with caching)")
    
    export_comparison_html(
        graph_before, graph_after,
        "comparison_example3_caching.html",
        label1="No Caching",
        label2="With Caching",
        title="Caching Optimization Comparison"
    )
    
    comparison = compare_graphs(graph_before, graph_after)
    summary = comparison['summary']
    
    print(f"\n📊 Results:")
    print(f"  Time saved: {summary['time_saved']:.4f}s ({summary['time_saved_pct']:.1f}%)")
    print(f"  Cache hits saved significant time!")
    print(f"✓ Output: comparison_example3_caching.html\n")


# Example 4: Algorithm Complexity
print("="*70)
print("EXAMPLE 4: Algorithm Complexity (O(n²) vs O(n log n))")
print("="*70)

# Before: Bubble sort O(n²)
def bubble_sort(arr):
    """Slow bubble sort."""
    arr = arr.copy()
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr


# After: Built-in sort O(n log n)
def fast_sort(arr):
    """Fast built-in sort."""
    return sorted(arr)


def example4_sorting():
    """Compare sorting algorithms."""
    import random
    test_data = [random.randint(1, 100) for _ in range(100)]
    
    print("\nTracing bubble sort...")
    with trace_scope() as graph_before:
        sorted_data = bubble_sort(test_data)
        print(f"  Sorted {len(sorted_data)} items with bubble sort")
    
    print("Tracing fast sort...")
    with trace_scope() as graph_after:
        sorted_data = fast_sort(test_data)
        print(f"  Sorted {len(sorted_data)} items with built-in sort")
    
    export_comparison_html(
        graph_before, graph_after,
        "comparison_example4_sorting.html",
        label1="Bubble Sort O(n²)",
        label2="Built-in Sort O(n log n)",
        title="Sorting Algorithm Comparison"
    )
    
    comparison = compare_graphs(graph_before, graph_after)
    summary = comparison['summary']
    
    print(f"\n📊 Results:")
    print(f"  Time saved: {summary['time_saved']:.4f}s ({summary['time_saved_pct']:.1f}%)")
    print(f"  Algorithm complexity matters!")
    print(f"✓ Output: comparison_example4_sorting.html\n")


# Example 5: Data Structure Optimization
print("="*70)
print("EXAMPLE 5: Data Structure Optimization (List vs Set)")
print("="*70)

# Before: Using list for membership testing
def find_duplicates_slow(data):
    """Find duplicates using list."""
    seen = []
    duplicates = []
    for item in data:
        if item in seen:  # O(n) lookup in list
            if item not in duplicates:
                duplicates.append(item)
        else:
            seen.append(item)
    return duplicates


# After: Using set for membership testing
def find_duplicates_fast(data):
    """Find duplicates using set."""
    seen = set()
    duplicates = set()
    for item in data:
        if item in seen:  # O(1) lookup in set
            duplicates.add(item)
        else:
            seen.add(item)
    return list(duplicates)


def example5_data_structures():
    """Compare data structure choices."""
    import random
    test_data = [random.randint(1, 50) for _ in range(200)]
    
    print("\nTracing with list...")
    with trace_scope() as graph_before:
        dups = find_duplicates_slow(test_data)
        print(f"  Found {len(dups)} duplicates using list")
    
    print("Tracing with set...")
    with trace_scope() as graph_after:
        dups = find_duplicates_fast(test_data)
        print(f"  Found {len(dups)} duplicates using set")
    
    export_comparison_html(
        graph_before, graph_after,
        "comparison_example5_data_structures.html",
        label1="List (O(n) lookup)",
        label2="Set (O(1) lookup)",
        title="Data Structure Optimization"
    )
    
    comparison = compare_graphs(graph_before, graph_after)
    summary = comparison['summary']
    
    print(f"\n📊 Results:")
    print(f"  Time saved: {summary['time_saved']:.4f}s ({summary['time_saved_pct']:.1f}%)")
    print(f"  Right data structure = better performance!")
    print(f"✓ Output: comparison_example5_data_structures.html\n")


# Example 6: Real-world Scenario
print("="*70)
print("EXAMPLE 6: Real-world Web API Optimization")
print("="*70)

# Before: Sequential processing
def fetch_user_data_slow(user_id):
    """Simulate slow API call."""
    time.sleep(0.05)
    return {'id': user_id, 'name': f'User{user_id}'}


def fetch_user_orders_slow(user_id):
    """Simulate slow database query."""
    time.sleep(0.08)
    return [f'Order{i}' for i in range(3)]


def get_user_profile_slow(user_id):
    """Get user profile sequentially."""
    user = fetch_user_data_slow(user_id)
    orders = fetch_user_orders_slow(user_id)
    return {**user, 'orders': orders}


def process_users_slow(user_ids):
    """Process users sequentially."""
    profiles = []
    for uid in user_ids:
        profile = get_user_profile_slow(uid)
        profiles.append(profile)
    return profiles


# After: Optimized with batching
def fetch_users_batch(user_ids):
    """Batch fetch users."""
    time.sleep(0.1)  # Single batch call
    return [{'id': uid, 'name': f'User{uid}'} for uid in user_ids]


def fetch_orders_batch(user_ids):
    """Batch fetch orders."""
    time.sleep(0.15)  # Single batch call
    return {uid: [f'Order{i}' for i in range(3)] for uid in user_ids}


def process_users_fast(user_ids):
    """Process users with batching."""
    users = fetch_users_batch(user_ids)
    orders_map = fetch_orders_batch(user_ids)
    
    profiles = []
    for user in users:
        profile = {**user, 'orders': orders_map[user['id']]}
        profiles.append(profile)
    return profiles


def example6_realworld():
    """Compare real-world optimization."""
    user_ids = [1, 2, 3, 4, 5]
    
    print("\nTracing sequential processing...")
    with trace_scope() as graph_before:
        profiles = process_users_slow(user_ids)
        print(f"  Processed {len(profiles)} user profiles sequentially")
    
    print("Tracing batch processing...")
    with trace_scope() as graph_after:
        profiles = process_users_fast(user_ids)
        print(f"  Processed {len(profiles)} user profiles with batching")
    
    export_comparison_html(
        graph_before, graph_after,
        "comparison_example6_realworld.html",
        label1="Sequential Processing",
        label2="Batch Processing",
        title="Real-world API Optimization"
    )
    
    comparison = compare_graphs(graph_before, graph_after)
    summary = comparison['summary']
    
    print(f"\n📊 Results:")
    print(f"  Time saved: {summary['time_saved']:.4f}s ({summary['time_saved_pct']:.1f}%)")
    print(f"  Batching reduces API calls!")
    print(f"✓ Output: comparison_example6_realworld.html\n")


# Main execution
def run_all_examples():
    """Run all comparison examples."""
    print("\n" + "="*70)
    print("COMPARISON MODE EXAMPLES")
    print("="*70 + "\n")
    
    examples = [
        example1_fibonacci,
        example2_list_processing,
        example3_caching,
        example4_sorting,
        example5_data_structures,
        example6_realworld,
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"❌ Error in {example.__name__}: {e}")
            import traceback
            traceback.print_exc()
    
    print("="*70)
    print("✅ ALL EXAMPLES COMPLETED!")
    print("="*70)
    print("\nGenerated files:")
    print("  - comparison_example1_fibonacci.html")
    print("  - comparison_example2_list_processing.html")
    print("  - comparison_example3_caching.html")
    print("  - comparison_example4_sorting.html")
    print("  - comparison_example5_data_structures.html")
    print("  - comparison_example6_realworld.html")
    print("\nOpen these files in your browser to see side-by-side comparisons!")


if __name__ == "__main__":
    run_all_examples()
