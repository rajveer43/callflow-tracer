#!/usr/bin/env python3
"""
Test script to verify that the curly brace escaping fix in exporter.py works correctly.
This script tests the HTML template formatting without the ValueError.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'callflow-tracer'))

from callflow_tracer.exporter import _generate_html

def test_html_format():
    """Test that the HTML template can be formatted without errors."""
    
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
    
    # Mock profiling stats
    mock_profiling_stats = {
        'memory': {
            'current_mb': 10.5,
            'peak_mb': 15.2
        },
        'io_wait': 0.001,
        'cpu': {
            'profile_data': 'Sample CPU profile data'
        }
    }
    
    try:
        # This should work without ValueError now
        html_content = _generate_html(
            graph_data=mock_graph_data,
            title="Test Call Flow Graph",
            include_vis_js=True,
            profiling_stats=mock_profiling_stats,
            layout="hierarchical"
        )
        
        # Basic checks to ensure the HTML was generated correctly
        assert '{title}' not in html_content, "Title placeholder not replaced"
        assert 'Test Call Flow Graph' in html_content, "Title not inserted"
        assert 'test_function' in html_content, "Node data not inserted"
        assert '{{' in html_content, "CSS/JS braces should be escaped"
        
        print("✅ SUCCESS: HTML template formatting works correctly!")
        print(f"✅ Generated HTML length: {len(html_content)} characters")
        print("✅ All placeholders were replaced properly")
        print("✅ CSS and JavaScript curly braces are properly escaped")
        
        return True
        
    except ValueError as e:
        if "unexpected '{' in field name" in str(e):
            print(f"❌ FAILED: Still getting curly brace error: {e}")
            return False
        else:
            print(f"❌ FAILED: Different ValueError: {e}")
            return False
    except Exception as e:
        print(f"❌ FAILED: Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("Testing HTML template formatting fix...")
    print("=" * 50)
    
    success = test_html_format()
    
    print("=" * 50)
    if success:
        print("🎉 All tests passed! The curly brace escaping fix is working.")
    else:
        print("💥 Tests failed. There may still be unescaped braces.")
    
    sys.exit(0 if success else 1)
