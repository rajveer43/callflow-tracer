"""
Performance profiling utilities for callflow-tracer.

This module provides performance profiling capabilities including memory usage tracking,
CPU profiling, and I/O wait time measurement.
"""

import time
import tracemalloc
import cProfile
import pstats
import io
import os
from typing import Dict, Any, Optional, Callable, TypeVar, cast
from functools import wraps
from contextlib import contextmanager

T = TypeVar('T', bound=Callable[..., Any])

class PerformanceStats:
    """Container for performance statistics."""
    
    def __init__(self):
        self.memory_snapshot = None
        self.start_time = 0.0
        self.cpu_profile = None
        self.io_wait_time = 0.0
        self.last_io_check = 0.0
        self._is_top_level = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert performance stats to dictionary."""
        return {
            'memory': self._get_memory_stats(),
            'cpu': self._get_cpu_stats(),
            'io_wait': self.io_wait_time
        }
    
    def _get_memory_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics."""
        if not self.memory_snapshot:
            return {}
            
        current, peak = tracemalloc.get_traced_memory()
        return {
            'current_mb': current / (1024 * 1024),
            'peak_mb': peak / (1024 * 1024)
        }
    
    def _get_cpu_stats(self) -> Dict[str, Any]:
        """Get CPU profiling statistics."""
        if not self.cpu_profile:
            return {}
            
        s = io.StringIO()
        ps = pstats.Stats(self.cpu_profile, stream=s).sort_stats('cumulative')
        ps.print_stats(10)  # Top 10 functions by cumulative time
        
        return {
            'profile_data': s.getvalue()
        }

# Global state to track active profilers
_active_profilers = 0
_global_profiler = None

def _start_profiling():
    """Start profiling if not already started."""
    global _active_profilers, _global_profiler
    if _active_profilers == 0:
        tracemalloc.start()
        _global_profiler = cProfile.Profile()
        _global_profiler.enable()
    _active_profilers += 1

def _stop_profiling():
    """Stop profiling if this was the last active profiler."""
    global _active_profilers, _global_profiler
    _active_profilers -= 1
    if _active_profilers == 0:
        if _global_profiler:
            _global_profiler.disable()
            _global_profiler = None
        tracemalloc.stop()

def profile_function(func: T) -> T:
    """
    Decorator to profile a function's performance.
    
    Tracks memory usage, CPU time, and I/O wait.
    
    Example:
        @profile_function
        def my_function():
            # Your code here
            pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        global _global_profiler
        
        # Initialize performance tracking
        stats = PerformanceStats()
        
        # Start profiling
        _start_profiling()
        
        # Record start time
        stats.start_time = time.perf_counter()
        stats.last_io_check = time.process_time()
        
        try:
            # Execute the function
            result = func(*args, **kwargs)
            return result
        finally:
            # Calculate I/O wait time
            stats.io_wait_time = (time.perf_counter() - stats.start_time) - \
                               (time.process_time() - stats.last_io_check)
            
            # Store CPU profile if we have one
            if _global_profiler:
                stats.cpu_profile = _global_profiler
            
            # Take memory snapshot if we're the last profiler
            if _active_profilers == 1:
                stats.memory_snapshot = tracemalloc.take_snapshot()
            
            # Stop profiling
            _stop_profiling()
            
            # Store stats in function for later access
            wrapper.performance_stats = stats  # type: ignore
    
    return cast(T, wrapper)

@contextmanager
def profile_section(name: str = None):
    """
    Context manager for profiling a section of code.
    
    Example:
        with profile_section("data_processing"):
            # Code to profile
            process_data()
    """
    global _global_profiler
    
    stats = PerformanceStats()
    
    # Start profiling
    _start_profiling()
    
    # Record start time
    stats.start_time = time.perf_counter()
    stats.last_io_check = time.process_time()
    
    try:
        yield stats
    finally:
        # Calculate I/O wait time
        stats.io_wait_time = (time.perf_counter() - stats.start_time) - \
                           (time.process_time() - stats.last_io_check)
        
        # Store CPU profile if we have one
        if _global_profiler:
            stats.cpu_profile = _global_profiler
        
        # Take memory snapshot if we're the last profiler
        if _active_profilers == 1:
            stats.memory_snapshot = tracemalloc.take_snapshot()
        
        # Stop profiling
        _stop_profiling()
        
        # Print summary if we're the top-level profiler
        if _active_profilers == 0:
            print(f"\n=== Performance Profile: {name or 'unnamed'} ===")
            print(f"Wall time: {time.perf_counter() - stats.start_time:.4f}s")
            print(f"I/O wait time: {stats.io_wait_time:.4f}s")
            
            mem_stats = stats._get_memory_stats()
            if mem_stats:
                print(f"Memory usage: {mem_stats['current_mb']:.2f}MB (peak: {mem_stats['peak_mb']:.2f}MB)")
            
            cpu_stats = stats._get_cpu_stats()
            if 'profile_data' in cpu_stats:
                print("\nCPU Profile (top 10 by cumulative time):")
                print(cpu_stats['profile_data'])

def get_memory_usage() -> Dict[str, float]:
    """Get current memory usage statistics."""
    if not tracemalloc.is_tracing():
        tracemalloc.start()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
    else:
        current, peak = tracemalloc.get_traced_memory()
    
    return {
        'current_mb': current / (1024 * 1024),
        'peak_mb': peak / (1024 * 1024)
    }
