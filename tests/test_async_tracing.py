"""
Comprehensive tests for async tracing functionality.
"""

import asyncio
import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from callflow_tracer.async_tracer import (
    trace_async, trace_scope_async, gather_traced,
    AsyncCallGraph, get_async_stats
)


# Test 1: Basic async function tracing
@trace_async
async def simple_async_function():
    """Simple async function for testing."""
    await asyncio.sleep(0.01)
    return "Hello, Async!"


async def test_basic_async_tracing():
    """Test basic async function tracing."""
    print("\n" + "="*60)
    print("TEST 1: Basic Async Function Tracing")
    print("="*60)
    
    async with trace_scope_async() as graph:
        result = await simple_async_function()
        print(f"Result: {result}")
    
    assert isinstance(graph, AsyncCallGraph)
    assert len(graph.nodes) > 0
    print(f"✓ Traced {len(graph.nodes)} async function(s)")
    print(f"✓ Graph duration: {graph.to_dict()['metadata']['duration']:.3f}s")
    return True


# Test 2: Multiple async calls
@trace_async
async def fetch_data(item_id: int):
    """Simulate fetching data."""
    await asyncio.sleep(0.02)
    return f"Data for item {item_id}"


async def test_multiple_async_calls():
    """Test tracing multiple async calls."""
    print("\n" + "="*60)
    print("TEST 2: Multiple Async Calls")
    print("="*60)
    
    async with trace_scope_async() as graph:
        results = []
        for i in range(5):
            result = await fetch_data(i)
            results.append(result)
        
        print(f"Fetched {len(results)} items")
    
    assert len(results) == 5
    print(f"✓ Traced {len(graph.nodes)} function(s)")
    print(f"✓ Total edges: {len(graph.edges)}")
    return True


# Test 3: Concurrent execution with gather
@trace_async
async def process_item(item_id: int):
    """Process an item concurrently."""
    await asyncio.sleep(0.01)
    return item_id * 2


async def test_concurrent_execution():
    """Test tracing concurrent execution."""
    print("\n" + "="*60)
    print("TEST 3: Concurrent Execution with gather_traced")
    print("="*60)
    
    async with trace_scope_async() as graph:
        tasks = [process_item(i) for i in range(10)]
        results = await gather_traced(*tasks)
        
        print(f"Processed {len(results)} items concurrently")
    
    assert len(results) == 10
    assert all(results[i] == i * 2 for i in range(10))
    
    stats = get_async_stats(graph)
    print(f"✓ Async functions: {stats.get('total_async_functions', 0)}")
    print(f"✓ Timeline events: {stats.get('timeline_events', 0)}")
    return True


# Test 4: Nested async calls
@trace_async
async def outer_async():
    """Outer async function."""
    result1 = await inner_async_1()
    result2 = await inner_async_2()
    return f"{result1} + {result2}"


@trace_async
async def inner_async_1():
    """Inner async function 1."""
    await asyncio.sleep(0.01)
    return "Inner1"


@trace_async
async def inner_async_2():
    """Inner async function 2."""
    await asyncio.sleep(0.01)
    return "Inner2"


async def test_nested_async_calls():
    """Test tracing nested async calls."""
    print("\n" + "="*60)
    print("TEST 4: Nested Async Calls")
    print("="*60)
    
    async with trace_scope_async() as graph:
        result = await outer_async()
        print(f"Result: {result}")
    
    assert "Inner1" in result and "Inner2" in result
    print(f"✓ Traced {len(graph.nodes)} function(s)")
    print(f"✓ Call relationships: {len(graph.edges)}")
    return True


# Test 5: Async with exception handling
@trace_async
async def risky_async_function(should_fail: bool = False):
    """Async function that might raise an exception."""
    await asyncio.sleep(0.01)
    if should_fail:
        raise ValueError("Intentional error")
    return "Success"


async def test_async_exception_handling():
    """Test async tracing with exceptions."""
    print("\n" + "="*60)
    print("TEST 5: Async Exception Handling")
    print("="*60)
    
    async with trace_scope_async() as graph:
        # Success case
        result1 = await risky_async_function(False)
        print(f"Success result: {result1}")
        
        # Failure case
        try:
            result2 = await risky_async_function(True)
        except ValueError as e:
            print(f"Caught expected error: {e}")
    
    print(f"✓ Traced {len(graph.nodes)} function(s) despite exception")
    return True


# Test 6: Export async trace to HTML
async def test_async_export_html():
    """Test exporting async trace to HTML."""
    print("\n" + "="*60)
    print("TEST 6: Export Async Trace to HTML")
    print("="*60)
    
    output_file = "test_async_trace.html"
    
    async with trace_scope_async(output_file) as graph:
        tasks = [process_item(i) for i in range(5)]
        await gather_traced(*tasks)
    
    assert os.path.exists(output_file)
    file_size = os.path.getsize(output_file)
    print(f"✓ Created {output_file} ({file_size} bytes)")
    
    # Clean up
    # if os.path.exists(output_file):
    #     os.remove(output_file)
    #     print(f"✓ Cleaned up {output_file}")
    
    return True


# Test 7: Async statistics
@trace_async
async def fast_async():
    """Fast async function."""
    await asyncio.sleep(0.001)
    return "fast"


@trace_async
async def slow_async():
    """Slow async function."""
    await asyncio.sleep(0.05)
    return "slow"


async def test_async_statistics():
    """Test async-specific statistics."""
    print("\n" + "="*60)
    print("TEST 7: Async Statistics")
    print("="*60)
    
    async with trace_scope_async() as graph:
        await fast_async()
        await slow_async()
        await fast_async()
    
    stats = get_async_stats(graph)
    
    print(f"✓ Total async functions: {stats.get('total_async_functions', 0)}")
    print(f"✓ Total async time: {stats.get('total_async_time', 0):.3f}s")
    print(f"✓ Total await time: {stats.get('total_await_time', 0):.3f}s")
    print(f"✓ Total active time: {stats.get('total_active_time', 0):.3f}s")
    print(f"✓ Efficiency: {stats.get('efficiency', 0):.2f}%")
    
    assert stats.get('total_async_functions', 0) > 0
    return True


# Test 8: Mixed sync and async (async calling sync)
def sync_helper():
    """Synchronous helper function."""
    time.sleep(0.01)
    return "sync_result"


@trace_async
async def async_with_sync():
    """Async function that calls sync code."""
    result = sync_helper()
    await asyncio.sleep(0.01)
    return f"async + {result}"


async def test_mixed_sync_async():
    """Test async functions calling sync code."""
    print("\n" + "="*60)
    print("TEST 8: Mixed Sync and Async")
    print("="*60)
    
    async with trace_scope_async() as graph:
        result = await async_with_sync()
        print(f"Result: {result}")
    
    assert "sync_result" in result
    print(f"✓ Traced {len(graph.nodes)} function(s)")
    return True


# Test 9: Async with parameters
@trace_async
async def async_with_params(name: str, count: int, **kwargs):
    """Async function with various parameters."""
    await asyncio.sleep(0.01)
    return f"{name} called {count} times with {kwargs}"


async def test_async_with_parameters():
    """Test async tracing with function parameters."""
    print("\n" + "="*60)
    print("TEST 9: Async with Parameters")
    print("="*60)
    
    async with trace_scope_async() as graph:
        result = await async_with_params("test", 5, extra="data")
        print(f"Result: {result}")
    
    assert "test" in result and "5" in result
    print(f"✓ Traced function with parameters")
    return True


# Test 10: Concurrent tasks tracking
@trace_async
async def concurrent_task(task_id: int):
    """Task for concurrent execution."""
    await asyncio.sleep(0.02)
    return f"Task {task_id} complete"


async def test_concurrent_tracking():
    """Test tracking of concurrent task execution."""
    print("\n" + "="*60)
    print("TEST 10: Concurrent Tasks Tracking")
    print("="*60)
    
    async with trace_scope_async() as graph:
        tasks = [concurrent_task(i) for i in range(20)]
        results = await gather_traced(*tasks)
        
        print(f"Completed {len(results)} concurrent tasks")
    
    stats = get_async_stats(graph)
    max_concurrent = stats.get('max_concurrent_tasks', 0)
    
    print(f"✓ Max concurrent tasks: {max_concurrent}")
    print(f"✓ Timeline events: {stats.get('timeline_events', 0)}")
    
    assert len(results) == 20
    return True


# Main test runner
async def run_all_tests():
    """Run all async tracing tests."""
    print("\n" + "="*70)
    print("ASYNC TRACING TEST SUITE")
    print("="*70)
    
    tests = [
        ("Basic Async Tracing", test_basic_async_tracing),
        ("Multiple Async Calls", test_multiple_async_calls),
        ("Concurrent Execution", test_concurrent_execution),
        ("Nested Async Calls", test_nested_async_calls),
        ("Exception Handling", test_async_exception_handling),
        ("Export to HTML", test_async_export_html),
        ("Async Statistics", test_async_statistics),
        ("Mixed Sync/Async", test_mixed_sync_async),
        ("Async with Parameters", test_async_with_parameters),
        ("Concurrent Tracking", test_concurrent_tracking),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            result = await test_func()
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
    # Run the async test suite
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
