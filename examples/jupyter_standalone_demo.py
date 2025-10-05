"""
Standalone demonstration of Jupyter integration features.

This script demonstrates all the features that would be available in a Jupyter notebook,
but can be run as a regular Python script. It generates HTML outputs that can be viewed
in a browser.
"""

import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from callflow_tracer import trace_scope, profile_section, profile_function
from callflow_tracer.exporter import export_html


def demo_basic_tracing():
    """Demo 1: Basic function tracing."""
    print("\n" + "=" * 60)
    print("DEMO 1: Basic Function Tracing")
    print("=" * 60)
    
    def calculate_sum(numbers):
        """Calculate sum of numbers."""
        return sum(numbers)
    
    def calculate_average(numbers):
        """Calculate average of numbers."""
        total = calculate_sum(numbers)
        return total / len(numbers)
    
    def process_data(data):
        """Process data and return statistics."""
        avg = calculate_average(data)
        total = calculate_sum(data)
        return {'average': avg, 'total': total}
    
    # Trace the execution
    with trace_scope() as graph:
        result = process_data([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        print(f"\nResult: {result}")
    
    print(f"\n✓ Captured {len(graph.nodes)} nodes and {len(graph.edges)} edges")
    
    # Export to HTML
    output_file = "demo1_basic_tracing.html"
    export_html(graph, output_file, title="Demo 1: Basic Function Tracing")
    print(f"✓ Exported to {output_file}")
    
    return graph


def demo_recursive_functions():
    """Demo 2: Recursive function tracing."""
    print("\n" + "=" * 60)
    print("DEMO 2: Recursive Function Tracing")
    print("=" * 60)
    
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
    
    # Trace recursive calls
    with trace_scope() as graph:
        fib_result = fibonacci(8)
        fact_result = factorial(5)
        print(f"\nFibonacci(8) = {fib_result}")
        print(f"Factorial(5) = {fact_result}")
    
    print(f"\n✓ Captured {len(graph.nodes)} function calls")
    
    # Export to HTML
    output_file = "demo2_recursive_functions.html"
    export_html(graph, output_file, title="Demo 2: Recursive Functions", layout="force")
    print(f"✓ Exported to {output_file}")
    
    return graph


def demo_performance_profiling():
    """Demo 3: Performance profiling."""
    print("\n" + "=" * 60)
    print("DEMO 3: Performance Profiling")
    print("=" * 60)
    
    @profile_function
    def matrix_operations(size):
        """Perform matrix-like operations."""
        matrix = [[i * j for j in range(size)] for i in range(size)]
        total = sum(sum(row) for row in matrix)
        return total
    
    @profile_function
    def data_processing(n):
        """Process large dataset."""
        data = [i ** 2 for i in range(n)]
        result = sum(data) / len(data)
        return result
    
    # Run with profiling
    print("\nRunning matrix operations...")
    result1 = matrix_operations(50)
    print(f"Matrix sum: {result1}")
    
    print("\nRunning data processing...")
    result2 = data_processing(10000)
    print(f"Average: {result2:.2f}")
    
    # Display profiling stats
    print("\n--- Matrix Operations Stats ---")
    stats1 = matrix_operations.performance_stats
    print(f"I/O wait time: {stats1.io_wait_time:.4f}s")
    mem_stats1 = stats1._get_memory_stats()
    if mem_stats1:
        print(f"Memory: {mem_stats1['current_mb']:.2f}MB (peak: {mem_stats1['peak_mb']:.2f}MB)")
    
    print("\n--- Data Processing Stats ---")
    stats2 = data_processing.performance_stats
    print(f"I/O wait time: {stats2.io_wait_time:.4f}s")
    mem_stats2 = stats2._get_memory_stats()
    if mem_stats2:
        print(f"Memory: {mem_stats2['current_mb']:.2f}MB (peak: {mem_stats2['peak_mb']:.2f}MB)")
    
    print("\n✓ Profiling completed")


def demo_combined_analysis():
    """Demo 4: Combined tracing and profiling."""
    print("\n" + "=" * 60)
    print("DEMO 4: Combined Tracing and Profiling")
    print("=" * 60)
    
    def load_data(size):
        """Simulate data loading."""
        time.sleep(0.05)  # Simulate I/O
        return list(range(size))
    
    def transform_data(data):
        """Transform data."""
        return [x * 2 + 1 for x in data]
    
    def analyze_data(data):
        """Analyze transformed data."""
        return {
            'mean': sum(data) / len(data),
            'min': min(data),
            'max': max(data),
            'count': len(data)
        }
    
    def pipeline(size):
        """Complete data pipeline."""
        data = load_data(size)
        transformed = transform_data(data)
        results = analyze_data(transformed)
        return results
    
    # Run with both tracing and profiling
    with profile_section("Data Pipeline") as perf_stats:
        with trace_scope() as graph:
            results = pipeline(1000)
            print(f"\nAnalysis Results: {results}")
    
    print(f"\n✓ Captured {len(graph.nodes)} nodes and {len(graph.edges)} edges")
    
    # Display profiling stats
    print("\n--- Performance Stats ---")
    stats_dict = perf_stats.to_dict()
    print(f"I/O wait time: {stats_dict['io_wait']:.4f}s")
    if stats_dict['memory']:
        print(f"Memory: {stats_dict['memory']['current_mb']:.2f}MB")
    if stats_dict['cpu']:
        print(f"CPU profile captured: {len(stats_dict['cpu']['profile_data'])} characters")
    
    # Export to HTML with profiling data
    output_file = "demo4_combined_analysis.html"
    export_html(
        graph,
        output_file,
        title="Demo 4: Combined Analysis",
        profiling_stats=stats_dict
    )
    print(f"\n✓ Exported to {output_file}")
    
    return graph, perf_stats


def demo_ml_pipeline():
    """Demo 5: Machine Learning Pipeline."""
    print("\n" + "=" * 60)
    print("DEMO 5: Machine Learning Pipeline")
    print("=" * 60)
    
    def fetch_dataset(n_samples):
        """Simulate fetching data from a source."""
        time.sleep(0.02)
        return [[i + j for j in range(5)] for i in range(n_samples)]
    
    def preprocess(data):
        """Preprocess the data."""
        # Normalize
        return [[x / 10.0 for x in row] for row in data]
    
    def feature_engineering(data):
        """Create new features."""
        # Add polynomial features
        return [row + [x ** 2 for x in row] for row in data]
    
    def train_model(features):
        """Simulate model training."""
        time.sleep(0.05)
        # Simple computation to simulate training
        weights = [sum(col) / len(col) for col in zip(*features)]
        return weights
    
    def evaluate_model(weights, features):
        """Evaluate model performance."""
        predictions = [sum(w * f for w, f in zip(weights, row)) for row in features]
        score = sum(predictions) / len(predictions)
        return score
    
    def ml_pipeline(n_samples):
        """Complete ML pipeline."""
        # Fetch data
        data = fetch_dataset(n_samples)
        
        # Preprocess
        processed = preprocess(data)
        
        # Feature engineering
        features = feature_engineering(processed)
        
        # Train
        model = train_model(features)
        
        # Evaluate
        score = evaluate_model(model, features)
        
        return score
    
    # Run the pipeline with tracing and profiling
    print("\nRunning ML Pipeline...")
    
    with profile_section("ML Pipeline") as perf_stats:
        with trace_scope() as graph:
            final_score = ml_pipeline(100)
            print(f"\nModel Score: {final_score:.4f}")
    
    # Show metrics
    print("\n--- Pipeline Metrics ---")
    print(f"Functions called: {len(graph.nodes)}")
    print(f"Call relationships: {len(graph.edges)}")
    
    stats = perf_stats.to_dict()
    print(f"Total I/O wait: {stats['io_wait']:.4f}s")
    if stats['memory']:
        print(f"Peak memory: {stats['memory']['peak_mb']:.2f}MB")
    if stats['cpu']:
        print(f"CPU profile captured: {len(stats['cpu']['profile_data'])} characters")
    
    # Export to HTML
    output_file = "demo5_ml_pipeline.html"
    export_html(
        graph,
        output_file,
        title="Demo 5: ML Pipeline",
        profiling_stats=stats
    )
    print(f"\n✓ Exported to {output_file}")
    
    return graph, perf_stats


def demo_nested_calls():
    """Demo 6: Complex nested function calls."""
    print("\n" + "=" * 60)
    print("DEMO 6: Complex Nested Function Calls")
    print("=" * 60)
    
    def level_3_a():
        time.sleep(0.01)
        return "3A"
    
    def level_3_b():
        time.sleep(0.01)
        return "3B"
    
    def level_2_a():
        return level_3_a() + level_3_b()
    
    def level_2_b():
        return level_3_a()
    
    def level_1():
        result_a = level_2_a()
        result_b = level_2_b()
        return result_a + result_b
    
    def main():
        return level_1()
    
    # Trace nested calls
    with profile_section("Nested Calls") as perf_stats:
        with trace_scope() as graph:
            result = main()
            print(f"\nResult: {result}")
    
    print(f"\n✓ Captured {len(graph.nodes)} nodes and {len(graph.edges)} edges")
    print(f"✓ I/O wait time: {perf_stats.to_dict()['io_wait']:.4f}s")
    
    # Export to HTML
    output_file = "demo6_nested_calls.html"
    export_html(
        graph,
        output_file,
        title="Demo 6: Nested Function Calls",
        profiling_stats=perf_stats.to_dict(),
        layout="hierarchical"
    )
    print(f"✓ Exported to {output_file}")
    
    return graph


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 70)
    print(" " * 15 + "JUPYTER INTEGRATION DEMO")
    print(" " * 10 + "Standalone Python Script Version")
    print("=" * 70)
    
    print("\nThis demo shows all features available in Jupyter notebooks.")
    print("Each demo generates an interactive HTML file that you can open")
    print("in your web browser.")
    
    try:
        # Run all demos
        demo_basic_tracing()
        demo_recursive_functions()
        demo_performance_profiling()
        demo_combined_analysis()
        demo_ml_pipeline()
        demo_nested_calls()
        
        # Summary
        print("\n" + "=" * 70)
        print("DEMO COMPLETE!")
        print("=" * 70)
        print("\nGenerated HTML files:")
        print("  1. demo1_basic_tracing.html - Basic function call graph")
        print("  2. demo2_recursive_functions.html - Recursive function visualization")
        print("  3. demo4_combined_analysis.html - Tracing + Profiling")
        print("  4. demo5_ml_pipeline.html - ML pipeline with profiling")
        print("  5. demo6_nested_calls.html - Complex nested calls")
        
        print("\nTo view the visualizations:")
        print("  - Open any .html file in your web browser")
        print("  - Use the controls to change layouts and filters")
        print("  - Hover over nodes/edges for details")
        print("  - Expand the CPU Profile section for performance data")
        
        print("\nTo use in Jupyter Notebook:")
        print("  - Open examples/jupyter_example.ipynb")
        print("  - Run: jupyter notebook")
        print("  - Execute the cells to see interactive visualizations")
        
        print("\n✓ All demos completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n✗ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
