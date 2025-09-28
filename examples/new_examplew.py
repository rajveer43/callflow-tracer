"""
Comprehensive Flamegraph Example for CallFlow Tracer

This example demonstrates how to use the flamegraph functionality to visualize
performance bottlenecks in your code. The flamegraph shows the call stack
and execution time of functions, making it easy to identify where your
application spends the most time.

Features demonstrated:
1. Nested function calls with varying execution times
2. CPU-intensive operations
3. I/O operations and delays
4. Memory allocation patterns
5. Recursive functions
6. Multiple execution paths
"""

import os
import sys
import time
import random
import math
import numpy as np
from typing import List, Dict, Any

# Ensure local package is imported when running from the examples directory
CURRENT_DIR = os.path.dirname(__file__)
REPO_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from callflow_tracer import trace, trace_scope, get_current_graph, export_html, generate_flamegraph


@trace
def cpu_intensive_task(iterations: int = 10000) -> float:
    """
    Simulate CPU-intensive computation.
    This will show up prominently in the flamegraph.
    """
    result = 0.0
    for i in range(iterations):
        # Complex mathematical operations
        result += math.sin(i) * math.cos(i) + math.sqrt(i + 1)
        result = result % 1000  # Keep numbers manageable
    return result


@trace
def memory_allocation_task(size_mb: int = 10) -> List[float]:
    """
    Allocate and process large arrays.
    Shows memory allocation patterns in the flamegraph.
    """
    if HAS_NUMPY:
        # Use numpy for efficient array operations
        num_elements = int(size_mb * 1024 * 1024 / 8)  # 8 bytes per float64
        large_array = np.random.random(num_elements)
        
        # Process the array
        processed = np.sort(large_array)
        mean_value = np.mean(processed)
        
        return processed[:1000].tolist()  # Return smaller subset as list
    else:
        print("WARNING: NumPy not found. Using fallback implementations for array operations.")
        # Fallback implementation using Python lists
        num_elements = min(int(size_mb * 1024 * 128), 100000)  # Smaller for memory safety
        large_array = [random.random() for _ in range(num_elements)]
        
        # Process the array
        processed = sorted(large_array)
        mean_value = sum(processed) / len(processed)
        
        return processed[:1000]  # Return smaller subset to avoid memory issues


@trace
def io_simulation_task(delay_seconds: float = 0.1) -> str:
    """
    Simulate I/O operations with delays.
    These will appear as flat sections in the flamegraph.
    """
    # Simulate network request
    time.sleep(delay_seconds)
    
    # Simulate file processing
    time.sleep(delay_seconds * 0.5)
    
    return f"IO completed after {delay_seconds * 1.5:.2f}s"


@trace
def recursive_fibonacci(n: int) -> int:
    """
    Recursive Fibonacci calculation.
    Shows recursive call patterns in the flamegraph.
    """
    if n <= 1:
        return n
    return recursive_fibonacci(n - 1) + recursive_fibonacci(n - 2)


@trace
def data_processing_pipeline(data_size: int = 1000) -> Dict[str, Any]:
    """
    Complex data processing pipeline with multiple stages.
    Each stage will be visible in the flamegraph.
    """
    # Stage 1: Data generation
    raw_data = [random.random() * 100 for _ in range(data_size)]
    
    # Stage 2: Data filtering
    filtered_data = [x for x in raw_data if x > 25]
    
    # Stage 3: Data transformation
    transformed_data = [math.log(x + 1) for x in filtered_data]
    
    # Stage 4: Statistical analysis
    stats = {
        'mean': sum(transformed_data) / len(transformed_data),
        'min': min(transformed_data),
        'max': max(transformed_data),
        'count': len(transformed_data)
    }
    
    return stats


@trace
def mixed_workload_function() -> Dict[str, Any]:
    """
    Function that calls multiple other functions.
    This creates a complex call tree in the flamegraph.
    """
    results = {}
    
    # CPU-intensive work
    results['cpu_result'] = cpu_intensive_task(5000)
    
    # Memory allocation
    results['memory_data'] = memory_allocation_task(5)
    
    # I/O simulation
    results['io_result'] = io_simulation_task(0.05)
    
    # Data processing
    results['processing_stats'] = data_processing_pipeline(500)
    
    # Recursive computation (small to avoid stack overflow)
    results['fibonacci'] = recursive_fibonacci(10)
    
    return results


@trace
def performance_comparison_scenario():
    """
    Run different scenarios to compare performance characteristics.
    """
    scenarios = []
    
    # Scenario 1: CPU-bound
    start_time = time.time()
    cpu_result = cpu_intensive_task(15000)
    cpu_time = time.time() - start_time
    scenarios.append(('CPU-bound', cpu_time, cpu_result))
    
    # Scenario 2: Memory-bound
    start_time = time.time()
    memory_result = memory_allocation_task(20)
    memory_time = time.time() - start_time
    scenarios.append(('Memory-bound', memory_time, len(memory_result)))
    
    # Scenario 3: I/O-bound
    start_time = time.time()
    io_result = io_simulation_task(0.2)
    io_time = time.time() - start_time
    scenarios.append(('I/O-bound', io_time, io_result))
    
    return scenarios


@trace
def main_application():
    """
    Main application function that orchestrates all operations.
    This will be the root of the flamegraph.
    """
    print("Starting Flamegraph Example Application")
    print("=" * 50)
    
    # Run mixed workload
    print("Running mixed workload...")
    mixed_results = mixed_workload_function()
    print(f"Mixed workload completed: {len(mixed_results)} results")
    
    # Run performance comparison
    print("\nRunning performance comparison...")
    comparison_results = performance_comparison_scenario()
    for scenario_name, duration, result in comparison_results:
        print(f"{scenario_name}: {duration:.4f}s")
    
    # Run additional CPU work to make flamegraph more interesting
    print("\nRunning additional CPU-intensive tasks...")
    for i in range(3):
        cpu_result = cpu_intensive_task(8000)
        print(f"CPU task {i+1} completed: {cpu_result:.2f}")
    
    print("\nApplication completed successfully!")
    return {
        'mixed_results': mixed_results,
        'comparison_results': comparison_results
    }


def run_flamegraph_example():
    """
    Main function to run the flamegraph example and generate visualizations.
    """
    print("CallFlow Tracer Flamegraph Example")
    print("=" * 60)
    print("This example will generate both a call graph and a flamegraph")
    print("to help you understand your application's performance characteristics.\n")
    
    # Run the application with tracing enabled
    with trace_scope("flamegraph_example"):
        results = main_application()
        
        # Get the current call graph
        graph = get_current_graph()
        
        print(f"\nCall graph captured with {len(graph.nodes)} nodes and {len(graph.edges)} edges")
        
        # Generate HTML call graph visualization
        print("Generating HTML call graph...")
        export_html(graph, "flamegraph_example_callgraph.html", 
                   title="Flamegraph Example - Call Graph Visualization")
        print("Call graph saved to: flamegraph_example_callgraph.html")
        
        # Generate flamegraph visualization
        print("Generating flamegraph...")
        generate_flamegraph(graph, "flamegraph_example_flamegraph.html", 
                          width=1400, height=900)
        print("Flamegraph saved to: flamegraph_example_flamegraph.html")
        
        print("\n" + "=" * 60)
        print("Example completed successfully!")
        print("\nGenerated files:")
        print("1. flamegraph_example_callgraph.html - Interactive call graph")
        print("2. flamegraph_example_flamegraph.html - Interactive flamegraph")
        print("\nHow to interpret the flamegraph:")
        print("• Width of each bar = time spent in that function")
        print("• Height = call stack depth")
        print("• Colors help distinguish different functions")
        print("• Click on bars to zoom in")
        print("• Hover for detailed timing information")
        print("\nLook for:")
        print("• Wide bars = performance bottlenecks")
        print("• Deep stacks = complex call chains")
        print("• Flat sections = I/O or waiting time")
        
        return results


if __name__ == "__main__":
    # Run the example
    results = run_flamegraph_example()
    
    # Optional: Print some results for verification
    print(f"\nApplication Results Summary:")
    print(f"Mixed workload results: {len(results['mixed_results'])} items")
    print(f"Performance comparison: {len(results['comparison_results'])} scenarios")


# Jupyter Notebook Usage Example:
"""
To use this in a Jupyter notebook:

%load_ext callflow_tracer

%%callflow_cell_trace
# Your code here - it will be automatically traced
results = main_application()

# The flamegraph will be generated automatically
# You can also manually generate it:
graph = get_current_graph()
generate_flamegraph(graph, "notebook_flamegraph.html")
"""