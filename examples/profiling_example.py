"""
Example demonstrating the performance profiling features of callflow-tracer.

This example shows how to use:
1. @profile_function decorator
2. profile_section context manager
3. get_memory_usage() function
"""

import time
import random
import numpy as np
import os
import sys

# Ensure local package is imported when running from the examples directory
CURRENT_DIR = os.path.dirname(__file__)
REPO_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from callflow_tracer import profile_function, profile_section, get_memory_usage
from callflow_tracer import trace_scope
from callflow_tracer import export_html

def generate_large_data(size_mb):
    """Generate a large numpy array of the given size in MB."""
    # Each float64 is 8 bytes, so we need size_mb * 1024 * 1024 / 8 elements
    num_elements = int(size_mb * 1024 * 1024 / 8)
    return np.random.random(num_elements)

@profile_function
def process_data(data_size: int) -> float:
    """Process some data with artificial CPU and memory usage."""
    # Allocate some memory
    data = [random.random() for _ in range(data_size)]
    
    # Do some CPU-intensive work
    total = 0.0
    for i in range(len(data)):
        # Simulate CPU work
        total += sum(data[:i+1]) / (i+1)
    
    # Simulate I/O wait
    time.sleep(0.1)
    
    return total

def example_with_sections():
    """Example using profile_section context manager."""
    with profile_section("Data Processing"):
        print("Processing small dataset...")
        result1 = process_data(100)
        
        # Check memory usage
        mem = get_memory_usage()
        print(f"\nCurrent memory usage: {mem['current_mb']:.2f}MB")
        
        print("\nProcessing large dataset...")
        result2 = process_data(100)
        
        # Allocate some large data
        print("\nAllocating large numpy array...")
        large_data = generate_large_data(100)  # 10MB
        
        # Check memory usage after large allocation
        mem = get_memory_usage()
        print(f"Memory after large allocation: {mem['current_mb']:.2f}MB")
        
        # Do some computation with the large data
        print("\nComputing with large data...")
        result3 = np.mean(large_data) * result2
        
        # Simulate I/O operation
        with profile_section("I/O Operation"):
            print("\nPerforming I/O operation...")
            time.sleep(0.2)
    
    return result1, result2, result3

if __name__ == "__main__":
    print("=== Starting Performance Profiling Example ===\n")
    
    # Example 1: Using the decorator
    print("1. Profiling with @profile_function decorator:")
    result = process_data(5000)
    print(f"Result: {result:.6f}")
    
    # Example 2: Using nested context managers
    print("\n2. Profiling with nested profile_section context managers:")
    data1, data2, data3 = example_with_sections()
    print(f"Results: {data1:.6f}, {data2:.6f}, {data3:.6f}")

    # Example 3: Export interactive call graph (HTML)
    print("\n3. Visualizing as interactive call graph (exports to callgraph.html):")
    # output_html = os.path.join(REPO_ROOT, "dist", "callgraph.html")
    # Collect profiling stats while tracing and then embed them in the HTML
    with profile_section("Tracing + Profiling") as perf_stats:
        with trace_scope(None) as graph:
            # Run a representative workload to populate the call graph
            _ = process_data(10000)
            _ = example_with_sections()
    export_html(graph, "callgraph.html", title="Call Graph with Performance Profiling", profiling_stats=perf_stats.to_dict())
    # print(f"Call graph written to: {output_html}")
    
    print("\n=== Example Complete ===")
    print("Check the output above for performance metrics.")
