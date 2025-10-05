"""
Test to verify that cProfile data is correctly captured and displayed.

This test addresses the issue where the CPU Profile Analysis dashboard
always showed 0.000s execution time, 0 function calls, and 0 hot spots.
"""

import time
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from callflow_tracer import trace_scope, profile_section, export_html


def fibonacci(n):
    """Recursive fibonacci to generate CPU activity."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


def process_data(size):
    """CPU-intensive data processing."""
    data = [i * i for i in range(size)]
    total = sum(data)
    # Add some computation
    for i in range(len(data)):
        total += data[i] / (i + 1)
    return total


def io_operation():
    """Simulate I/O operation."""
    time.sleep(0.05)
    return "completed"


def main():
    """Main test function."""
    print("=== Testing cProfile Data Collection ===\n")
    
    # Test 1: Verify profiling with profile_section
    print("Test 1: Using profile_section context manager")
    with profile_section("CPU Intensive Work") as stats:
        # Generate CPU activity
        result1 = fibonacci(15)
        result2 = process_data(1000)
        result3 = io_operation()
        
        print(f"Fibonacci(15) = {result1}")
        print(f"Process data result = {result2:.2f}")
        print(f"I/O operation = {result3}")
    
    # Verify stats were collected
    print("\n--- Verifying Stats Collection ---")
    stats_dict = stats.to_dict()
    
    print(f"Memory stats present: {bool(stats_dict.get('memory'))}")
    print(f"CPU stats present: {bool(stats_dict.get('cpu'))}")
    print(f"I/O wait time: {stats_dict.get('io_wait', 0):.4f}s")
    
    cpu_data = stats_dict.get('cpu', {}).get('profile_data', '')
    if cpu_data:
        print(f"\nCPU Profile Data Length: {len(cpu_data)} characters")
        print("CPU Profile Data Preview (first 500 chars):")
        print(cpu_data[:500])
        
        # Parse basic metrics from profile data
        lines = cpu_data.split('\n')
        for line in lines[:10]:
            if 'function calls' in line:
                print(f"\n✓ Found function call summary: {line.strip()}")
                break
    else:
        print("\n✗ ERROR: No CPU profile data captured!")
    
    # Test 2: Export to HTML and verify
    print("\n\nTest 2: Exporting to HTML with profiling stats")
    with trace_scope(None) as graph:
        # Run workload
        fibonacci(10)
        process_data(500)
        io_operation()
    
    # Export with profiling stats
    output_file = os.path.join(os.path.dirname(__file__), "test_cprofile_output.html")
    export_html(graph, output_file, 
                title="cProfile Test - Call Graph", 
                profiling_stats=stats_dict)
    
    print(f"✓ HTML exported to: {output_file}")
    
    # Verify HTML contains profiling data
    with open(output_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Check for key indicators in HTML
    checks = [
        ("CPU Profile Analysis" in html_content, "CPU Profile section present"),
        ("Total Execution Time" in html_content, "Execution time metric present"),
        ("Function Calls" in html_content, "Function calls metric present"),
        ("Performance Distribution" in html_content, "Performance distribution present"),
        (f"{stats_dict.get('io_wait', 0):.3f}s" in html_content, "I/O wait time in stats"),
    ]
    
    print("\n--- HTML Content Verification ---")
    all_passed = True
    for passed, description in checks:
        status = "✓" if passed else "✗"
        print(f"{status} {description}")
        if not passed:
            all_passed = False
    
    # Final summary
    print("\n" + "="*50)
    if all_passed and cpu_data:
        print("✓ ALL TESTS PASSED!")
        print("cProfile data is being correctly captured and exported.")
    else:
        print("✗ SOME TESTS FAILED!")
        print("Please review the output above for details.")
    print("="*50)
    
    return all_passed and bool(cpu_data)


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
