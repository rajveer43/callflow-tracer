#!/usr/bin/env python3
"""
Test script to verify that the CPU profile analysis fix works correctly.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'callflow-tracer'))

from callflow_tracer.exporter import _analyze_cpu_profile, _generate_html

def test_cpu_profile_analysis():
    """Test CPU profile analysis with sample data."""
    
    # Sample CPU profile text (simplified)
    sample_profile = """         125 function calls (120 primitive calls) in 0.002 seconds

   Ordered by: standard name

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000    0.002    0.002 <string>:1(<module>)
       10    0.001    0.000    0.001    0.000 example.py:15(calculate)
        5    0.000    0.000    0.000    0.000 example.py:25(helper)
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
"""
    
    print("Testing CPU profile analysis...")
    
    # Test the analysis function
    metrics = _analyze_cpu_profile(sample_profile)
    
    print(f"✅ Total Time: {metrics['total_time']:.3f}s")
    print(f"✅ Total Calls: {metrics['total_calls']}")
    print(f"✅ Top Functions: {len(metrics['top_functions'])}")
    print(f"✅ Health Indicators: {len(metrics['health_indicators'])}")
    
    # Test health indicators
    health = metrics['health_indicators']
    print(f"✅ Execution Time Health: {health['execution_time']['message']}")
    print(f"✅ Call Efficiency Health: {health['call_efficiency']['message']}")
    print(f"✅ Hot Spots Health: {health['hot_spots']['message']}")
    
    return True

def test_html_generation():
    """Test HTML generation with CPU profile data."""
    
    # Create mock graph data
    mock_graph_data = {
        'nodes': [
            {
                'full_name': 'test_function',
                'name': 'test_function',
                'module': 'test_module',
                'call_count': 5,
                'total_time': 0.1,
                'avg_time': 0.02
            }
        ],
        'edges': [
            {
                'caller': 'main',
                'callee': 'test_function',
                'call_count': 5,
                'total_time': 0.1,
                'avg_time': 0.02
            }
        ],
        'metadata': {
            'total_nodes': 1,
            'total_edges': 1,
            'duration': 0.1
        }
    }
    
    # Mock profiling stats with CPU data
    mock_profiling_stats = {
        'memory': {
            'current_mb': 10.5,
            'peak_mb': 15.2
        },
        'io_wait': 0.001,
        'cpu': {
            'profile_data': '''125 function calls (120 primitive calls) in 0.002 seconds

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000    0.002    0.002 <string>:1(<module>)
       10    0.001    0.000    0.001    0.000 example.py:15(calculate)'''
        }
    }
    
    print("\nTesting HTML generation with CPU profile...")
    
    try:
        # This should work without TypeError now
        html_content = _generate_html(
            graph_data=mock_graph_data,
            title="Test Call Flow Graph",
            include_vis_js=True,
            profiling_stats=mock_profiling_stats,
            layout="hierarchical"
        )
        
        # Basic checks
        assert 'CPU Profile Analysis' in html_content, "CPU profile section not found"
        assert 'What This Data Means' in html_content, "Explanation section not found"
        assert 'Performance Health Guide' in html_content, "Health guide not found"
        assert 'health-' in html_content, "Health indicators not found"
        
        print("✅ HTML generation successful!")
        print(f"✅ Generated HTML length: {len(html_content)} characters")
        print("✅ CPU profile section included")
        print("✅ Health indicators working")
        
        return True
        
    except Exception as e:
        print(f"❌ HTML generation failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing CPU Profile Analysis Fix...")
    print("=" * 50)
    
    success1 = test_cpu_profile_analysis()
    success2 = test_html_generation()
    
    print("=" * 50)
    if success1 and success2:
        print("🎉 All tests passed! CPU profile analysis is working correctly.")
    else:
        print("💥 Some tests failed.")
    
    sys.exit(0 if success1 and success2 else 1)
