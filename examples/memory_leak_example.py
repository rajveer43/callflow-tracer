"""
Memory Leak Detection Examples

This file demonstrates memory leak detection capabilities including:
1. Basic leak detection
2. Object allocation tracking
3. Memory growth pattern analysis
4. Reference cycle detection
5. Real-world leak scenarios
"""

import time
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from callflow_tracer.memory_leak_detector import (
    detect_leaks, track_allocations, get_memory_growth,
    get_top_memory_consumers, find_reference_cycles
)


# Example 1: Basic Leak Detection
print("="*70)
print("EXAMPLE 1: Basic Memory Leak Detection")
print("="*70)

def example1_basic_leak_detection():
    """Detect a simple memory leak."""
    print("\nDetecting memory leaks in code...")
    
    with detect_leaks("memory_leak_example1_basic.html") as detector:
        # Intentional leak: list keeps growing
        leaked_data = []
        
        for i in range(10):
            # Allocate memory that won't be freed
            leaked_data.append([0] * 10000)
            detector.take_snapshot(f"Iteration_{i}")
            time.sleep(0.05)
        
        print(f"Allocated {len(leaked_data)} arrays")
    
    print("✓ Output: memory_leak_example1_basic.html\n")


# Example 2: Track Allocations with Decorator
print("="*70)
print("EXAMPLE 2: Track Allocations with Decorator")
print("="*70)

@track_allocations
def process_large_dataset():
    """Process a large dataset with memory tracking."""
    data = []
    
    # Simulate data processing
    for i in range(100):
        record = {
            'id': i,
            'data': list(range(1000)),
            'metadata': {'timestamp': time.time()}
        }
        data.append(record)
    
    # Process data
    results = [sum(r['data']) for r in data]
    
    return results


def example2_track_allocations():
    """Use decorator to track allocations."""
    print("\nTracking allocations in function...")
    results = process_large_dataset()
    print(f"Processed {len(results)} records")
    print()


# Example 3: Reference Cycle Detection
print("="*70)
print("EXAMPLE 3: Reference Cycle Detection")
print("="*70)

class Node:
    """Node class that can create reference cycles."""
    def __init__(self, value):
        self.value = value
        self.next = None
        self.prev = None


def example3_reference_cycles():
    """Detect reference cycles."""
    print("\nCreating reference cycles...")
    
    with detect_leaks("memory_leak_example3_cycles.html") as detector:
        # Create circular linked list
        nodes = [Node(i) for i in range(10)]
        
        for i in range(len(nodes)):
            nodes[i].next = nodes[(i + 1) % len(nodes)]
            nodes[i].prev = nodes[(i - 1) % len(nodes)]
        
        detector.take_snapshot("After cycle creation")
        
        # Delete references but cycles remain
        del nodes
        
        detector.take_snapshot("After deletion")
        
        # Find cycles
        cycles = find_reference_cycles()
        print(f"Reference cycles found: {len(cycles)}")
    
    print("✓ Output: memory_leak_example3_cycles.html\n")


# Example 4: Memory Growth Monitoring
print("="*70)
print("EXAMPLE 4: Memory Growth Monitoring")
print("="*70)

def example4_memory_growth():
    """Monitor memory growth over time."""
    print("\nMonitoring memory growth...")
    
    # Allocate memory gradually
    data_holder = []
    
    def allocate_more():
        data_holder.append([0] * 50000)
    
    # Monitor growth
    print("Taking measurements...")
    measurements = get_memory_growth(interval=0.3, iterations=5)
    
    for i, m in enumerate(measurements):
        if 'memory_growth' in m:
            print(f"  Measurement {i}: {m['memory_growth']:+,} bytes")
        
        # Allocate between measurements
        if i < 4:
            allocate_more()
    
    print()


# Example 5: Top Memory Consumers
print("="*70)
print("EXAMPLE 5: Top Memory Consumers")
print("="*70)

def example5_top_consumers():
    """Identify top memory consumers."""
    print("\nIdentifying top memory consumers...")
    
    # Allocate various data structures
    large_list = [list(range(10000)) for _ in range(100)]
    large_dict = {i: [0] * 1000 for i in range(500)}
    large_string = "x" * 1000000
    
    # Get top consumers
    consumers = get_top_memory_consumers(limit=10)
    
    print(f"\nTop {len(consumers)} memory consumers:")
    for i, consumer in enumerate(consumers[:5]):
        print(f"  #{i+1}: {consumer['size_mb']:.2f} MB - {consumer['file']}")
    
    print()


# Example 6: Real-world Scenario - Cache Leak
print("="*70)
print("EXAMPLE 6: Real-world Cache Leak")
print("="*70)

class LeakyCache:
    """Cache that leaks memory by never evicting entries."""
    def __init__(self):
        self.cache = {}
    
    def get(self, key):
        return self.cache.get(key)
    
    def set(self, key, value):
        # BUG: Never removes old entries!
        self.cache[key] = value


def example6_cache_leak():
    """Detect memory leak in cache implementation."""
    print("\nDetecting cache memory leak...")
    
    with detect_leaks("memory_leak_example6_cache.html") as detector:
        cache = LeakyCache()
        
        # Simulate cache usage
        for i in range(1000):
            # Generate unique keys (cache never evicts)
            key = f"key_{i}"
            value = [0] * 1000  # 1KB per entry
            cache.set(key, value)
            
            if i % 200 == 0:
                detector.take_snapshot(f"Cache_size_{len(cache.cache)}")
        
        print(f"Cache size: {len(cache.cache)} entries")
        print(f"Estimated memory: {len(cache.cache) * 1000 * 8 / 1024:.2f} KB")
    
    print("✓ Output: memory_leak_example6_cache.html\n")


# Example 7: Event Listener Leak
print("="*70)
print("EXAMPLE 7: Event Listener Leak")
print("="*70)

class EventEmitter:
    """Event emitter that can leak listeners."""
    def __init__(self):
        self.listeners = []
    
    def on(self, callback):
        self.listeners.append(callback)
    
    def emit(self, data):
        for listener in self.listeners:
            listener(data)


def example7_listener_leak():
    """Detect event listener memory leak."""
    print("\nDetecting event listener leak...")
    
    with detect_leaks("memory_leak_example7_listeners.html") as detector:
        emitter = EventEmitter()
        
        # Add many listeners that are never removed
        for i in range(500):
            # Each lambda captures variables (potential leak)
            data = [0] * 100
            emitter.on(lambda x, d=data: len(d) + x)
            
            if i % 100 == 0:
                detector.take_snapshot(f"Listeners_{len(emitter.listeners)}")
        
        print(f"Total listeners: {len(emitter.listeners)}")
    
    print("✓ Output: memory_leak_example7_listeners.html\n")


# Example 8: Database Connection Leak
print("="*70)
print("EXAMPLE 8: Database Connection Leak")
print("="*70)

class DatabaseConnection:
    """Simulated database connection."""
    def __init__(self, conn_id):
        self.conn_id = conn_id
        self.buffer = [0] * 10000  # 10KB buffer per connection
    
    def query(self, sql):
        return f"Result from connection {self.conn_id}"
    
    def close(self):
        self.buffer = None


class ConnectionPool:
    """Connection pool that leaks connections."""
    def __init__(self):
        self.connections = []
        self.next_id = 0
    
    def get_connection(self):
        conn = DatabaseConnection(self.next_id)
        self.next_id += 1
        self.connections.append(conn)
        return conn
    
    def release_connection(self, conn):
        # BUG: Never actually removes from pool!
        pass


def example8_connection_leak():
    """Detect database connection leak."""
    print("\nDetecting connection pool leak...")
    
    with detect_leaks("memory_leak_example8_connections.html") as detector:
        pool = ConnectionPool()
        
        # Simulate many requests
        for i in range(100):
            conn = pool.get_connection()
            result = conn.query("SELECT * FROM users")
            pool.release_connection(conn)  # Doesn't actually release!
            
            if i % 20 == 0:
                detector.take_snapshot(f"Connections_{len(pool.connections)}")
        
        print(f"Leaked connections: {len(pool.connections)}")
        print(f"Estimated memory: {len(pool.connections) * 10 / 1024:.2f} MB")
    
    print("✓ Output: memory_leak_example8_connections.html\n")


# Example 9: Closure Leak
print("="*70)
print("EXAMPLE 9: Closure Memory Leak")
print("="*70)

def example9_closure_leak():
    """Detect memory leak from closures."""
    print("\nDetecting closure leak...")
    
    with detect_leaks("memory_leak_example9_closures.html") as detector:
        callbacks = []
        
        for i in range(200):
            # Large data captured by closure
            large_data = [0] * 5000
            
            # Closure captures large_data
            def callback(x, data=large_data):
                return len(data) + x
            
            callbacks.append(callback)
            
            if i % 40 == 0:
                detector.take_snapshot(f"Closures_{len(callbacks)}")
        
        print(f"Total closures: {len(callbacks)}")
    
    print("✓ Output: memory_leak_example9_closures.html\n")


# Example 10: Good Code (No Leaks)
print("="*70)
print("EXAMPLE 10: Good Code (No Leaks)")
print("="*70)

def example10_no_leaks():
    """Example of code with no memory leaks."""
    print("\nAnalyzing clean code...")
    
    with detect_leaks("memory_leak_example10_clean.html") as detector:
        # Proper resource management
        for i in range(10):
            # Data is properly scoped
            data = [0] * 10000
            result = sum(data)
            # data goes out of scope and is freed
            
            detector.take_snapshot(f"Iteration_{i}")
        
        print("Clean code - no leaks expected")
    
    print("✓ Output: memory_leak_example10_clean.html\n")


# Main execution
def run_all_examples():
    """Run all memory leak detection examples."""
    print("\n" + "="*70)
    print("MEMORY LEAK DETECTION EXAMPLES")
    print("="*70 + "\n")
    
    examples = [
        example1_basic_leak_detection,
        example2_track_allocations,
        example3_reference_cycles,
        example4_memory_growth,
        example5_top_consumers,
        example6_cache_leak,
        example7_listener_leak,
        example8_connection_leak,
        example9_closure_leak,
        example10_no_leaks,
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"❌ Error in {example.__name__}: {e}")
            import traceback
            traceback.print_exc()
    
    print("="*70)
    print("✅ ALL EXAMPLES COMPLETED!")
    print("="*70)
    print("\nGenerated files:")
    print("  - memory_leak_example1_basic.html")
    print("  - memory_leak_example3_cycles.html")
    print("  - memory_leak_example6_cache.html")
    print("  - memory_leak_example7_listeners.html")
    print("  - memory_leak_example8_connections.html")
    print("  - memory_leak_example9_closures.html")
    print("  - memory_leak_example10_clean.html")
    print("\nOpen these files in your browser to see memory leak reports!")


if __name__ == "__main__":
    run_all_examples()
