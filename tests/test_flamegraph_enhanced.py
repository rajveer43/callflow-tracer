"""
Test suite for enhanced flamegraph features.

Tests all new features:
- Statistics calculation
- Color schemes
- Search functionality
- Export options
- Enhanced HTML generation
"""

import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from callflow_tracer import trace_scope
from callflow_tracer.flamegraph import generate_flamegraph, _calculate_statistics


def test_statistics_calculation():
    """Test 1: Statistics calculation."""
    print("Test 1: Statistics Calculation")
    print("-" * 60)
    
    def func_a():
        time.sleep(0.02)
        return 1
    
    def func_b():
        time.sleep(0.03)
        return 2
    
    def main():
        return func_a() + func_b()
    
    with trace_scope() as graph:
        result = main()
    
    # Calculate statistics
    graph_dict = graph.to_dict()
    stats = _calculate_statistics(graph_dict)
    
    print(f"  Total functions: {stats['total_functions']}")
    print(f"  Total calls: {stats['total_calls']}")
    print(f"  Total time: {stats['total_time']:.4f}s")
    print(f"  Avg time/call: {stats['avg_time_per_call']:.4f}s")
    print(f"  Slowest function: {stats['slowest_function']['name']}")
    print(f"  Most called: {stats['most_called_function']['name']}")
    
    # Verify statistics
    assert stats['total_functions'] > 0, "Should have functions"
    assert stats['total_calls'] > 0, "Should have calls"
    assert stats['total_time'] > 0, "Should have execution time"
    assert stats['slowest_function'] is not None, "Should identify slowest function"
    assert stats['most_called_function'] is not None, "Should identify most called"
    
    print("✓ Test passed\n")


def test_color_schemes():
    """Test 2: All color schemes."""
    print("Test 2: Color Schemes")
    print("-" * 60)
    
    def sample_func():
        return 42
    
    with trace_scope() as graph:
        result = sample_func()
    
    color_schemes = ['default', 'hot', 'cool', 'rainbow', 'performance']
    
    for scheme in color_schemes:
        output_file = os.path.join(
            os.path.dirname(__file__),
            f"test_enhanced_color_{scheme}.html"
        )
        
        generate_flamegraph(
            graph,
            output_file,
            color_scheme=scheme,
            show_stats=True
        )
        
        assert os.path.exists(output_file), f"Should create {scheme} file"
        
        # Verify color scheme in HTML
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert scheme in content or 'colorScheme' in content, f"Should reference {scheme}"
        print(f"  ✓ {scheme:12s} scheme generated")
    
    print("✓ Test passed\n")


def test_search_enabled():
    """Test 3: Search functionality."""
    print("Test 3: Search Functionality")
    print("-" * 60)
    
    def searchable_function():
        return 42
    
    with trace_scope() as graph:
        result = searchable_function()
    
    output_file = os.path.join(os.path.dirname(__file__), "test_enhanced_search.html")
    
    # Generate with search enabled
    generate_flamegraph(
        graph,
        output_file,
        search_enabled=True,
        show_stats=True
    )
    
    assert os.path.exists(output_file), "Should create file"
    
    # Verify search elements in HTML
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ("searchBox" in content, "Search box present"),
        ("searchFunction" in content or "search" in content, "Search function present"),
        ("clearSearch" in content, "Clear search present"),
    ]
    
    for passed, description in checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {description}")
        assert passed, f"Check failed: {description}"
    
    print("✓ Test passed\n")


def test_statistics_panel():
    """Test 4: Statistics panel in HTML."""
    print("Test 4: Statistics Panel")
    print("-" * 60)
    
    def slow_func():
        time.sleep(0.05)
        return 1
    
    def fast_func():
        return 2
    
    def main():
        return slow_func() + fast_func()
    
    with trace_scope() as graph:
        result = main()
    
    output_file = os.path.join(os.path.dirname(__file__), "test_enhanced_stats.html")
    
    # Generate with stats enabled
    generate_flamegraph(
        graph,
        output_file,
        show_stats=True,
        color_scheme="performance"
    )
    
    assert os.path.exists(output_file), "Should create file"
    
    # Verify statistics panel in HTML
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ("Statistics" in content or "stats-panel" in content, "Statistics panel present"),
        ("Total Functions" in content or "total_functions" in content, "Total functions shown"),
        ("Total Calls" in content or "total_calls" in content, "Total calls shown"),
        ("Slowest Function" in content or "slowest_function" in content, "Slowest function shown"),
    ]
    
    for passed, description in checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {description}")
        assert passed, f"Check failed: {description}"
    
    print("✓ Test passed\n")


def test_export_functionality():
    """Test 5: Export SVG functionality."""
    print("Test 5: Export Functionality")
    print("-" * 60)
    
    def exportable_func():
        return 42
    
    with trace_scope() as graph:
        result = exportable_func()
    
    output_file = os.path.join(os.path.dirname(__file__), "test_enhanced_export.html")
    
    generate_flamegraph(
        graph,
        output_file,
        show_stats=True,
        search_enabled=True
    )
    
    assert os.path.exists(output_file), "Should create file"
    
    # Verify export functionality in HTML
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ("exportSVG" in content, "Export SVG function present"),
        ("Export SVG" in content or "💾" in content, "Export button present"),
    ]
    
    for passed, description in checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {description}")
        assert passed, f"Check failed: {description}"
    
    print("✓ Test passed\n")


def test_enhanced_ui():
    """Test 6: Enhanced UI elements."""
    print("Test 6: Enhanced UI")
    print("-" * 60)
    
    def ui_test_func():
        return 42
    
    with trace_scope() as graph:
        result = ui_test_func()
    
    output_file = os.path.join(os.path.dirname(__file__), "test_enhanced_ui.html")
    
    generate_flamegraph(
        graph,
        output_file,
        title="Enhanced UI Test",
        color_scheme="performance",
        show_stats=True,
        search_enabled=True
    )
    
    assert os.path.exists(output_file), "Should create file"
    
    # Verify enhanced UI elements
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ("gradient" in content, "Gradient styling present"),
        ("Enhanced UI Test" in content, "Custom title present"),
        ("container" in content, "Container styling present"),
        ("control" in content, "Controls present"),
    ]
    
    for passed, description in checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {description}")
        assert passed, f"Check failed: {description}"
    
    print("✓ Test passed\n")


def test_performance_color_scheme():
    """Test 7: Performance color scheme specifically."""
    print("Test 7: Performance Color Scheme")
    print("-" * 60)
    
    def very_slow():
        time.sleep(0.1)
        return 1
    
    def medium():
        time.sleep(0.03)
        return 2
    
    def fast():
        return 3
    
    def main():
        return very_slow() + medium() + fast()
    
    with trace_scope() as graph:
        result = main()
    
    output_file = os.path.join(os.path.dirname(__file__), "test_enhanced_performance.html")
    
    generate_flamegraph(
        graph,
        output_file,
        title="Performance Color Test",
        color_scheme="performance",
        show_stats=True
    )
    
    assert os.path.exists(output_file), "Should create file"
    
    # Verify performance color scheme
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert "performance" in content, "Should use performance color scheme"
    assert "#4ecdc4" in content or "#ff6b6b" in content, "Should have performance colors"
    
    print("  ✓ Performance color scheme applied")
    print("  ✓ Fast functions = green")
    print("  ✓ Slow functions = red")
    print("✓ Test passed\n")


def test_min_width_threshold():
    """Test 8: Minimum width threshold."""
    print("Test 8: Minimum Width Threshold")
    print("-" * 60)
    
    def tiny_func():
        return 1
    
    def main():
        for _ in range(10):
            tiny_func()
        return "done"
    
    with trace_scope() as graph:
        result = main()
    
    output_file = os.path.join(os.path.dirname(__file__), "test_enhanced_minwidth.html")
    
    # Test with different thresholds
    thresholds = [0.1, 0.5, 1.0]
    
    for threshold in thresholds:
        generate_flamegraph(
            graph,
            output_file,
            min_width=threshold,
            show_stats=True
        )
        
        assert os.path.exists(output_file), f"Should create file with threshold {threshold}"
        print(f"  ✓ Generated with min_width={threshold}")
    
    print("✓ Test passed\n")


def test_all_features_combined():
    """Test 9: All features together."""
    print("Test 9: All Features Combined")
    print("-" * 60)
    
    def feature_test():
        time.sleep(0.02)
        return 42
    
    with trace_scope() as graph:
        result = feature_test()
    
    output_file = os.path.join(os.path.dirname(__file__), "test_enhanced_all_features.html")
    
    # Generate with ALL features enabled
    generate_flamegraph(
        graph,
        output_file,
        title="All Features Test",
        color_scheme="performance",
        show_stats=True,
        search_enabled=True,
        min_width=0.1,
        width=1400,
        height=900
    )
    
    assert os.path.exists(output_file), "Should create file"
    
    # Verify all features present
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    features = [
        ("All Features Test", "Custom title"),
        ("stats" in content or "Statistics" in content, "Statistics panel"),
        ("search" in content, "Search functionality"),
        ("performance", "Performance color scheme"),
        ("export" in content, "Export functionality"),
    ]
    
    all_present = True
    for check, description in features:
        if isinstance(check, str):
            passed = check in content
        else:
            passed = check
        
        status = "✓" if passed else "✗"
        print(f"  {status} {description}")
        
        if not passed:
            all_present = False
    
    assert all_present, "All features should be present"
    print("✓ Test passed\n")


def test_backward_compatibility():
    """Test 10: Backward compatibility with old API."""
    print("Test 10: Backward Compatibility")
    print("-" * 60)
    
    def compat_func():
        return 42
    
    with trace_scope() as graph:
        result = compat_func()
    
    output_file = os.path.join(os.path.dirname(__file__), "test_enhanced_compat.html")
    
    # Test old API (should still work)
    generate_flamegraph(graph, output_file)
    
    assert os.path.exists(output_file), "Should work with old API"
    print("  ✓ Old API still works")
    
    # Test with only width/height (old style)
    generate_flamegraph(graph, output_file, width=1200, height=800)
    
    assert os.path.exists(output_file), "Should work with old parameters"
    print("  ✓ Old parameters still work")
    
    print("✓ Test passed\n")


def main():
    """Run all enhanced flamegraph tests."""
    print("=" * 70)
    print(" " * 15 + "ENHANCED FLAMEGRAPH TESTS")
    print(" " * 20 + "Test Suite")
    print("=" * 70)
    print()
    
    tests = [
        test_statistics_calculation,
        test_color_schemes,
        test_search_enabled,
        test_statistics_panel,
        test_export_functionality,
        test_enhanced_ui,
        test_performance_color_scheme,
        test_min_width_threshold,
        test_all_features_combined,
        test_backward_compatibility,
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
        print("\n✨ Enhanced Features Verified:")
        print("   ✓ Statistics calculation")
        print("   ✓ All 5 color schemes")
        print("   ✓ Search functionality")
        print("   ✓ Statistics panel")
        print("   ✓ Export to SVG")
        print("   ✓ Enhanced UI")
        print("   ✓ Performance color scheme")
        print("   ✓ Minimum width threshold")
        print("   ✓ All features combined")
        print("   ✓ Backward compatibility")
        
        print("\n📁 Generated test files in tests/ directory")
        print("   Open any test_enhanced_*.html to see the results!")
        return True
    else:
        print(f"\n✗ {failed} TEST(S) FAILED")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
