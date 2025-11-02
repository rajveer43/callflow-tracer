"""
Demo script for testing callflow-tracer CLI commands.

This script demonstrates various function call patterns that can be traced.

Usage examples:
    callflow-tracer trace cli_demo.py
    callflow-tracer flamegraph cli_demo.py
    callflow-tracer profile cli_demo.py --memory
    callflow-tracer memory-leak cli_demo.py
"""

import time
import random


def fast_function():
    """A fast function that completes quickly."""
    return sum(range(100))


def slow_function():
    """A slow function that takes noticeable time."""
    time.sleep(0.1)
    total = 0
    for i in range(1000):
        total += i ** 2
    return total


def recursive_fibonacci(n):
    """Recursive function for demonstration."""
    if n <= 1:
        return n
    return recursive_fibonacci(n - 1) + recursive_fibonacci(n - 2)


def data_processor(data):
    """Process some data."""
    result = []
    for item in data:
        processed = item * 2 + random.random()
        result.append(processed)
    return result


def nested_calls():
    """Function that makes nested calls."""
    data = [random.random() for _ in range(100)]
    processed = data_processor(data)
    return sum(processed)


def memory_intensive():
    """Function that allocates memory."""
    large_list = [random.random() for _ in range(10000)]
    return sum(large_list) / len(large_list)


def main():
    """Main function demonstrating various patterns."""
    print("Starting CLI demo...")
    
    # Fast operations
    print("Running fast operations...")
    for _ in range(10):
        fast_function()
    
    # Slow operations
    print("Running slow operations...")
    for _ in range(3):
        slow_function()
    
    # Recursive calls
    print("Running recursive operations...")
    fib_result = recursive_fibonacci(10)
    print(f"Fibonacci(10) = {fib_result}")
    
    # Nested calls
    print("Running nested operations...")
    for _ in range(5):
        nested_calls()
    
    # Memory intensive
    print("Running memory intensive operations...")
    for _ in range(3):
        memory_intensive()
    
    print("Demo complete!")
    return "Success"


if __name__ == "__main__":
    result = main()
    print(f"Result: {result}")
