"""
Async/Await Tracing Examples

This file demonstrates various async tracing capabilities including:
1. Basic async function tracing
2. Concurrent execution with asyncio.gather
3. Nested async calls
4. Real-world async patterns (API calls, database queries)
5. Performance analysis of async code
"""

import asyncio
import random
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from callflow_tracer.async_tracer import (
    trace_async, trace_scope_async, gather_traced, get_async_stats
)


# Example 1: Basic Async Function
print("="*70)
print("EXAMPLE 1: Basic Async Function Tracing")
print("="*70)

@trace_async
async def fetch_user(user_id: int):
    """Simulate fetching user data from API."""
    await asyncio.sleep(0.1)  # Simulate network delay
    return {
        'id': user_id,
        'name': f'User{user_id}',
        'email': f'user{user_id}@example.com'
    }


async def example1_basic_async():
    """Basic async function tracing."""
    async with trace_scope_async("async_example1_basic.html") as graph:
        user = await fetch_user(1)
        print(f"Fetched user: {user['name']}")
    
    print(f"✓ Traced {len(graph.nodes)} async function(s)")
    print(f"✓ Output: async_example1_basic.html\n")


# Example 2: Concurrent Execution
print("="*70)
print("EXAMPLE 2: Concurrent Execution with gather")
print("="*70)

@trace_async
async def fetch_product(product_id: int):
    """Simulate fetching product data."""
    await asyncio.sleep(random.uniform(0.05, 0.15))
    return {
        'id': product_id,
        'name': f'Product {product_id}',
        'price': random.uniform(10, 100)
    }


async def example2_concurrent():
    """Demonstrate concurrent async execution."""
    async with trace_scope_async("async_example2_concurrent.html") as graph:
        # Fetch multiple products concurrently
        product_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        tasks = [fetch_product(pid) for pid in product_ids]
        
        print("Fetching 10 products concurrently...")
        products = await gather_traced(*tasks)
        print(f"Fetched {len(products)} products")
    
    stats = get_async_stats(graph)
    print(f"✓ Max concurrent tasks: {stats.get('max_concurrent_tasks', 0)}")
    print(f"✓ Total async time: {stats.get('total_async_time', 0):.3f}s")
    print(f"✓ Output: async_example2_concurrent.html\n")


# Example 3: Nested Async Calls
print("="*70)
print("EXAMPLE 3: Nested Async Calls")
print("="*70)

@trace_async
async def fetch_user_profile(user_id: int):
    """Fetch complete user profile with nested calls."""
    user = await fetch_user(user_id)
    orders = await fetch_user_orders(user_id)
    preferences = await fetch_user_preferences(user_id)
    
    return {
        **user,
        'orders': orders,
        'preferences': preferences
    }


@trace_async
async def fetch_user_orders(user_id: int):
    """Fetch user's order history."""
    await asyncio.sleep(0.08)
    return [f'Order{i}' for i in range(1, 4)]


@trace_async
async def fetch_user_preferences(user_id: int):
    """Fetch user preferences."""
    await asyncio.sleep(0.05)
    return {'theme': 'dark', 'language': 'en'}


async def example3_nested():
    """Demonstrate nested async calls."""
    async with trace_scope_async("async_example3_nested.html") as graph:
        profile = await fetch_user_profile(1)
        print(f"Fetched profile for: {profile['name']}")
        print(f"  Orders: {len(profile['orders'])}")
        print(f"  Preferences: {profile['preferences']}")
    
    print(f"✓ Traced {len(graph.nodes)} function(s)")
    print(f"✓ Call relationships: {len(graph.edges)}")
    print(f"✓ Output: async_example3_nested.html\n")


# Example 4: Real-world API Pattern
print("="*70)
print("EXAMPLE 4: Real-world API Pattern")
print("="*70)

@trace_async
async def fetch_from_api(endpoint: str):
    """Simulate API call."""
    await asyncio.sleep(random.uniform(0.05, 0.2))
    return {'endpoint': endpoint, 'data': f'Data from {endpoint}'}


@trace_async
async def fetch_from_database(query: str):
    """Simulate database query."""
    await asyncio.sleep(random.uniform(0.03, 0.1))
    return {'query': query, 'rows': random.randint(1, 100)}


@trace_async
async def fetch_from_cache(key: str):
    """Simulate cache lookup."""
    await asyncio.sleep(0.01)  # Cache is fast
    return {'key': key, 'value': f'Cached value for {key}'}


@trace_async
async def process_request(request_id: int):
    """Process a complete request with multiple data sources."""
    # Fetch from different sources concurrently
    api_task = fetch_from_api(f'/api/data/{request_id}')
    db_task = fetch_from_database(f'SELECT * FROM data WHERE id={request_id}')
    cache_task = fetch_from_cache(f'request_{request_id}')
    
    api_data, db_data, cache_data = await gather_traced(
        api_task, db_task, cache_task
    )
    
    return {
        'request_id': request_id,
        'api': api_data,
        'database': db_data,
        'cache': cache_data
    }


async def example4_realworld():
    """Demonstrate real-world async pattern."""
    async with trace_scope_async("async_example4_realworld.html") as graph:
        # Process multiple requests concurrently
        requests = [process_request(i) for i in range(1, 6)]
        results = await gather_traced(*requests)
        
        print(f"Processed {len(results)} requests")
        for result in results:
            print(f"  Request {result['request_id']}: "
                  f"API={result['api']['endpoint']}, "
                  f"DB={result['database']['rows']} rows")
    
    stats = get_async_stats(graph)
    print(f"\n✓ Total async functions: {stats.get('total_async_functions', 0)}")
    print(f"✓ Efficiency: {stats.get('efficiency', 0):.2f}%")
    print(f"✓ Output: async_example4_realworld.html\n")


# Example 5: Performance Analysis
print("="*70)
print("EXAMPLE 5: Async Performance Analysis")
print("="*70)

@trace_async
async def slow_operation():
    """Intentionally slow operation."""
    await asyncio.sleep(0.2)
    return "slow"


@trace_async
async def fast_operation():
    """Fast operation."""
    await asyncio.sleep(0.01)
    return "fast"


@trace_async
async def medium_operation():
    """Medium speed operation."""
    await asyncio.sleep(0.05)
    return "medium"


async def example5_performance():
    """Analyze performance of different async operations."""
    async with trace_scope_async("async_example5_performance.html") as graph:
        # Run operations multiple times
        print("Running performance test...")
        
        tasks = []
        for _ in range(5):
            tasks.append(fast_operation())
        for _ in range(3):
            tasks.append(medium_operation())
        for _ in range(2):
            tasks.append(slow_operation())
        
        results = await gather_traced(*tasks)
        print(f"Completed {len(results)} operations")
    
    stats = get_async_stats(graph)
    print(f"\n📊 Performance Statistics:")
    print(f"  Total async time: {stats.get('total_async_time', 0):.3f}s")
    print(f"  Total await time: {stats.get('total_await_time', 0):.3f}s")
    print(f"  Total active time: {stats.get('total_active_time', 0):.3f}s")
    print(f"  Efficiency: {stats.get('efficiency', 0):.2f}%")
    print(f"  Max concurrent: {stats.get('max_concurrent_tasks', 0)}")
    print(f"\n✓ Output: async_example5_performance.html\n")


# Example 6: Error Handling
print("="*70)
print("EXAMPLE 6: Async Error Handling")
print("="*70)

@trace_async
async def risky_operation(should_fail: bool = False):
    """Operation that might fail."""
    await asyncio.sleep(0.05)
    if should_fail:
        raise ValueError("Operation failed!")
    return "success"


async def example6_error_handling():
    """Demonstrate error handling in async tracing."""
    async with trace_scope_async("async_example6_errors.html") as graph:
        # Mix of successful and failed operations
        results = []
        
        # Successful operations
        for i in range(3):
            try:
                result = await risky_operation(False)
                results.append(('success', result))
            except Exception as e:
                results.append(('error', str(e)))
        
        # Failed operations
        for i in range(2):
            try:
                result = await risky_operation(True)
                results.append(('success', result))
            except Exception as e:
                results.append(('error', str(e)))
        
        successes = sum(1 for status, _ in results if status == 'success')
        failures = sum(1 for status, _ in results if status == 'error')
        
        print(f"Operations: {successes} succeeded, {failures} failed")
    
    print(f"✓ Traced {len(graph.nodes)} function(s) with error handling")
    print(f"✓ Output: async_example6_errors.html\n")


# Example 7: Async Pipeline
print("="*70)
print("EXAMPLE 7: Async Data Pipeline")
print("="*70)

@trace_async
async def extract_data(source: str):
    """Extract data from source."""
    await asyncio.sleep(0.1)
    return [f'data_{i}' for i in range(10)]


@trace_async
async def transform_data(data: list):
    """Transform extracted data."""
    await asyncio.sleep(0.08)
    return [item.upper() for item in data]


@trace_async
async def load_data(data: list, destination: str):
    """Load transformed data to destination."""
    await asyncio.sleep(0.06)
    return f"Loaded {len(data)} items to {destination}"


@trace_async
async def run_pipeline(source: str, destination: str):
    """Run complete ETL pipeline."""
    # Sequential pipeline stages
    raw_data = await extract_data(source)
    transformed_data = await transform_data(raw_data)
    result = await load_data(transformed_data, destination)
    return result


async def example7_pipeline():
    """Demonstrate async data pipeline."""
    async with trace_scope_async("async_example7_pipeline.html") as graph:
        # Run multiple pipelines concurrently
        pipelines = [
            run_pipeline(f'source_{i}', f'dest_{i}')
            for i in range(3)
        ]
        
        results = await gather_traced(*pipelines)
        
        for i, result in enumerate(results):
            print(f"Pipeline {i+1}: {result}")
    
    print(f"\n✓ Traced complete ETL pipeline")
    print(f"✓ Output: async_example7_pipeline.html\n")


# Main execution
async def run_all_examples():
    """Run all async examples."""
    print("\n" + "="*70)
    print("ASYNC TRACING EXAMPLES")
    print("="*70 + "\n")
    
    examples = [
        example1_basic_async,
        example2_concurrent,
        example3_nested,
        example4_realworld,
        example5_performance,
        example6_error_handling,
        example7_pipeline,
    ]
    
    for example in examples:
        try:
            await example()
        except Exception as e:
            print(f"❌ Error in {example.__name__}: {e}")
            import traceback
            traceback.print_exc()
    
    print("="*70)
    print("✅ ALL EXAMPLES COMPLETED!")
    print("="*70)
    print("\nGenerated files:")
    print("  - async_example1_basic.html")
    print("  - async_example2_concurrent.html")
    print("  - async_example3_nested.html")
    print("  - async_example4_realworld.html")
    print("  - async_example5_performance.html")
    print("  - async_example6_errors.html")
    print("  - async_example7_pipeline.html")
    print("\nOpen these files in your browser to explore the async call graphs!")


if __name__ == "__main__":
    asyncio.run(run_all_examples())
