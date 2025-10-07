"""
Memory Leak Detection for callflow-tracer.

This module provides comprehensive memory leak detection including:
- Object allocation tracking
- Reference counting analysis
- Memory growth pattern detection
- Leak visualization
"""

import gc
import sys
import tracemalloc
import weakref
import time
from typing import Dict, List, Optional, Any, Set, Tuple
from collections import defaultdict
from contextlib import contextmanager
import traceback


class ObjectTracker:
    """Track object allocations and references."""
    
    def __init__(self):
        self.tracked_objects = weakref.WeakValueDictionary()
        self.allocation_traces = {}
        self.object_types = defaultdict(int)
        self.allocation_timeline = []
        self.reference_counts = {}
        self.start_time = None
    
    def track_object(self, obj, allocation_info: Optional[str] = None):
        """Track a new object allocation."""
        obj_id = id(obj)
        obj_type = type(obj).__name__
        
        try:
            self.tracked_objects[obj_id] = obj
            self.object_types[obj_type] += 1
            self.reference_counts[obj_id] = sys.getrefcount(obj)
            
            # Store allocation trace
            if allocation_info is None:
                allocation_info = ''.join(traceback.format_stack()[:-1])
            
            self.allocation_traces[obj_id] = {
                'type': obj_type,
                'time': time.time() - (self.start_time or time.time()),
                'trace': allocation_info,
                'size': sys.getsizeof(obj)
            }
            
            self.allocation_timeline.append({
                'time': time.time() - (self.start_time or time.time()),
                'obj_id': obj_id,
                'type': obj_type,
                'action': 'allocated',
                'refcount': sys.getrefcount(obj)
            })
        except TypeError:
            # Some objects can't be weakly referenced
            pass
    
    def get_live_objects(self) -> Dict[int, Any]:
        """Get all currently live tracked objects."""
        return dict(self.tracked_objects)
    
    def get_object_stats(self) -> Dict[str, Any]:
        """Get statistics about tracked objects."""
        live_objects = self.get_live_objects()
        
        type_counts = defaultdict(int)
        for obj in live_objects.values():
            type_counts[type(obj).__name__] += 1
        
        return {
            'total_tracked': len(self.allocation_traces),
            'currently_live': len(live_objects),
            'leaked_count': len(self.allocation_traces) - len(live_objects),
            'type_distribution': dict(type_counts),
            'timeline_events': len(self.allocation_timeline)
        }


class MemorySnapshot:
    """Snapshot of memory state at a point in time."""
    
    def __init__(self, label: str = ""):
        self.label = label
        self.timestamp = time.time()
        self.tracemalloc_snapshot = None
        self.gc_stats = None
        self.object_counts = {}
        self.memory_usage = 0
        
        # Take snapshot
        if tracemalloc.is_tracing():
            self.tracemalloc_snapshot = tracemalloc.take_snapshot()
        
        # Get GC stats
        self.gc_stats = {
            'collections': gc.get_count(),
            'objects': len(gc.get_objects()),
            'garbage': len(gc.garbage)
        }
        
        # Count objects by type
        for obj in gc.get_objects():
            obj_type = type(obj).__name__
            self.object_counts[obj_type] = self.object_counts.get(obj_type, 0) + 1
        
        # Get memory usage
        if tracemalloc.is_tracing():
            current, peak = tracemalloc.get_traced_memory()
            self.memory_usage = current
    
    def compare_to(self, other: 'MemorySnapshot') -> Dict[str, Any]:
        """Compare this snapshot to another."""
        comparison = {
            'time_diff': self.timestamp - other.timestamp,
            'memory_diff': self.memory_usage - other.memory_usage,
            'objects_diff': self.gc_stats['objects'] - other.gc_stats['objects'],
            'type_changes': {}
        }
        
        # Compare object counts by type
        all_types = set(self.object_counts.keys()) | set(other.object_counts.keys())
        for obj_type in all_types:
            current_count = self.object_counts.get(obj_type, 0)
            previous_count = other.object_counts.get(obj_type, 0)
            diff = current_count - previous_count
            
            if diff != 0:
                comparison['type_changes'][obj_type] = {
                    'before': previous_count,
                    'after': current_count,
                    'diff': diff
                }
        
        # Compare tracemalloc snapshots
        if self.tracemalloc_snapshot and other.tracemalloc_snapshot:
            top_stats = self.tracemalloc_snapshot.compare_to(
                other.tracemalloc_snapshot, 'lineno'
            )
            comparison['top_allocations'] = [
                {
                    'file': stat.traceback.format()[0] if stat.traceback else 'unknown',
                    'size_diff': stat.size_diff,
                    'count_diff': stat.count_diff
                }
                for stat in top_stats[:10]
            ]
        
        return comparison


class MemoryLeakDetector:
    """Main memory leak detector."""
    
    def __init__(self):
        self.object_tracker = ObjectTracker()
        self.snapshots: List[MemorySnapshot] = []
        self.growth_patterns: List[Dict[str, Any]] = []
        self.suspected_leaks: List[Dict[str, Any]] = []
        self.enabled = False
        self.start_time = None
        self.tracemalloc_started = False
    
    def start(self):
        """Start memory leak detection."""
        if self.enabled:
            return
        
        self.enabled = True
        self.start_time = time.time()
        self.object_tracker.start_time = self.start_time
        
        # Start tracemalloc if not already started
        if not tracemalloc.is_tracing():
            tracemalloc.start(25)  # Track up to 25 frames
            self.tracemalloc_started = True
        
        # Take initial snapshot
        self.take_snapshot("Initial")
        
        # Enable garbage collection debugging
        gc.set_debug(gc.DEBUG_STATS)
    
    def stop(self):
        """Stop memory leak detection."""
        if not self.enabled:
            return
        
        self.enabled = False
        
        # Take final snapshot
        self.take_snapshot("Final")
        
        # Analyze for leaks
        self.analyze_leaks()
        
        # Stop tracemalloc if we started it
        if self.tracemalloc_started:
            tracemalloc.stop()
            self.tracemalloc_started = False
        
        # Disable GC debugging
        gc.set_debug(0)
    
    def take_snapshot(self, label: str = ""):
        """Take a memory snapshot."""
        snapshot = MemorySnapshot(label or f"Snapshot_{len(self.snapshots)}")
        self.snapshots.append(snapshot)
        return snapshot
    
    def analyze_growth_pattern(self):
        """Analyze memory growth patterns."""
        if len(self.snapshots) < 2:
            return
        
        for i in range(1, len(self.snapshots)):
            comparison = self.snapshots[i].compare_to(self.snapshots[i-1])
            
            # Detect growth
            if comparison['memory_diff'] > 0:
                growth_rate = comparison['memory_diff'] / comparison['time_diff']
                
                pattern = {
                    'from_snapshot': self.snapshots[i-1].label,
                    'to_snapshot': self.snapshots[i].label,
                    'memory_growth': comparison['memory_diff'],
                    'time_elapsed': comparison['time_diff'],
                    'growth_rate': growth_rate,
                    'object_growth': comparison['objects_diff'],
                    'type_changes': comparison['type_changes']
                }
                
                self.growth_patterns.append(pattern)
    
    def analyze_leaks(self):
        """Analyze collected data for memory leaks."""
        self.analyze_growth_pattern()
        
        # Check for objects that should have been freed
        obj_stats = self.object_tracker.get_object_stats()
        
        if obj_stats['leaked_count'] > 0:
            self.suspected_leaks.append({
                'type': 'unreleased_objects',
                'count': obj_stats['leaked_count'],
                'details': obj_stats['type_distribution']
            })
        
        # Check for continuous memory growth
        if len(self.growth_patterns) >= 2:
            consistent_growth = all(
                p['memory_growth'] > 0 
                for p in self.growth_patterns[-3:]
            )
            
            if consistent_growth:
                avg_growth_rate = sum(
                    p['growth_rate'] 
                    for p in self.growth_patterns[-3:]
                ) / 3
                
                self.suspected_leaks.append({
                    'type': 'continuous_growth',
                    'avg_growth_rate': avg_growth_rate,
                    'patterns': self.growth_patterns[-3:]
                })
        
        # Check for reference cycles
        gc.collect()
        if len(gc.garbage) > 0:
            self.suspected_leaks.append({
                'type': 'reference_cycles',
                'count': len(gc.garbage),
                'objects': [type(obj).__name__ for obj in gc.garbage[:10]]
            })
    
    def get_report(self) -> Dict[str, Any]:
        """Generate comprehensive leak detection report."""
        return {
            'duration': time.time() - (self.start_time or time.time()),
            'snapshots': len(self.snapshots),
            'object_stats': self.object_tracker.get_object_stats(),
            'growth_patterns': self.growth_patterns,
            'suspected_leaks': self.suspected_leaks,
            'snapshot_comparisons': [
                self.snapshots[i].compare_to(self.snapshots[i-1])
                for i in range(1, len(self.snapshots))
            ] if len(self.snapshots) > 1 else []
        }


@contextmanager
def detect_leaks(output_file: Optional[str] = None, snapshot_interval: Optional[float] = None):
    """
    Context manager for memory leak detection.
    
    Args:
        output_file: Optional file to save leak report
        snapshot_interval: Optional interval for automatic snapshots
    
    Usage:
        with detect_leaks("leak_report.html") as detector:
            # Your code here
            potentially_leaky_function()
    """
    detector = MemoryLeakDetector()
    detector.start()
    
    try:
        yield detector
    finally:
        detector.stop()
        
        # Export report if requested
        if output_file:
            from .memory_leak_visualizer import export_leak_report
            export_leak_report(detector, output_file)


def track_allocations(func):
    """
    Decorator to track memory allocations in a function.
    
    Usage:
        @track_allocations
        def my_function():
            # Memory allocations here will be tracked
            pass
    """
    def wrapper(*args, **kwargs):
        detector = MemoryLeakDetector()
        detector.start()
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            detector.stop()
            report = detector.get_report()
            
            # Print summary
            print(f"\n{'='*60}")
            print(f"Memory Allocation Report: {func.__name__}")
            print(f"{'='*60}")
            print(f"Duration: {report['duration']:.3f}s")
            print(f"Snapshots: {report['snapshots']}")
            
            obj_stats = report['object_stats']
            print(f"Objects tracked: {obj_stats['total_tracked']}")
            print(f"Currently live: {obj_stats['currently_live']}")
            print(f"Potential leaks: {obj_stats['leaked_count']}")
            
            if report['suspected_leaks']:
                print(f"\n⚠️  {len(report['suspected_leaks'])} suspected leak(s) detected!")
                for leak in report['suspected_leaks']:
                    print(f"  - {leak['type']}: {leak.get('count', 'N/A')}")
            else:
                print("\n✅ No memory leaks detected!")
            
            print(f"{'='*60}\n")
    
    return wrapper


def find_reference_cycles() -> List[List[Any]]:
    """
    Find reference cycles in current objects.
    
    Returns:
        List of reference cycles found
    """
    gc.collect()
    cycles = []
    
    for obj in gc.garbage:
        referrers = gc.get_referrers(obj)
        if len(referrers) > 0:
            cycle = [obj] + referrers[:5]  # Limit cycle length
            cycles.append(cycle)
    
    return cycles


def get_memory_growth(interval: float = 1.0, iterations: int = 5) -> List[Dict[str, Any]]:
    """
    Monitor memory growth over time.
    
    Args:
        interval: Time between measurements (seconds)
        iterations: Number of measurements to take
    
    Returns:
        List of memory measurements
    """
    measurements = []
    
    for i in range(iterations):
        snapshot = MemorySnapshot(f"Measurement_{i}")
        measurements.append({
            'iteration': i,
            'timestamp': snapshot.timestamp,
            'memory_usage': snapshot.memory_usage,
            'object_count': snapshot.gc_stats['objects']
        })
        
        if i < iterations - 1:
            time.sleep(interval)
    
    # Calculate growth
    for i in range(1, len(measurements)):
        measurements[i]['memory_growth'] = (
            measurements[i]['memory_usage'] - measurements[i-1]['memory_usage']
        )
        measurements[i]['object_growth'] = (
            measurements[i]['object_count'] - measurements[i-1]['object_count']
        )
    
    return measurements


def get_top_memory_consumers(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get the top memory-consuming objects.
    
    Args:
        limit: Number of top consumers to return
    
    Returns:
        List of top memory consumers
    """
    if not tracemalloc.is_tracing():
        tracemalloc.start()
        should_stop = True
    else:
        should_stop = False
    
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    
    consumers = []
    for stat in top_stats[:limit]:
        consumers.append({
            'file': stat.traceback.format()[0] if stat.traceback else 'unknown',
            'size': stat.size,
            'count': stat.count,
            'size_mb': stat.size / 1024 / 1024
        })
    
    if should_stop:
        tracemalloc.stop()
    
    return consumers
