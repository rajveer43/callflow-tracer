"""
Comprehensive test suite for flamegraph functionality.

Tests cover:
- Basic flamegraph generation
- Data processing and validation
- HTML output verification
- Edge cases and error handling
- Integration with trace_scope
"""

import sys
import os
import time
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from callflow_tracer import trace_scope
from callflow_tracer.flamegraph import generate_flamegraph, _process_for_flamegraph


def test_basic_flamegraph_generation():
    """Test 1: Basic flamegraph generation."""
    print("Test 1: Basic Flamegraph Generation")
    print("-" * 60)
    
    def func_a():
        return func_b() + func_c()
    
    def func_b():
        time.sleep(0.01)
        return 10
    
    def func_c():
        time.sleep(0.01)
        return 20
    
    # Trace execution
    with trace_scope() as graph:
        result = func_a()
    
    print(f"Result: {result}")
    print(f"Captured {len(graph.nodes)} nodes, {len(graph.edges)} edges")
    
    # Generate flamegraph
    output_file = os.path.join(os.path.dirname(__file__), "test_flamegraph_basic.html")
    generate_flamegraph(graph, output_file)
    
    # Verify file was created
    assert os.path.exists(output_file), "Flamegraph HTML file should be created"
    
    # Verify file contains expected content
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ("CallFlow Flame Graph" in content, "Title present"),
        ("d3-flamegraph" in content, "D3 flamegraph library included"),
        ("func_a" in content or "func_b" in content, "Function names in data"),
        ("<script>" in content, "JavaScript present"),
        ("flamegraph()" in content, "Flamegraph initialization"),
    ]
    
    all_passed = True
    for passed, description in checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {description}")
        if not passed:
            all_passed = False
    
    assert all_passed, "All content checks should pass"
    print("✓ Test passed\n")


def test_recursive_function_flamegraph():
    """Test 2: Flamegraph with recursive functions."""
    print("Test 2: Recursive Function Flamegraph")
    print("-" * 60)
    
    def fibonacci(n):
        if n <= 1:
            return n
        return fibonacci(n - 1) + fibonacci(n - 2)
    
    # Trace recursive execution
    with trace_scope() as graph:
        result = fibonacci(8)
    
    print(f"Fibonacci(8) = {result}")
    print(f"Captured {len(graph.nodes)} nodes (recursive calls)")
    
    # Generate flamegraph
    output_file = os.path.join(os.path.dirname(__file__), "test_flamegraph_recursive.html")
    generate_flamegraph(graph, output_file, width=1400, height=800)
    
    assert os.path.exists(output_file), "Flamegraph file should be created"
    
    # Verify file size (should be substantial for recursive calls)
    file_size = os.path.getsize(output_file)
    print(f"  ✓ Generated file size: {file_size} bytes")
    assert file_size > 1000, "File should contain substantial content"
    
    print("✓ Test passed\n")


def test_data_processing():
    """Test 3: Flamegraph data processing."""
    print("Test 3: Flamegraph Data Processing")
    print("-" * 60)
    
    def level_2():
        time.sleep(0.01)
        return "L2"
    
    def level_1():
        result = level_2()
        time.sleep(0.01)
        return "L1" + result
    
    def main():
        return level_1()
    
    # Trace execution
    with trace_scope() as graph:
        result = main()
    
    print(f"Result: {result}")
    
    # Test data processing
    graph_dict = graph.to_dict()
    flame_data = _process_for_flamegraph(graph_dict)
    
    print(f"  ✓ Processed {len(flame_data)} root nodes")
    assert len(flame_data) > 0, "Should have at least one root node"
    
    # Verify flame data structure
    root = flame_data[0]
    assert 'name' in root, "Root should have name"
    assert 'value' in root, "Root should have value"
    assert 'children' in root, "Root should have children"
    
    print(f"  ✓ Root node: {root['name']}")
    print(f"  ✓ Root value: {root['value']}ms")
    print(f"  ✓ Children count: {len(root['children'])}")
    
    print("✓ Test passed\n")


def test_empty_graph_handling():
    """Test 4: Handle empty or invalid graph data."""
    print("Test 4: Empty Graph Handling")
    print("-" * 60)
    
    # Test with empty graph data
    empty_data = {'nodes': [], 'edges': [], 'metadata': {}}
    flame_data = _process_for_flamegraph(empty_data)
    
    print(f"  ✓ Empty graph processed: {len(flame_data)} nodes")
    
    # Generate flamegraph with empty data
    output_file = os.path.join(os.path.dirname(__file__), "test_flamegraph_empty.html")
    generate_flamegraph(empty_data, output_file)
    
    assert os.path.exists(output_file), "Should create file even with empty data"
    
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Should have fallback content
    assert "No Data" in content or "flamegraph" in content, "Should have fallback or error handling"
    print("  ✓ Empty graph handled gracefully")
    
    print("✓ Test passed\n")


def test_custom_dimensions():
    """Test 5: Custom width and height."""
    print("Test 5: Custom Dimensions")
    print("-" * 60)
    
    def simple_func():
        return 42
    
    with trace_scope() as graph:
        result = simple_func()
    
    # Test different dimensions
    dimensions = [
        (800, 400),
        (1600, 1000),
        (1200, 600)
    ]
    
    for width, height in dimensions:
        output_file = os.path.join(
            os.path.dirname(__file__), 
            f"test_flamegraph_{width}x{height}.html"
        )
        generate_flamegraph(graph, output_file, width=width, height=height)
        
        assert os.path.exists(output_file), f"Should create {width}x{height} file"
        
        # Verify dimensions in HTML
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert f"width: {width}px" in content, f"Should have width {width}"
        assert f"height: {height}px" in content, f"Should have height {height}"
        
        print(f"  ✓ Generated {width}x{height} flamegraph")
    
    print("✓ Test passed\n")


def test_complex_call_hierarchy():
    """Test 6: Complex call hierarchy."""
    print("Test 6: Complex Call Hierarchy")
    print("-" * 60)
    
    def leaf_1():
        time.sleep(0.005)
        return 1
    
    def leaf_2():
        time.sleep(0.005)
        return 2
    
    def branch_a():
        return leaf_1() + leaf_2()
    
    def branch_b():
        return leaf_1() * 2
    
    def trunk():
        return branch_a() + branch_b()
    
    def root():
        return trunk()
    
    # Trace complex hierarchy
    with trace_scope() as graph:
        result = root()
    
    print(f"Result: {result}")
    print(f"Nodes: {len(graph.nodes)}, Edges: {len(graph.edges)}")
    
    # Generate flamegraph
    output_file = os.path.join(os.path.dirname(__file__), "test_flamegraph_complex.html")
    generate_flamegraph(graph, output_file, width=1400, height=800)
    
    assert os.path.exists(output_file), "Complex hierarchy file should be created"
    
    # Verify data structure
    graph_dict = graph.to_dict()
    flame_data = _process_for_flamegraph(graph_dict)
    
    # Should have hierarchical structure
    assert len(flame_data) > 0, "Should have root nodes"
    
    # Check for nested children
    def count_total_nodes(node):
        count = 1
        for child in node.get('children', []):
            count += count_total_nodes(child)
        return count
    
    total_nodes = sum(count_total_nodes(root) for root in flame_data)
    print(f"  ✓ Total nodes in flame data: {total_nodes}")
    assert total_nodes >= len(graph.nodes), "Should capture all nodes"
    
    print("✓ Test passed\n")


def test_performance_timing():
    """Test 7: Verify timing data in flamegraph."""
    print("Test 7: Performance Timing Data")
    print("-" * 60)
    
    def slow_function():
        """Intentionally slow function."""
        time.sleep(0.05)
        return "slow"
    
    def fast_function():
        """Fast function."""
        return "fast"
    
    def timed_main():
        slow = slow_function()
        fast = fast_function()
        return slow + fast
    
    # Trace with timing
    with trace_scope() as graph:
        result = timed_main()
    
    print(f"Result: {result}")
    
    # Check that timing data is captured
    graph_dict = graph.to_dict()
    nodes = graph_dict['nodes']
    
    # Find the slow function node
    slow_node = next((n for n in nodes if 'slow_function' in n['full_name']), None)
    
    if slow_node:
        print(f"  ✓ Slow function time: {slow_node['total_time']:.4f}s")
        assert slow_node['total_time'] >= 0.04, "Should capture significant time"
    
    # Generate flamegraph
    output_file = os.path.join(os.path.dirname(__file__), "test_flamegraph_timing.html")
    generate_flamegraph(graph, output_file)
    
    # Verify timing data in HTML
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert "total_time" in content, "Should include timing data"
    print("  ✓ Timing data included in flamegraph")
    
    print("✓ Test passed\n")


def test_flamegraph_with_dict_input():
    """Test 8: Generate flamegraph from dict instead of CallGraph."""
    print("Test 8: Flamegraph from Dictionary Input")
    print("-" * 60)
    
    def sample_func():
        return 42
    
    # Get graph as dict
    with trace_scope() as graph:
        result = sample_func()
    
    graph_dict = graph.to_dict()
    
    # Generate flamegraph from dict
    output_file = os.path.join(os.path.dirname(__file__), "test_flamegraph_dict.html")
    generate_flamegraph(graph_dict, output_file)
    
    assert os.path.exists(output_file), "Should accept dict input"
    print("  ✓ Flamegraph generated from dictionary")
    
    # Verify content
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert "flamegraph" in content, "Should contain flamegraph code"
    print("  ✓ Content verified")
    
    print("✓ Test passed\n")


def test_interactive_features():
    """Test 9: Verify interactive features in HTML."""
    print("Test 9: Interactive Features")
    print("-" * 60)
    
    def interactive_demo():
        def step1():
            return 1
        def step2():
            return 2
        return step1() + step2()
    
    with trace_scope() as graph:
        result = interactive_demo()
    
    output_file = os.path.join(os.path.dirname(__file__), "test_flamegraph_interactive.html")
    generate_flamegraph(graph, output_file)
    
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for interactive features
    features = [
        ("zoomToFit" in content, "Zoom to fit button"),
        ("resetZoom" in content, "Reset zoom button"),
        ("tooltip" in content, "Tooltip functionality"),
        ("d3.select" in content, "D3.js selection"),
        (".call(chart)" in content, "Chart rendering"),
    ]
    
    all_present = True
    for present, description in features:
        status = "✓" if present else "✗"
        print(f"  {status} {description}")
        if not present:
            all_present = False
    
    assert all_present, "All interactive features should be present"
    print("✓ Test passed\n")


def test_error_handling():
    """Test 10: Error handling and edge cases."""
    print("Test 10: Error Handling")
    print("-" * 60)
    
    # Test with None input
    try:
        output_file = os.path.join(os.path.dirname(__file__), "test_flamegraph_none.html")
        generate_flamegraph(None, output_file)
        print("  ✓ Handled None input gracefully")
    except Exception as e:
        print(f"  ✓ Caught expected error: {type(e).__name__}")
    
    # Test with invalid data structure
    invalid_data = {'invalid': 'structure'}
    flame_data = _process_for_flamegraph(invalid_data)
    print(f"  ✓ Invalid data processed: {len(flame_data)} nodes")
    
    # Test with missing fields
    partial_data = {'nodes': [{'name': 'test'}], 'edges': []}
    flame_data = _process_for_flamegraph(partial_data)
    print(f"  ✓ Partial data processed: {len(flame_data)} nodes")
    
    print("✓ Test passed\n")


def main():
    """Run all flamegraph tests."""
    print("=" * 70)
    print(" " * 20 + "FLAMEGRAPH TESTS")
    print(" " * 15 + "Comprehensive Test Suite")
    print("=" * 70)
    print()
    
    tests = [
        test_basic_flamegraph_generation,
        test_recursive_function_flamegraph,
        test_data_processing,
        test_empty_graph_handling,
        test_custom_dimensions,
        test_complex_call_hierarchy,
        test_performance_timing,
        test_flamegraph_with_dict_input,
        test_interactive_features,
        test_error_handling,
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
    
    print("=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)
    
    if failed == 0:
        print("\n✓ ALL TESTS PASSED!")
        print("\nGenerated test files:")
        print("  - test_flamegraph_basic.html")
        print("  - test_flamegraph_recursive.html")
        print("  - test_flamegraph_complex.html")
        print("  - test_flamegraph_timing.html")
        print("  - And more...")
        print("\n📊 Open any HTML file in your browser to see the flamegraphs!")
        return True
    else:
        print(f"\n✗ {failed} TEST(S) FAILED")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
