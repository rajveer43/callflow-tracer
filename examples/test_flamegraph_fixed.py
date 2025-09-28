"""
Complex version of the flamegraph test example.
This example runs a complex, deeply-nested workload with multiple branching execution paths and generates a flamegraph visualization of the call stack.
"""

import os
import sys
import time
import random
import math
import numpy as np

# Ensure local package is imported when running from the examples directory
CURRENT_DIR = os.path.dirname(__file__)
REPO_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from callflow_tracer import trace, trace_scope, get_current_graph, export_html, generate_flamegraph

@trace
def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n-1)

@trace
def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)

@trace
def generate_data(n: int = 100):
    """
    Complex function that calls itself recursively and has multiple execution paths.
    """
    data = []
    for _ in range(n):
        x = random.randint(0, 100)
        y = random.randint(0, 100)
        z = random.randint(0, 100)
        a = random.random()
        b = random.random()
        c = random.random()
        data.append((x, y, z, a, b, c))
    return data

@trace
def process_data(data):
    """
    Complex function that calls itself recursively and has multiple execution paths.
    """
    result = 0
    for item in data:
        x, y, z, a, b, c = item
        result += factorial(x) + fibonacci(y) + math.sin(z) * math.cos(z) + a * b + c * math.sqrt(z)
    return result

@trace
def main_example():
    """
    Main example function.
    """
    print("Generating data...")
    data = generate_data(10000)
    print("Processing data...")
    result = process_data(data)
    print(f"Result: {result:.4f}")

if __name__ == "__main__":
    print("Running Complex Flamegraph Example")
    print("=" * 40)

    try:
        with trace_scope("flamegraph_example") as graph:
            main_example()
            generate_flamegraph(graph, "flamegraph_example.html", width=800, height=600)

    except Exception as e:
        print(f"ERROR in main execution: {e}")
        import traceback
        traceback.print_exc()
    
    print("Example completed!")
