"""
Test suite for 3D visualization functionality
"""

import os
import tempfile
from pathlib import Path
from callflow_tracer import trace, get_current_graph, export_html_3d, clear_trace


@trace
def simple_function():
    """A simple function for testing"""
    return "simple"


@trace
def caller_function():
    """Function that calls another function"""
    return simple_function()


@trace
def multi_level_a():
    """Multi-level call chain - level A"""
    return "A"


@trace
def multi_level_b():
    """Multi-level call chain - level B"""
    return multi_level_a()


@trace
def multi_level_c():
    """Multi-level call chain - level C"""
    return multi_level_b()


@trace
def main_test():
    """Main test function"""
    caller_function()
    multi_level_c()
    return "done"


def test_3d_export_creates_file():
    """Test that 3D export creates an HTML file"""
    clear_trace()
    
    # Run traced code
    main_test()
    
    # Get graph
    graph = get_current_graph()
    
    # Export to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        temp_path = f.name
    
    try:
        export_html_3d(graph, temp_path)
        
        # Check file exists
        assert os.path.exists(temp_path), "3D HTML file was not created"
        
        # Check file is not empty
        file_size = os.path.getsize(temp_path)
        assert file_size > 0, "3D HTML file is empty"
        
        print(f"✅ Test passed: 3D HTML file created ({file_size} bytes)")
        
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_3d_html_contains_threejs():
    """Test that 3D HTML contains Three.js library"""
    clear_trace()
    
    # Run traced code
    main_test()
    
    # Get graph
    graph = get_current_graph()
    
    # Export to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        temp_path = f.name
    
    try:
        export_html_3d(graph, temp_path)
        
        # Read file content
        with open(temp_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for Three.js
        assert 'three.js' in content.lower() or 'three.min.js' in content, \
            "Three.js library not found in HTML"
        
        # Check for OrbitControls
        assert 'OrbitControls' in content, \
            "OrbitControls not found in HTML"
        
        print("✅ Test passed: Three.js and OrbitControls found in HTML")
        
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_3d_html_contains_layouts():
    """Test that 3D HTML contains layout options"""
    clear_trace()
    
    # Run traced code
    main_test()
    
    # Get graph
    graph = get_current_graph()
    
    # Export to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        temp_path = f.name
    
    try:
        export_html_3d(graph, temp_path)
        
        # Read file content
        with open(temp_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for layout options
        layouts = ['force', 'sphere', 'helix', 'grid', 'tree']
        for layout in layouts:
            assert layout in content.lower(), \
                f"Layout '{layout}' not found in HTML"
        
        print(f"✅ Test passed: All {len(layouts)} layout options found")
        
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_3d_html_contains_controls():
    """Test that 3D HTML contains interactive controls"""
    clear_trace()
    
    # Run traced code
    main_test()
    
    # Get graph
    graph = get_current_graph()
    
    # Export to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        temp_path = f.name
    
    try:
        export_html_3d(graph, temp_path)
        
        # Read file content
        with open(temp_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for control elements
        controls = [
            'nodeSize',
            'spread',
            'rotationSpeed',
            'resetView',
            'toggleAnimation'
        ]
        
        for control in controls:
            assert control in content, \
                f"Control '{control}' not found in HTML"
        
        print(f"✅ Test passed: All {len(controls)} controls found")
        
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_3d_html_contains_graph_data():
    """Test that 3D HTML contains the actual graph data"""
    clear_trace()
    
    # Run traced code
    main_test()
    
    # Get graph
    graph = get_current_graph()
    
    # Export to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        temp_path = f.name
    
    try:
        export_html_3d(graph, temp_path)
        
        # Read file content
        with open(temp_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for function names
        assert 'simple_function' in content, "simple_function not found in HTML"
        assert 'caller_function' in content, "caller_function not found in HTML"
        assert 'multi_level' in content, "multi_level functions not found in HTML"
        
        # Check for nodes and edges arrays
        assert 'const nodes =' in content, "Nodes array not found"
        assert 'const edges =' in content, "Edges array not found"
        
        print("✅ Test passed: Graph data found in HTML")
        
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_3d_html_contains_statistics():
    """Test that 3D HTML contains statistics panel"""
    clear_trace()
    
    # Run traced code
    main_test()
    
    # Get graph
    graph = get_current_graph()
    graph_dict = graph.to_dict()
    
    # Export to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        temp_path = f.name
    
    try:
        export_html_3d(graph, temp_path)
        
        # Read file content
        with open(temp_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for statistics
        assert 'Statistics' in content or 'stats' in content.lower(), \
            "Statistics panel not found"
        
        # Check for metadata
        total_nodes = str(graph_dict['metadata']['total_nodes'])
        total_edges = str(graph_dict['metadata']['total_edges'])
        
        assert total_nodes in content, f"Total nodes ({total_nodes}) not found"
        assert total_edges in content, f"Total edges ({total_edges}) not found"
        
        print("✅ Test passed: Statistics panel found with correct data")
        
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_3d_export_with_custom_title():
    """Test 3D export with custom title"""
    clear_trace()
    
    # Run traced code
    main_test()
    
    # Get graph
    graph = get_current_graph()
    
    # Export with custom title
    custom_title = "My Custom 3D Visualization"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        temp_path = f.name
    
    try:
        export_html_3d(graph, temp_path, title=custom_title)
        
        # Read file content
        with open(temp_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for custom title
        assert custom_title in content, "Custom title not found in HTML"
        
        print(f"✅ Test passed: Custom title '{custom_title}' found")
        
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_3d_html_is_valid_html():
    """Test that generated 3D HTML is valid HTML5"""
    clear_trace()
    
    # Run traced code
    main_test()
    
    # Get graph
    graph = get_current_graph()
    
    # Export to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        temp_path = f.name
    
    try:
        export_html_3d(graph, temp_path)
        
        # Read file content
        with open(temp_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for HTML5 structure
        assert '<!DOCTYPE html>' in content, "HTML5 doctype not found"
        assert '<html' in content, "HTML tag not found"
        assert '<head>' in content, "Head tag not found"
        assert '<body>' in content, "Body tag not found"
        assert '</html>' in content, "Closing HTML tag not found"
        
        # Check for required meta tags
        assert '<meta charset="UTF-8">' in content, "UTF-8 charset not found"
        
        print("✅ Test passed: Valid HTML5 structure")
        
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)


def run_all_tests():
    """Run all 3D visualization tests"""
    tests = [
        ("File Creation", test_3d_export_creates_file),
        ("Three.js Library", test_3d_html_contains_threejs),
        ("Layout Options", test_3d_html_contains_layouts),
        ("Interactive Controls", test_3d_html_contains_controls),
        ("Graph Data", test_3d_html_contains_graph_data),
        ("Statistics Panel", test_3d_html_contains_statistics),
        ("Custom Title", test_3d_export_with_custom_title),
        ("Valid HTML5", test_3d_html_is_valid_html),
    ]
    
    print("=" * 80)
    print("3D VISUALIZATION TEST SUITE")
    print("=" * 80)
    print()
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"Running: {test_name}...")
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"❌ Test failed: {test_name}")
            print(f"   Error: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ Test error: {test_name}")
            print(f"   Error: {e}")
            failed += 1
        print()
    
    print("=" * 80)
    print("TEST RESULTS")
    print("=" * 80)
    print(f"✅ Passed: {passed}/{len(tests)}")
    if failed > 0:
        print(f"❌ Failed: {failed}/{len(tests)}")
    print("=" * 80)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
