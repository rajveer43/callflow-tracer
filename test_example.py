#!/usr/bin/env python3
"""
Test script for callflow-tracer package.
This demonstrates the basic functionality and creates sample output files.
"""

import sys
import os
import time
import random

# Add the package to the path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'callflow_tracer'))

from callflow_tracer import trace, trace_scope, export_json, export_html


@trace
def fibonacci(n):
    """Calculate Fibonacci number recursively."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)


@trace
def quicksort(arr):
    """Sort array using quicksort algorithm."""
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quicksort(left) + middle + quicksort(right)


@trace
def binary_search(arr, target):
    """Binary search implementation."""
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1


@trace
def process_data(data):
    """Process data through multiple steps."""
    # Simulate data processing
    time.sleep(0.01)  # 10ms delay
    
    # Sort the data
    sorted_data = quicksort(data)
    
    # Search for a specific value
    target = sorted_data[len(sorted_data) // 2]
    index = binary_search(sorted_data, target)
    
    return {
        'sorted': sorted_data,
        'target': target,
        'index': index,
        'length': len(sorted_data)
    }


@trace
def generate_test_data(size=100):
    """Generate random test data."""
    return [random.randint(1, 1000) for _ in range(size)]


@trace
def main():
    """Main function that orchestrates the test."""
    print("🧠 CallFlow Tracer Test")
    print("=" * 50)
    
    # Generate test data
    print("Generating test data...")
    data = generate_test_data(50)
    print(f"Generated {len(data)} random numbers")
    
    # Process the data
    print("Processing data...")
    result = process_data(data)
    print(f"Processed data: {result['length']} items, target at index {result['index']}")
    
    # Calculate Fibonacci
    print("Calculating Fibonacci...")
    fib_result = fibonacci(8)
    print(f"Fibonacci(8) = {fib_result}")
    
    print("\n✅ Test completed successfully!")
    print("Check the generated HTML file: test_output.html")


def test_decorator_approach():
    """Test using the @trace decorator approach."""
    print("\n🔍 Testing @trace decorator approach...")
    
    with trace_scope("decorator_test.html"):
        main()


def test_context_manager_approach():
    """Test using the trace_scope context manager approach."""
    print("\n🔍 Testing trace_scope context manager approach...")
    
    def some_function():
        """A function to trace."""
        time.sleep(0.005)
        return "Hello from traced function!"
    
    def another_function():
        """Another function to trace."""
        result = some_function()
        return result.upper()
    
    with trace_scope("context_test.html"):
        result = another_function()
        print(f"Result: {result}")


def test_export_formats():
    """Test different export formats."""
    print("\n🔍 Testing export formats...")
    
    with trace_scope() as graph:
        # Run some traced code
        fibonacci(5)
        quicksort([3, 1, 4, 1, 5, 9, 2, 6])
    
    # Export to JSON
    export_json(graph, "test_output.json")
    print("✅ Exported to JSON: test_output.json")
    
    # Export to HTML
    export_html(graph, "test_output.html", title="CallFlow Tracer Test Results")
    print("✅ Exported to HTML: test_output.html")


if __name__ == "__main__":
    print("🚀 Starting CallFlow Tracer Tests")
    print("=" * 50)
    
    try:
        # Test different approaches
        test_decorator_approach()
        test_context_manager_approach()
        test_export_formats()
        
        print("\n🎉 All tests completed successfully!")
        print("\nGenerated files:")
        print("- decorator_test.html")
        print("- context_test.html") 
        print("- test_output.json")
        print("- test_output.html")
        print("\nOpen the HTML files in your browser to see the interactive graphs!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
