"""
Demonstration of Enhanced Flamegraph Features

This example showcases all the new features added to the flamegraph module:
1. Statistics Panel
2. Search Functionality
3. Multiple Color Schemes
4. Export Options
5. Enhanced UI
6. Performance Tips
"""

import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from callflow_tracer import trace_scope
from callflow_tracer.flamegraph import generate_flamegraph


def demo_1_basic_vs_enhanced():
    """Demo 1: Compare basic and enhanced flamegraphs."""
    print("\n" + "=" * 70)
    print("DEMO 1: Basic vs Enhanced Flamegraph")
    print("=" * 70)
    
    def fast_function():
        """Fast function."""
        return sum(range(100))
    
    def medium_function():
        """Medium speed function."""
        time.sleep(0.05)
        return sum(range(1000))
    
    def slow_function():
        """Slow function - bottleneck!"""
        time.sleep(0.15)
        return sum(range(10000))
    
    def main_workflow():
        """Main workflow with mixed performance."""
        results = []
        results.append(fast_function())
        results.append(medium_function())
        results.append(slow_function())
        return sum(results)
    
    # Trace execution
    print("\nRunning workflow with mixed performance...")
    with trace_scope() as graph:
        result = main_workflow()
        print(f"Result: {result}")
    
    print(f"\nCaptured {len(graph.nodes)} nodes")
    
    # Generate basic flamegraph (old way)
    print("\n1. Generating BASIC flamegraph...")
    generate_flamegraph(graph, "flamegraph_basic_comparison.html")
    print("   ✓ Saved to: flamegraph_basic_comparison.html")
    
    # Generate enhanced flamegraph (new way)
    print("\n2. Generating ENHANCED flamegraph with all features...")
    generate_flamegraph(
        graph,
        "flamegraph_enhanced_comparison.html",
        title="Enhanced Flamegraph Demo",
        color_scheme="performance",  # Green=fast, Red=slow
        show_stats=True,
        search_enabled=True,
        width=1400,
        height=800
    )
    print("   ✓ Saved to: flamegraph_enhanced_comparison.html")
    
    print("\n📊 Compare both files:")
    print("   - Basic: Simple visualization")
    print("   - Enhanced: Statistics, search, color coding, export")


def demo_2_color_schemes():
    """Demo 2: Test all color schemes."""
    print("\n" + "=" * 70)
    print("DEMO 2: All Color Schemes")
    print("=" * 70)
    
    def level_1():
        time.sleep(0.02)
        return level_2() + level_3()
    
    def level_2():
        time.sleep(0.03)
        return 10
    
    def level_3():
        time.sleep(0.05)
        return 20
    
    def main():
        return level_1()
    
    # Trace execution
    print("\nRunning multi-level workflow...")
    with trace_scope() as graph:
        result = main()
        print(f"Result: {result}")
    
    # Generate flamegraph with each color scheme
    color_schemes = {
        'default': 'Default (Red-Yellow-Green)',
        'hot': 'Hot (Red-Orange) - Highlights hot spots',
        'cool': 'Cool (Blue-Green) - Easy on eyes',
        'rainbow': 'Rainbow - Distinguishes functions',
        'performance': 'Performance (Green=Fast, Red=Slow) - Best for optimization!'
    }
    
    print(f"\nGenerating flamegraphs with {len(color_schemes)} color schemes...")
    
    for scheme, description in color_schemes.items():
        filename = f"flamegraph_color_{scheme}.html"
        generate_flamegraph(
            graph,
            filename,
            title=f"Color Scheme: {description}",
            color_scheme=scheme,
            show_stats=True,
            search_enabled=True
        )
        print(f"   ✓ {scheme:12s} → {filename}")
    
    print("\n🎨 Open each file to see the different color schemes!")
    print("   Recommended: 'performance' for finding bottlenecks")


def demo_3_search_functionality():
    """Demo 3: Demonstrate search functionality."""
    print("\n" + "=" * 70)
    print("DEMO 3: Search Functionality")
    print("=" * 70)
    
    def database_query():
        """Simulate database query."""
        time.sleep(0.08)
        return "data"
    
    def cache_lookup():
        """Simulate cache lookup."""
        time.sleep(0.01)
        return "cached"
    
    def api_call_external():
        """Simulate external API call."""
        time.sleep(0.12)
        return "api_response"
    
    def process_data():
        """Process data."""
        time.sleep(0.03)
        return "processed"
    
    def validate_data():
        """Validate data."""
        time.sleep(0.02)
        return "valid"
    
    def application_main():
        """Main application logic."""
        # Try cache first
        cached = cache_lookup()
        
        # If not cached, query database
        if not cached:
            data = database_query()
        
        # Call external API
        api_data = api_call_external()
        
        # Process and validate
        processed = process_data()
        validated = validate_data()
        
        return "complete"
    
    # Trace execution
    print("\nRunning application with multiple functions...")
    with trace_scope() as graph:
        result = application_main()
        print(f"Result: {result}")
    
    print(f"\nCaptured {len(graph.nodes)} functions")
    
    # Generate flamegraph with search enabled
    generate_flamegraph(
        graph,
        "flamegraph_search_demo.html",
        title="Search Demo - Try searching for 'api' or 'database'",
        color_scheme="performance",
        show_stats=True,
        search_enabled=True,
        width=1400,
        height=800
    )
    
    print("\n✓ Saved to: flamegraph_search_demo.html")
    print("\n🔍 Try these searches in the flamegraph:")
    print("   - 'api' - Find API-related functions")
    print("   - 'database' - Find database operations")
    print("   - 'cache' - Find caching functions")
    print("   - 'data' - Find data processing functions")


def demo_4_statistics_panel():
    """Demo 4: Showcase statistics panel."""
    print("\n" + "=" * 70)
    print("DEMO 4: Statistics Panel")
    print("=" * 70)
    
    def recursive_fibonacci(n):
        """Recursive fibonacci - generates many calls."""
        if n <= 1:
            return n
        return recursive_fibonacci(n - 1) + recursive_fibonacci(n - 2)
    
    def iterative_sum(n):
        """Iterative sum - fast."""
        return sum(range(n))
    
    def nested_loops(n):
        """Nested loops - slow."""
        total = 0
        for i in range(n):
            for j in range(n):
                total += i * j
        return total
    
    def complex_workflow():
        """Complex workflow with various patterns."""
        fib = recursive_fibonacci(10)  # Many calls
        fast = iterative_sum(1000)     # Fast
        slow = nested_loops(50)        # Slow
        return fib + fast + slow
    
    # Trace execution
    print("\nRunning complex workflow...")
    with trace_scope() as graph:
        result = complex_workflow()
        print(f"Result: {result}")
    
    print(f"\nCaptured {len(graph.nodes)} nodes")
    
    # Generate flamegraph with statistics
    generate_flamegraph(
        graph,
        "flamegraph_statistics_demo.html",
        title="Statistics Panel Demo",
        color_scheme="performance",
        show_stats=True,  # Enable statistics panel
        search_enabled=True,
        width=1400,
        height=900
    )
    
    print("\n✓ Saved to: flamegraph_statistics_demo.html")
    print("\n📊 The statistics panel shows:")
    print("   - Total functions called")
    print("   - Total number of calls")
    print("   - Total execution time")
    print("   - Average time per call")
    print("   - Call depth")
    print("   - 🔥 Slowest function (bottleneck!)")
    print("   - 📞 Most called function")


def demo_5_performance_analysis():
    """Demo 5: Real-world performance analysis."""
    print("\n" + "=" * 70)
    print("DEMO 5: Real-World Performance Analysis")
    print("=" * 70)
    
    def load_config():
        """Load configuration."""
        time.sleep(0.01)
        return {"setting": "value"}
    
    def initialize_database():
        """Initialize database connection."""
        time.sleep(0.05)
        return "db_connection"
    
    def fetch_user_data(user_id):
        """Fetch user data - SLOW!"""
        time.sleep(0.15)  # Bottleneck!
        return {"user": user_id, "name": "User"}
    
    def fetch_user_permissions(user_id):
        """Fetch user permissions."""
        time.sleep(0.03)
        return ["read", "write"]
    
    def validate_permissions(permissions):
        """Validate permissions."""
        time.sleep(0.01)
        return True
    
    def load_dashboard_data():
        """Load dashboard data."""
        time.sleep(0.08)
        return {"widgets": []}
    
    def render_dashboard():
        """Render dashboard."""
        time.sleep(0.02)
        return "<html>Dashboard</html>"
    
    def application_startup(user_id):
        """Application startup sequence."""
        # Load config
        config = load_config()
        
        # Initialize database
        db = initialize_database()
        
        # Fetch user data (SLOW!)
        user = fetch_user_data(user_id)
        
        # Fetch and validate permissions
        permissions = fetch_user_permissions(user_id)
        valid = validate_permissions(permissions)
        
        # Load dashboard
        dashboard_data = load_dashboard_data()
        
        # Render
        html = render_dashboard()
        
        return html
    
    # Trace execution
    print("\nRunning application startup sequence...")
    with trace_scope() as graph:
        result = application_startup(user_id=123)
        print(f"Result: {len(result)} bytes")
    
    print(f"\nCaptured {len(graph.nodes)} functions")
    
    # Generate flamegraph for performance analysis
    generate_flamegraph(
        graph,
        "flamegraph_performance_analysis.html",
        title="Performance Analysis - Find the Bottleneck!",
        color_scheme="performance",  # Red bars = slow functions
        show_stats=True,
        search_enabled=True,
        min_width=0.1,  # Hide functions < 0.1% of total time
        width=1600,
        height=900
    )
    
    print("\n✓ Saved to: flamegraph_performance_analysis.html")
    print("\n🎯 Performance Analysis Tips:")
    print("   1. Look for RED bars (slow functions)")
    print("   2. Check the statistics panel for slowest function")
    print("   3. Wide bars = where time is spent")
    print("   4. In this example, 'fetch_user_data' should be the widest/reddest")
    print("   5. That's your optimization target!")


def demo_6_export_options():
    """Demo 6: Test export functionality."""
    print("\n" + "=" * 70)
    print("DEMO 6: Export Options")
    print("=" * 70)
    
    def task_1():
        time.sleep(0.02)
        return "task1"
    
    def task_2():
        time.sleep(0.03)
        return "task2"
    
    def task_3():
        time.sleep(0.01)
        return "task3"
    
    def workflow():
        return task_1() + task_2() + task_3()
    
    # Trace execution
    print("\nRunning workflow...")
    with trace_scope() as graph:
        result = workflow()
        print(f"Result: {result}")
    
    # Generate flamegraph with export options
    generate_flamegraph(
        graph,
        "flamegraph_export_demo.html",
        title="Export Demo - Click 'Export SVG' button",
        color_scheme="rainbow",
        show_stats=True,
        search_enabled=True
    )
    
    print("\n✓ Saved to: flamegraph_export_demo.html")
    print("\n💾 Export Features:")
    print("   - Click '💾 Export SVG' button in the flamegraph")
    print("   - Saves high-quality vector graphics")
    print("   - Perfect for presentations and reports")
    print("   - Preserves all details and colors")


def demo_7_all_features_combined():
    """Demo 7: Kitchen sink - all features together."""
    print("\n" + "=" * 70)
    print("DEMO 7: All Features Combined")
    print("=" * 70)
    
    def microservice_a():
        """Microservice A."""
        time.sleep(0.04)
        return "service_a_response"
    
    def microservice_b():
        """Microservice B."""
        time.sleep(0.06)
        return "service_b_response"
    
    def microservice_c():
        """Microservice C - SLOW!"""
        time.sleep(0.12)
        return "service_c_response"
    
    def aggregate_responses():
        """Aggregate all responses."""
        time.sleep(0.02)
        return "aggregated"
    
    def cache_result():
        """Cache the result."""
        time.sleep(0.01)
        return "cached"
    
    def orchestrator():
        """Orchestrate microservices."""
        # Call all microservices
        a = microservice_a()
        b = microservice_b()
        c = microservice_c()  # This is slow!
        
        # Aggregate
        aggregated = aggregate_responses()
        
        # Cache
        cached = cache_result()
        
        return "complete"
    
    # Trace execution
    print("\nRunning microservices orchestration...")
    with trace_scope() as graph:
        result = orchestrator()
        print(f"Result: {result}")
    
    print(f"\nCaptured {len(graph.nodes)} nodes")
    
    # Generate ultimate flamegraph with ALL features
    generate_flamegraph(
        graph,
        "flamegraph_ultimate_demo.html",
        title="🔥 Ultimate Flamegraph - All Features Enabled",
        color_scheme="performance",
        show_stats=True,
        search_enabled=True,
        min_width=0.05,
        width=1600,
        height=1000
    )
    
    print("\n✓ Saved to: flamegraph_ultimate_demo.html")
    print("\n✨ This flamegraph has EVERYTHING:")
    print("   ✓ Statistics panel with all metrics")
    print("   ✓ Search functionality")
    print("   ✓ Performance color scheme (green=fast, red=slow)")
    print("   ✓ Export to SVG")
    print("   ✓ Enhanced tooltips with percentages")
    print("   ✓ Optimization tips")
    print("   ✓ Responsive design")
    print("   ✓ Modern UI with gradients")


def main():
    """Run all enhanced flamegraph demos."""
    print("\n" + "=" * 70)
    print(" " * 15 + "ENHANCED FLAMEGRAPH DEMOS")
    print(" " * 10 + "Testing All New Features")
    print("=" * 70)
    
    print("\nThis demo showcases all the new enhanced features:")
    print("  1. Basic vs Enhanced comparison")
    print("  2. All color schemes")
    print("  3. Search functionality")
    print("  4. Statistics panel")
    print("  5. Performance analysis")
    print("  6. Export options")
    print("  7. All features combined")
    
    try:
        # Run all demos
        demo_1_basic_vs_enhanced()
        demo_2_color_schemes()
        demo_3_search_functionality()
        demo_4_statistics_panel()
        demo_5_performance_analysis()
        demo_6_export_options()
        demo_7_all_features_combined()
        
        # Summary
        print("\n" + "=" * 70)
        print("ALL DEMOS COMPLETED!")
        print("=" * 70)
        
        print("\n📁 Generated Files:")
        print("   1. flamegraph_basic_comparison.html")
        print("   2. flamegraph_enhanced_comparison.html")
        print("   3. flamegraph_color_default.html")
        print("   4. flamegraph_color_hot.html")
        print("   5. flamegraph_color_cool.html")
        print("   6. flamegraph_color_rainbow.html")
        print("   7. flamegraph_color_performance.html")
        print("   8. flamegraph_search_demo.html")
        print("   9. flamegraph_statistics_demo.html")
        print("   10. flamegraph_performance_analysis.html")
        print("   11. flamegraph_export_demo.html")
        print("   12. flamegraph_ultimate_demo.html")
        
        print("\n✨ New Features Demonstrated:")
        print("   ✓ Statistics Panel - See metrics at a glance")
        print("   ✓ Search - Find functions quickly")
        print("   ✓ Color Schemes - 5 different schemes")
        print("   ✓ Performance Colors - Green=fast, Red=slow")
        print("   ✓ Export SVG - Save for presentations")
        print("   ✓ Enhanced UI - Modern, responsive design")
        print("   ✓ Better Tooltips - Shows percentages")
        print("   ✓ Optimization Tips - Built-in guide")
        
        print("\n🎯 Recommended Files to Open:")
        print("   1. flamegraph_enhanced_comparison.html - See the difference")
        print("   2. flamegraph_color_performance.html - Best for optimization")
        print("   3. flamegraph_ultimate_demo.html - All features together")
        
        print("\n💡 Pro Tips:")
        print("   - Use 'performance' color scheme to find bottlenecks")
        print("   - Search for specific function names")
        print("   - Check statistics panel for slowest function")
        print("   - Export as SVG for reports and presentations")
        print("   - Wide RED bars = your optimization targets!")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error during demos: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
