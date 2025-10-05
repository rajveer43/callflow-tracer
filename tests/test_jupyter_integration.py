"""
Test script for Jupyter integration functionality.

This script tests the jupyter.py module without requiring an actual Jupyter notebook.
It verifies that the integration functions work correctly.
"""

import sys
import os
import time
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from callflow_tracer import trace_scope, profile_section
from callflow_tracer.exporter import export_html


def test_basic_tracing():
    """Test basic function tracing."""
    print("Test 1: Basic Function Tracing")
    print("-" * 50)
    
    def calculate_sum(numbers):
        return sum(numbers)
    
    def calculate_average(numbers):
        total = calculate_sum(numbers)
        return total / len(numbers)
    
    def process_data(data):
        avg = calculate_average(data)
        total = calculate_sum(data)
        return {'average': avg, 'total': total}
    
    with trace_scope() as graph:
        result = process_data([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        print(f"Result: {result}")
    
    print(f"✓ Captured {len(graph.nodes)} nodes and {len(graph.edges)} edges")
    assert len(graph.nodes) > 0, "Should capture at least one node"
    assert len(graph.edges) > 0, "Should capture at least one edge"
    print()


def test_recursive_tracing():
    """Test recursive function tracing."""
    print("Test 2: Recursive Function Tracing")
    print("-" * 50)
    
    def fibonacci(n):
        if n <= 1:
            return n
        return fibonacci(n - 1) + fibonacci(n - 2)
    
    def factorial(n):
        if n <= 1:
            return 1
        return n * factorial(n - 1)
    
    with trace_scope() as graph:
        fib_result = fibonacci(8)
        fact_result = factorial(5)
        print(f"Fibonacci(8) = {fib_result}")
        print(f"Factorial(5) = {fact_result}")
    
    print(f"✓ Captured {len(graph.nodes)} function calls")
    assert len(graph.nodes) > 10, "Recursive calls should generate many nodes"
    print()


def test_profiling():
    """Test performance profiling."""
    print("Test 3: Performance Profiling")
    print("-" * 50)
    
    def data_processing(n):
        data = [i ** 2 for i in range(n)]
        result = sum(data) / len(data)
        return result
    
    with profile_section("Data Processing") as stats:
        result = data_processing(10000)
        print(f"Average: {result:.2f}")
    
    stats_dict = stats.to_dict()
    print(f"✓ I/O wait time: {stats_dict['io_wait']:.4f}s")
    
    if stats_dict['memory']:
        print(f"✓ Memory: {stats_dict['memory']['current_mb']:.2f}MB")
    
    if stats_dict['cpu']:
        cpu_data = stats_dict['cpu']['profile_data']
        print(f"✓ CPU profile data length: {len(cpu_data)} characters")
        assert len(cpu_data) > 0, "Should capture CPU profile data"
    
    print()


def test_combined_tracing_profiling():
    """Test combined tracing and profiling."""
    print("Test 4: Combined Tracing and Profiling")
    print("-" * 50)
    
    def load_data(size):
        time.sleep(0.02)
        return list(range(size))
    
    def transform_data(data):
        return [x * 2 + 1 for x in data]
    
    def analyze_data(data):
        return {
            'mean': sum(data) / len(data),
            'min': min(data),
            'max': max(data)
        }
    
    def pipeline(size):
        data = load_data(size)
        transformed = transform_data(data)
        results = analyze_data(transformed)
        return results
    
    with profile_section("Data Pipeline") as perf_stats:
        with trace_scope() as graph:
            results = pipeline(100)
            print(f"Analysis Results: {results}")
    
    print(f"✓ Captured {len(graph.nodes)} nodes and {len(graph.edges)} edges")
    
    stats_dict = perf_stats.to_dict()
    print(f"✓ I/O wait time: {stats_dict['io_wait']:.4f}s")
    
    assert len(graph.nodes) >= 4, "Should capture all pipeline functions"
    assert stats_dict['io_wait'] > 0, "Should measure I/O wait time"
    print()


def test_html_export_with_profiling():
    """Test HTML export with profiling data."""
    print("Test 5: HTML Export with Profiling")
    print("-" * 50)
    
    def step1():
        time.sleep(0.01)
        return "Step 1 complete"
    
    def step2():
        time.sleep(0.01)
        return "Step 2 complete"
    
    def step3():
        result1 = step1()
        result2 = step2()
        return f"{result1}, {result2}"
    
    def main_workflow():
        return step3()
    
    with profile_section("Complete Workflow") as perf_stats:
        with trace_scope() as graph:
            result = main_workflow()
            print(result)
    
    # Export to HTML
    output_file = os.path.join(os.path.dirname(__file__), "test_jupyter_export.html")
    export_html(
        graph,
        output_file,
        title="Jupyter Integration Test",
        profiling_stats=perf_stats.to_dict()
    )
    
    print(f"✓ Exported to {output_file}")
    print(f"  - {len(graph.nodes)} nodes")
    print(f"  - {len(graph.edges)} edges")
    
    # Verify file was created and contains expected content
    assert os.path.exists(output_file), "HTML file should be created"
    
    with open(output_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Check for key elements
    checks = [
        ("Jupyter Integration Test" in html_content, "Title present"),
        ("CPU Profile Analysis" in html_content, "CPU profile section present"),
        ("mynetwork" in html_content, "Network visualization present"),
        ("vis.Network" in html_content, "vis.js integration present"),
    ]
    
    for passed, description in checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {description}")
        assert passed, f"Check failed: {description}"
    
    print()


def test_graph_data_structure():
    """Test that graph data structure is correct for visualization."""
    print("Test 6: Graph Data Structure")
    print("-" * 50)
    
    def func_a():
        return func_b() + func_c()
    
    def func_b():
        return 10
    
    def func_c():
        return 20
    
    with trace_scope() as graph:
        result = func_a()
        print(f"Result: {result}")
    
    # Convert to dict (as used by display_callgraph)
    graph_dict = graph.to_dict()
    
    print(f"✓ Graph structure:")
    print(f"  - Nodes: {len(graph_dict['nodes'])}")
    print(f"  - Edges: {len(graph_dict['edges'])}")
    print(f"  - Metadata: {graph_dict['metadata']}")
    
    # Verify structure
    assert 'nodes' in graph_dict, "Should have nodes"
    assert 'edges' in graph_dict, "Should have edges"
    assert 'metadata' in graph_dict, "Should have metadata"
    
    # Check node structure
    if graph_dict['nodes']:
        node = graph_dict['nodes'][0]
        required_fields = ['name', 'module', 'full_name', 'call_count', 'total_time']
        for field in required_fields:
            assert field in node, f"Node should have '{field}' field"
            print(f"  ✓ Node has '{field}' field")
    
    # Check edge structure
    if graph_dict['edges']:
        edge = graph_dict['edges'][0]
        required_fields = ['caller', 'callee', 'call_count', 'total_time']
        for field in required_fields:
            assert field in edge, f"Edge should have '{field}' field"
            print(f"  ✓ Edge has '{field}' field")
    
    print()


def test_complex_workflow():
    """Test a complex real-world workflow."""
    print("Test 7: Complex ML Pipeline Workflow")
    print("-" * 50)
    
    def fetch_dataset(n_samples):
        time.sleep(0.01)
        return [[i + j for j in range(5)] for i in range(n_samples)]
    
    def preprocess(data):
        # Normalize
        return [[x / 10.0 for x in row] for row in data]
    
    def feature_engineering(data):
        # Add squared features
        return [row + [x ** 2 for x in row] for row in data]
    
    def train_model(features):
        time.sleep(0.02)
        # Simple computation
        weights = [sum(col) / len(col) for col in zip(*features)]
        return weights
    
    def evaluate_model(weights, features):
        predictions = [sum(w * f for w, f in zip(weights, row)) for row in features]
        score = sum(predictions) / len(predictions)
        return score
    
    def ml_pipeline(n_samples):
        data = fetch_dataset(n_samples)
        processed = preprocess(data)
        features = feature_engineering(processed)
        model = train_model(features)
        score = evaluate_model(model, features)
        return score
    
    print("Running ML Pipeline...")
    
    with profile_section("ML Pipeline") as perf_stats:
        with trace_scope() as graph:
            final_score = ml_pipeline(50)
            print(f"Model Score: {final_score:.4f}")
    
    print(f"✓ Pipeline captured {len(graph.nodes)} functions")
    print(f"✓ Call relationships: {len(graph.edges)}")
    
    stats = perf_stats.to_dict()
    print(f"✓ Total I/O wait: {stats['io_wait']:.4f}s")
    
    if stats['memory']:
        print(f"✓ Peak memory: {stats['memory']['peak_mb']:.2f}MB")
    
    if stats['cpu']:
        print(f"✓ CPU profile captured: {len(stats['cpu']['profile_data'])} chars")
    
    assert len(graph.nodes) >= 5, "Should capture all pipeline functions"
    print()


def main():
    """Run all tests."""
    print("=" * 60)
    print("JUPYTER INTEGRATION TESTS")
    print("=" * 60)
    print()
    
    tests = [
        test_basic_tracing,
        test_recursive_tracing,
        test_profiling,
        test_combined_tracing_profiling,
        test_html_export_with_profiling,
        test_graph_data_structure,
        test_complex_workflow,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"✗ TEST FAILED: {test.__name__}")
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()
            print()
    
    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("\n✓ ALL TESTS PASSED!")
        print("\nYou can now use the Jupyter notebook examples:")
        print("  - examples/jupyter_example.ipynb")
        print("\nTo run in Jupyter:")
        print("  1. jupyter notebook")
        print("  2. Open examples/jupyter_example.ipynb")
        print("  3. Run the cells")
        return True
    else:
        print(f"\n✗ {failed} TEST(S) FAILED")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
