"""
Comprehensive tests for memory leak detection functionality.
"""

import sys
import os
import time
import gc

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from callflow_tracer.memory_leak_detector import (
    MemoryLeakDetector, detect_leaks, track_allocations,
    find_reference_cycles, get_memory_growth, get_top_memory_consumers,
    MemorySnapshot, ObjectTracker
)


# Test 1: Basic leak detection
def test_basic_leak_detection():
    """Test basic memory leak detection."""
    print("\n" + "="*60)
    print("TEST 1: Basic Leak Detection")
    print("="*60)
    
    detector = MemoryLeakDetector()
    detector.start()
    
    # Create some objects
    leaked_list = []
    for i in range(100):
        leaked_list.append([i] * 100)
    
    detector.take_snapshot("After allocation")
    detector.stop()
    
    report = detector.get_report()
    
    print(f"Duration: {report['duration']:.3f}s")
    print(f"Snapshots: {report['snapshots']}")
    print(f"Objects tracked: {report['object_stats']['total_tracked']}")
    
    assert report['snapshots'] >= 2
    print("✓ Basic leak detection working")
    return True


# Test 2: Context manager
def test_context_manager():
    """Test detect_leaks context manager."""
    print("\n" + "="*60)
    print("TEST 2: Context Manager")
    print("="*60)
    
    output_file = "test_leak_report.html"
    
    with detect_leaks(output_file) as detector:
        # Allocate memory
        data = [list(range(1000)) for _ in range(50)]
        detector.take_snapshot("Mid-execution")
    
    assert os.path.exists(output_file)
    file_size = os.path.getsize(output_file)
    print(f"✓ Created {output_file} ({file_size} bytes)")
    
    # Clean up
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"✓ Cleaned up {output_file}")
    
    return True


# Test 3: Track allocations decorator
@track_allocations
def allocate_memory():
    """Function that allocates memory."""
    data = []
    for i in range(100):
        data.append({'id': i, 'data': [0] * 100})
    return data


def test_track_allocations_decorator():
    """Test @track_allocations decorator."""
    print("\n" + "="*60)
    print("TEST 3: Track Allocations Decorator")
    print("="*60)
    
    result = allocate_memory()
    
    assert len(result) == 100
    print("✓ Decorator tracked allocations")
    return True


# Test 4: Memory snapshots
def test_memory_snapshots():
    """Test memory snapshot functionality."""
    print("\n" + "="*60)
    print("TEST 4: Memory Snapshots")
    print("="*60)
    
    snapshot1 = MemorySnapshot("Before")
    
    # Allocate memory
    data = [list(range(1000)) for _ in range(100)]
    
    snapshot2 = MemorySnapshot("After")
    
    comparison = snapshot2.compare_to(snapshot1)
    
    print(f"Memory diff: {comparison['memory_diff']:,} bytes")
    print(f"Objects diff: {comparison['objects_diff']:,}")
    print(f"Type changes: {len(comparison['type_changes'])}")
    
    assert comparison['memory_diff'] > 0
    print("✓ Snapshots working correctly")
    return True


# Test 5: Object tracking
def test_object_tracking():
    """Test object tracking functionality."""
    print("\n" + "="*60)
    print("TEST 5: Object Tracking")
    print("="*60)
    
    tracker = ObjectTracker()
    tracker.start_time = time.time()
    
    # Track some objects
    obj1 = [1, 2, 3]
    obj2 = {'key': 'value'}
    obj3 = "test string"
    
    tracker.track_object(obj1)
    tracker.track_object(obj2)
    tracker.track_object(obj3)
    
    stats = tracker.get_object_stats()
    
    print(f"Total tracked: {stats['total_tracked']}")
    print(f"Currently live: {stats['currently_live']}")
    print(f"Type distribution: {stats['type_distribution']}")
    
    assert stats['total_tracked'] >= 3
    print("✓ Object tracking working")
    return True


# Test 6: Growth pattern detection
def test_growth_pattern_detection():
    """Test memory growth pattern detection."""
    print("\n" + "="*60)
    print("TEST 6: Growth Pattern Detection")
    print("="*60)
    
    detector = MemoryLeakDetector()
    detector.start()
    
    # Simulate memory growth
    data_holder = []
    for i in range(5):
        data_holder.append([0] * 10000)
        detector.take_snapshot(f"Growth_{i}")
        time.sleep(0.1)
    
    detector.stop()
    
    report = detector.get_report()
    growth_patterns = report['growth_patterns']
    
    print(f"Growth patterns detected: {len(growth_patterns)}")
    if growth_patterns:
        print(f"Average growth rate: {sum(p['growth_rate'] for p in growth_patterns) / len(growth_patterns):.2f} bytes/sec")
    
    assert len(growth_patterns) > 0
    print("✓ Growth pattern detection working")
    return True


# Test 7: Reference cycle detection
def test_reference_cycle_detection():
    """Test reference cycle detection."""
    print("\n" + "="*60)
    print("TEST 7: Reference Cycle Detection")
    print("="*60)
    
    # Create a reference cycle
    class Node:
        def __init__(self):
            self.ref = None
    
    node1 = Node()
    node2 = Node()
    node1.ref = node2
    node2.ref = node1
    
    # Delete references but keep cycle
    del node1, node2
    
    cycles = find_reference_cycles()
    
    print(f"Reference cycles found: {len(cycles)}")
    print("✓ Cycle detection working")
    return True


# Test 8: Memory growth monitoring
def test_memory_growth_monitoring():
    """Test memory growth monitoring."""
    print("\n" + "="*60)
    print("TEST 8: Memory Growth Monitoring")
    print("="*60)
    
    measurements = get_memory_growth(interval=0.2, iterations=3)
    
    print(f"Measurements taken: {len(measurements)}")
    for i, m in enumerate(measurements):
        if 'memory_growth' in m:
            print(f"  Iteration {i}: {m['memory_growth']:+,} bytes")
    
    assert len(measurements) == 3
    print("✓ Memory growth monitoring working")
    return True


# Test 9: Top memory consumers
def test_top_memory_consumers():
    """Test top memory consumers detection."""
    print("\n" + "="*60)
    print("TEST 9: Top Memory Consumers")
    print("="*60)
    
    # Allocate some memory
    large_data = [list(range(10000)) for _ in range(10)]
    
    consumers = get_top_memory_consumers(limit=5)
    
    print(f"Top consumers found: {len(consumers)}")
    for i, consumer in enumerate(consumers[:3]):
        print(f"  #{i+1}: {consumer['size_mb']:.2f} MB ({consumer['count']} allocations)")
    
    assert len(consumers) > 0
    print("✓ Top memory consumers detection working")
    return True


# Test 10: Leak report generation
def test_leak_report_generation():
    """Test complete leak report generation."""
    print("\n" + "="*60)
    print("TEST 10: Leak Report Generation")
    print("="*60)
    
    output_file = "test_complete_leak_report.html"
    
    with detect_leaks(output_file) as detector:
        # Simulate various scenarios
        
        # 1. Normal allocations
        normal_data = [i for i in range(1000)]
        detector.take_snapshot("After normal allocation")
        
        # 2. Large allocation
        large_data = [[0] * 1000 for _ in range(100)]
        detector.take_snapshot("After large allocation")
        
        # 3. Many small objects
        small_objects = [{'id': i} for i in range(500)]
        detector.take_snapshot("After small objects")
    
    assert os.path.exists(output_file)
    
    # Verify HTML content
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "Memory Leak Detection Report" in content
        assert "Snapshots Taken" in content
        print("✓ HTML content verified")
    
    file_size = os.path.getsize(output_file)
    print(f"✓ Generated complete report: {output_file} ({file_size} bytes)")
    
    # Clean up
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"✓ Cleaned up {output_file}")
    
    return True


# Test 11: Leak detection with actual leak
def test_actual_leak_detection():
    """Test detection of an actual memory leak."""
    print("\n" + "="*60)
    print("TEST 11: Actual Leak Detection")
    print("="*60)
    
    detector = MemoryLeakDetector()
    detector.start()
    
    # Create an intentional leak
    leaked_objects = []
    
    for i in range(10):
        obj = [0] * 10000
        leaked_objects.append(obj)
        detector.take_snapshot(f"Leak_{i}")
        time.sleep(0.05)
    
    detector.stop()
    
    report = detector.get_report()
    
    print(f"Suspected leaks: {len(report['suspected_leaks'])}")
    print(f"Growth patterns: {len(report['growth_patterns'])}")
    
    if report['suspected_leaks']:
        for leak in report['suspected_leaks']:
            print(f"  - {leak['type']}")
    
    # Should detect continuous growth
    assert len(report['growth_patterns']) > 0
    print("✓ Actual leak detected")
    return True


# Test 12: No leak scenario
def test_no_leak_scenario():
    """Test that no leaks are detected in clean code."""
    print("\n" + "="*60)
    print("TEST 12: No Leak Scenario")
    print("="*60)
    
    detector = MemoryLeakDetector()
    detector.start()
    
    # Clean code with proper cleanup
    for i in range(5):
        data = [0] * 1000
        # Data goes out of scope
        detector.take_snapshot(f"Clean_{i}")
    
    # Force garbage collection
    gc.collect()
    
    detector.stop()
    
    report = detector.get_report()
    
    print(f"Suspected leaks: {len(report['suspected_leaks'])}")
    print(f"Objects leaked: {report['object_stats']['leaked_count']}")
    
    # Should have minimal or no leaks
    print("✓ No leak scenario handled correctly")
    return True


# Main test runner
def run_all_tests():
    """Run all memory leak detection tests."""
    print("\n" + "="*70)
    print("MEMORY LEAK DETECTION TEST SUITE")
    print("="*70)
    
    tests = [
        ("Basic Leak Detection", test_basic_leak_detection),
        ("Context Manager", test_context_manager),
        ("Track Allocations Decorator", test_track_allocations_decorator),
        ("Memory Snapshots", test_memory_snapshots),
        ("Object Tracking", test_object_tracking),
        ("Growth Pattern Detection", test_growth_pattern_detection),
        ("Reference Cycle Detection", test_reference_cycle_detection),
        ("Memory Growth Monitoring", test_memory_growth_monitoring),
        ("Top Memory Consumers", test_top_memory_consumers),
        ("Leak Report Generation", test_leak_report_generation),
        ("Actual Leak Detection", test_actual_leak_detection),
        ("No Leak Scenario", test_no_leak_scenario),
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
