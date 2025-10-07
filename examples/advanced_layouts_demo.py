"""
Advanced Graph Layouts Demo

This example demonstrates all the advanced graph layout options available in callflow-tracer:
- Hierarchical (default)
- Force-Directed
- Circular
- Radial Tree
- Grid
- Tree (Vertical)
- Tree (Horizontal)
- Timeline
- Organic (Spring)

Each layout can be customized with different spacing options.
"""

from callflow_tracer import trace, trace_scope
import time


@trace
def database_query(query: str):
    """Simulate a database query"""
    time.sleep(0.01)
    return f"Results for: {query}"


@trace
def cache_lookup(key: str):
    """Simulate cache lookup"""
    time.sleep(0.005)
    return None


@trace
def fetch_user_data(user_id: int):
    """Fetch user data with caching"""
    cached = cache_lookup(f"user_{user_id}")
    if cached:
        return cached
    
    result = database_query(f"SELECT * FROM users WHERE id={user_id}")
    return result


@trace
def fetch_user_posts(user_id: int):
    """Fetch user posts"""
    return database_query(f"SELECT * FROM posts WHERE user_id={user_id}")


@trace
def fetch_user_comments(user_id: int):
    """Fetch user comments"""
    return database_query(f"SELECT * FROM comments WHERE user_id={user_id}")


@trace
def aggregate_user_activity(user_id: int):
    """Aggregate all user activity"""
    user = fetch_user_data(user_id)
    posts = fetch_user_posts(user_id)
    comments = fetch_user_comments(user_id)
    
    return {
        'user': user,
        'posts': posts,
        'comments': comments
    }


@trace
def process_analytics(user_ids: list):
    """Process analytics for multiple users"""
    results = []
    for user_id in user_ids:
        activity = aggregate_user_activity(user_id)
        results.append(activity)
    return results


@trace
def send_notification(user_id: int, message: str):
    """Send notification to user"""
    time.sleep(0.008)
    return f"Notification sent to user {user_id}"


@trace
def validate_input(data: dict):
    """Validate input data"""
    time.sleep(0.003)
    return True


@trace
def transform_data(data: dict):
    """Transform data for processing"""
    time.sleep(0.007)
    return data


@trace
def save_to_database(data: dict):
    """Save processed data to database"""
    database_query("INSERT INTO processed_data VALUES (...)")
    return True


@trace
def process_user_request(user_id: int, data: dict):
    """Main request processing pipeline"""
    # Validate
    if not validate_input(data):
        return {"error": "Invalid input"}
    
    # Transform
    transformed = transform_data(data)
    
    # Get user context
    user_activity = aggregate_user_activity(user_id)
    
    # Save results
    save_to_database(transformed)
    
    # Send notification
    send_notification(user_id, "Request processed successfully")
    
    return {"status": "success", "data": transformed}


@trace
def batch_process_requests(requests: list):
    """Process multiple requests in batch"""
    results = []
    for req in requests:
        result = process_user_request(req['user_id'], req['data'])
        results.append(result)
    
    # Run analytics
    user_ids = [req['user_id'] for req in requests]
    analytics = process_analytics(user_ids)
    
    return {
        'results': results,
        'analytics': analytics
    }


def main():
    """Main function to demonstrate the call flow"""
    
    # Simulate some requests
    requests = [
        {'user_id': 1, 'data': {'action': 'update_profile'}},
        {'user_id': 2, 'data': {'action': 'create_post'}},
        {'user_id': 3, 'data': {'action': 'add_comment'}},
    ]
    
    # Process batch
    results = batch_process_requests(requests)
    
    print(f"Processed {len(results['results'])} requests")
    print(f"Analytics generated for {len(results['analytics'])} users")


if __name__ == "__main__":
    print("=" * 70)
    print("Advanced Graph Layouts Demo")
    print("=" * 70)
    print("\nThis demo will generate an interactive HTML visualization with")
    print("multiple advanced layout options:\n")
    print("  📊 Hierarchical - Traditional top-down tree structure")
    print("  🌀 Force-Directed - Physics-based organic layout")
    print("  ⭕ Circular - Nodes arranged in a circle")
    print("  🎯 Radial Tree - Concentric circles by depth level")
    print("  📐 Grid - Uniform grid pattern")
    print("  🌲 Tree (Vertical) - Enhanced vertical tree with spacing")
    print("  🌳 Tree (Horizontal) - Left-to-right tree layout")
    print("  ⏱️  Timeline - Sorted by execution time")
    print("  🌿 Organic (Spring) - Natural spring-based layout")
    print("\n" + "=" * 70)
    print("\nRunning traced functions...")
    
    with trace_scope("advanced_layouts_demo.html"):
        main()
    
    print("\n" + "=" * 70)
    print("✅ Demo complete!")
    print("\nOpen 'advanced_layouts_demo.html' in your browser to explore")
    print("the different graph layouts using the dropdown menu.")
    print("\n💡 Tips:")
    print("  - Use the 'Layout' dropdown to switch between layouts")
    print("  - Adjust 'Node Spacing' to customize the layout density")
    print("  - Toggle 'Physics' for dynamic vs. static layouts")
    print("  - Use 'Filter by module' to focus on specific parts")
    print("  - Export your favorite layout as PNG or JSON")
    print("=" * 70)
