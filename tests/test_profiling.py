"""
Tests for the profiling functionality.
"""
import time
import pytest
import numpy as np
from callflow_tracer import profile_function, profile_section, get_memory_usage, PerformanceStats

@profile_function
def simple_function():
    """A simple function to test profiling."""
    data = [i for i in range(1000)]
    time.sleep(0.01)
    return sum(data)

def test_profile_function():
    """Test that the profile_function decorator works without errors."""
    result = simple_function()
    assert result == sum(range(1000))
    assert hasattr(simple_function, 'performance_stats')
    assert isinstance(simple_function.performance_stats, PerformanceStats)
    assert simple_function.performance_stats.io_wait_time > 0

def test_profile_section():
    """Test that the profile_section context manager works without errors."""
    with profile_section("test_section") as stats:
        data = [i for i in range(1000)]
        time.sleep(0.01)
        result = sum(data)
    
    assert result == sum(range(1000))
    assert isinstance(stats, PerformanceStats)
    assert stats.io_wait_time > 0

def test_memory_usage():
    """Test that memory usage tracking works."""
    # Get initial memory usage
    mem_before = get_memory_usage()
    
    # Allocate some memory
    data = np.random.random(1000000)  # ~8MB of data
    
    # Get memory usage after allocation
    mem_after = get_memory_usage()
    
    # Memory usage should have increased
    assert mem_after['current_mb'] > mem_before['current_mb']
    assert mem_after['peak_mb'] >= mem_after['current_mb']

def test_nested_profiling():
    """Test that nested profiling works without conflicts."""
    @profile_function
    def inner_function():
        return sum(range(100))
    
    with profile_section("outer_section") as outer_stats:
        result1 = inner_function()
        with profile_section("inner_section") as inner_stats:
            result2 = inner_function()
    
    # Check that both function calls worked
    assert result1 == result2 == sum(range(100))
    
    # Check that we have stats for both sections
    assert isinstance(outer_stats, PerformanceStats)
    assert isinstance(inner_stats, PerformanceStats)
    assert hasattr(inner_function, 'performance_stats')

def test_large_memory_allocation():
    """Test that large memory allocations are tracked correctly."""
    @profile_function
    def allocate_memory(size_mb):
        return np.random.random(size_mb * 131072)  # 1MB = 131072 float64s
    
    # Allocate 10MB of data
    result = allocate_memory(10)
    assert len(result) == 10 * 131072
    
    # Check that memory stats were recorded
    stats = allocate_memory.performance_stats
    mem_stats = stats._get_memory_stats()
    assert mem_stats['current_mb'] > 0

if __name__ == "__main__":
    # Run tests and print results
    test_profile_function()
    test_profile_section()
    test_memory_usage()
    test_nested_profiling()
    test_large_memory_allocation()
    print("All tests passed!")
