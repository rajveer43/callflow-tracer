"""
Comprehensive tests for comparison mode functionality.
"""

import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from callflow_tracer import trace_scope
from callflow_tracer.comparison import (
    compare_graphs, export_comparison_html
)


# Test functions for "before" optimization
def slow_fibonacci(n):
    """Slow recursive fibonacci (before optimization)."""
    if n <= 1:
        return n
    return slow_fibonacci(n-1) + slow_fibonacci(n-2)


def slow_factorial(n):
    """Slow recursive factorial (before optimization)."""
    if n <= 1:
        return 1
    return n * slow_factorial(n-1)


def slow_sum_list(lst):
    """Slow list sum (before optimization)."""
    total = 0
    for item in lst:
        time.sleep(0.001)  # Simulate slow operation
        total += item
    return total


# Test functions for "after" optimization
_fib_cache = {}

def fast_fibonacci(n):
    """Fast memoized fibonacci (after optimization)."""
    if n in _fib_cache:
        return _fib_cache[n]
    if n <= 1:
        return n
    result = fast_fibonacci(n-1) + fast_fibonacci(n-2)
    _fib_cache[n] = result
    return result


def fast_factorial(n):
    """Fast iterative factorial (after optimization)."""
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


def fast_sum_list(lst):
    """Fast list sum using built-in (after optimization)."""
    return sum(lst)


# Test 1: Basic comparison
def test_basic_comparison():
    """Test basic graph comparison."""
    print("\n" + "="*60)
    print("TEST 1: Basic Graph Comparison")
    print("="*60)
    
    # Trace "before" version
    with trace_scope() as graph_before:
        result1 = slow_fibonacci(10)
        print(f"Slow fibonacci(10) = {result1}")
    
    # Trace "after" version
    with trace_scope() as graph_after:
        result2 = fast_fibonacci(10)
        print(f"Fast fibonacci(10) = {result2}")
    
    # Compare
    comparison = compare_graphs(graph_before, graph_after, "Before", "After")
    
    summary = comparison['summary']
    print(f"\n📊 Comparison Summary:")
    print(f"  Time saved: {summary['time_saved']:.4f}s ({summary['time_saved_pct']:.1f}%)")
    print(f"  Improvements: {summary['improvements']}")
    print(f"  Regressions: {summary['regressions']}")
    
    assert summary['time_saved'] > 0, "Expected performance improvement"
    print("✓ Comparison successful")
    return True


# Test 2: Export comparison to HTML
def test_export_comparison_html():
    """Test exporting comparison to HTML."""
    print("\n" + "="*60)
    print("TEST 2: Export Comparison to HTML")
    print("="*60)
    
    output_file = "test_comparison.html"
    
    # Trace both versions
    with trace_scope() as graph_before:
        slow_factorial(8)
        slow_sum_list([1, 2, 3, 4, 5])
    
    with trace_scope() as graph_after:
        fast_factorial(8)
        fast_sum_list([1, 2, 3, 4, 5])
    
    # Export comparison
    export_comparison_html(
        graph_before, graph_after,
        output_file,
        label1="Unoptimized",
        label2="Optimized",
        title="Performance Optimization Comparison"
    )
    
    assert os.path.exists(output_file)
    file_size = os.path.getsize(output_file)
    print(f"✓ Created {output_file} ({file_size} bytes)")
    
    # Verify HTML content
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "Performance Optimization Comparison" in content
        assert "Unoptimized" in content
        assert "Optimized" in content
        print("✓ HTML content verified")
    
    # Clean up
    # if os.path.exists(output_file):
        # os.remove(output_file)
        # print(f"✓ Cleaned up {output_file}")
    
    return True


# Test 3: Comparison with added functions
def new_function():
    """Function that only exists in 'after' version."""
    time.sleep(0.01)
    return "new"


def test_comparison_with_additions():
    """Test comparison when new functions are added."""
    print("\n" + "="*60)
    print("TEST 3: Comparison with Added Functions")
    print("="*60)
    
    # Before: only old functions
    with trace_scope() as graph_before:
        slow_factorial(5)
    
    # After: old + new functions
    with trace_scope() as graph_after:
        fast_factorial(5)
        new_function()
    
    comparison = compare_graphs(graph_before, graph_after)
    summary = comparison['summary']
    
    print(f"Functions added: {summary['nodes_added']}")
    print(f"Functions removed: {summary['nodes_removed']}")
    print(f"Functions modified: {summary['nodes_modified']}")
    
    assert summary['nodes_added'] > 0, "Expected added functions"
    print("✓ Addition detection successful")
    return True


# Test 4: Comparison with removed functions
def test_comparison_with_removals():
    """Test comparison when functions are removed."""
    print("\n" + "="*60)
    print("TEST 4: Comparison with Removed Functions")
    print("="*60)
    
    # Before: multiple functions
    with trace_scope() as graph_before:
        slow_fibonacci(8)
        slow_factorial(5)
        slow_sum_list([1, 2, 3])
    
    # After: fewer functions
    with trace_scope() as graph_after:
        fast_fibonacci(8)
    
    comparison = compare_graphs(graph_before, graph_after)
    summary = comparison['summary']
    
    print(f"Functions removed: {summary['nodes_removed']}")
    
    assert summary['nodes_removed'] > 0, "Expected removed functions"
    print("✓ Removal detection successful")
    return True


# Test 5: Comparison statistics
def test_comparison_statistics():
    """Test detailed comparison statistics."""
    print("\n" + "="*60)
    print("TEST 5: Comparison Statistics")
    print("="*60)
    
    # Create two different traces
    with trace_scope() as graph1:
        for i in range(3):
            slow_fibonacci(8)
    
    with trace_scope() as graph2:
        for i in range(3):
            fast_fibonacci(8)
    
    comparison = compare_graphs(graph1, graph2, "Slow", "Fast")
    
    # Check node comparisons
    node_comps = comparison['node_comparisons']
    print(f"Total function comparisons: {len(node_comps)}")
    
    # Check top improvements
    top_improvements = comparison['top_improvements']
    if top_improvements:
        print(f"\nTop improvement:")
        imp = top_improvements[0]
        print(f"  Function: {imp['name']}")
        print(f"  Time saved: {-imp['time_diff']:.4f}s ({-imp['time_diff_pct']:.1f}%)")
    
    assert len(node_comps) > 0, "Expected node comparisons"
    print("✓ Statistics generated successfully")
    return True


# Test 6: Regression detection
def intentionally_slower(n):
    """Intentionally slower version for regression testing."""
    time.sleep(0.05)  # Add artificial delay
    return n * 2


def original_version(n):
    """Original faster version."""
    return n * 2


def test_regression_detection():
    """Test detection of performance regressions."""
    print("\n" + "="*60)
    print("TEST 6: Regression Detection")
    print("="*60)
    
    # Before: fast version
    with trace_scope() as graph_before:
        for i in range(3):
            original_version(i)
    
    # After: slower version (regression)
    with trace_scope() as graph_after:
        for i in range(3):
            intentionally_slower(i)
    
    comparison = compare_graphs(graph_before, graph_after)
    summary = comparison['summary']
    
    print(f"Regressions detected: {summary['regressions']}")
    print(f"Time change: {summary['time_saved']:.4f}s ({summary['time_saved_pct']:.1f}%)")
    
    assert summary['regressions'] > 0, "Expected to detect regressions"
    assert summary['time_saved'] < 0, "Expected negative time savings (regression)"
    print("✓ Regression detection successful")
    return True


# Test 7: Large comparison
def test_large_comparison():
    """Test comparison with many functions."""
    print("\n" + "="*60)
    print("TEST 7: Large Comparison")
    print("="*60)
    
    def create_functions(count, delay):
        """Create multiple function calls."""
        results = []
        for i in range(count):
            time.sleep(delay)
            results.append(i * 2)
        return results
    
    # Before: slower
    with trace_scope() as graph_before:
        create_functions(10, 0.002)
    
    # After: faster
    with trace_scope() as graph_after:
        create_functions(10, 0.001)
    
    comparison = compare_graphs(graph_before, graph_after)
    
    print(f"Nodes compared: {len(comparison['node_comparisons'])}")
    print(f"Time saved: {comparison['summary']['time_saved']:.4f}s")
    
    assert len(comparison['node_comparisons']) > 0
    print("✓ Large comparison successful")
    return True


# Test 8: Identical graphs
def test_identical_graphs():
    """Test comparison of identical graphs."""
    print("\n" + "="*60)
    print("TEST 8: Identical Graphs Comparison")
    print("="*60)
    
    def same_function(n):
        return n * 2
    
    # Run same code twice
    with trace_scope() as graph1:
        for i in range(5):
            same_function(i)
    
    with trace_scope() as graph2:
        for i in range(5):
            same_function(i)
    
    comparison = compare_graphs(graph1, graph2)
    summary = comparison['summary']
    
    print(f"Time difference: {abs(summary['time_saved']):.6f}s")
    print(f"Nodes added: {summary['nodes_added']}")
    print(f"Nodes removed: {summary['nodes_removed']}")
    
    # Should be very similar (small timing differences expected)
    assert summary['nodes_added'] == 0
    assert summary['nodes_removed'] == 0
    print("✓ Identical graph comparison successful")
    return True


# Test 9: Custom labels
def test_custom_labels():
    """Test comparison with custom labels."""
    print("\n" + "="*60)
    print("TEST 9: Custom Labels")
    print("="*60)
    
    with trace_scope() as graph1:
        slow_fibonacci(7)
    
    with trace_scope() as graph2:
        fast_fibonacci(7)
    
    comparison = compare_graphs(
        graph1, graph2,
        label1="Version 1.0",
        label2="Version 2.0"
    )
    
    assert comparison['label1'] == "Version 1.0"
    assert comparison['label2'] == "Version 2.0"
    
    print(f"✓ Custom labels: {comparison['label1']} vs {comparison['label2']}")
    return True


# Test 10: Full workflow test
def test_full_workflow():
    """Test complete comparison workflow."""
    print("\n" + "="*60)
    print("TEST 10: Full Workflow Test")
    print("="*60)
    
    output_file = "test_full_workflow.html"
    
    # Simulate a real optimization scenario
    print("Running unoptimized version...")
    with trace_scope() as graph_before:
        result1 = slow_fibonacci(10)
        result2 = slow_factorial(6)
        result3 = slow_sum_list([1, 2, 3, 4, 5])
        print(f"  Results: fib={result1}, fact={result2}, sum={result3}")
    
    print("Running optimized version...")
    with trace_scope() as graph_after:
        result1 = fast_fibonacci(10)
        result2 = fast_factorial(6)
        result3 = fast_sum_list([1, 2, 3, 4, 5])
        print(f"  Results: fib={result1}, fact={result2}, sum={result3}")
    
    # Generate comparison
    print("Generating comparison report...")
    export_comparison_html(
        graph_before, graph_after,
        output_file,
        label1="Before Optimization",
        label2="After Optimization",
        title="Complete Optimization Analysis"
    )
    
    # Verify
    assert os.path.exists(output_file)
    file_size = os.path.getsize(output_file)
    print(f"✓ Generated report: {output_file} ({file_size} bytes)")
    
    # Get statistics
    comparison = compare_graphs(graph_before, graph_after)
    summary = comparison['summary']
    
    print(f"\n📊 Final Results:")
    print(f"  Time saved: {summary['time_saved']:.4f}s ({summary['time_saved_pct']:.1f}%)")
    print(f"  Improvements: {summary['improvements']}")
    print(f"  Regressions: {summary['regressions']}")
    print(f"  Functions modified: {summary['nodes_modified']}")
    
    # Clean up
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"✓ Cleaned up {output_file}")
    
    return True


# Main test runner
def run_all_tests():
    """Run all comparison mode tests."""
    print("\n" + "="*70)
    print("COMPARISON MODE TEST SUITE")
    print("="*70)
    
    tests = [
        ("Basic Comparison", test_basic_comparison),
        ("Export to HTML", test_export_comparison_html),
        ("Added Functions", test_comparison_with_additions),
        ("Removed Functions", test_comparison_with_removals),
        ("Comparison Statistics", test_comparison_statistics),
        ("Regression Detection", test_regression_detection),
        ("Large Comparison", test_large_comparison),
        ("Identical Graphs", test_identical_graphs),
        ("Custom Labels", test_custom_labels),
        ("Full Workflow", test_full_workflow),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
                print(f"✅ {name}: PASSED")
            else:
                failed += 1
                print(f"❌ {name}: FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {name}: FAILED with exception: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*70)
    
    if failed == 0:
        print("✅ ALL TESTS PASSED!")
    else:
        print(f"❌ {failed} TEST(S) FAILED")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
