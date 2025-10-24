"""
3D Visualization Demo for CallFlow Tracer

This example demonstrates the 3D visualization feature using Three.js.
The 3D view provides an immersive way to explore function call relationships
with multiple layout algorithms and interactive controls.
"""

import os 
import sys
CURRENT_DIR = os.path.dirname(__file__)
REPO_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from callflow_tracer import trace, export_html_3d, get_current_graph
import time
import random



@trace
def database_query(query: str, table: str):
    """Simulate a database query"""
    time.sleep(random.uniform(0.01, 0.05))
    return f"Results from {table}: {query}"


@trace
def cache_lookup(key: str):
    """Simulate cache lookup"""
    time.sleep(random.uniform(0.001, 0.005))
    # Simulate cache miss
    return None


@trace
def fetch_user_data(user_id: int):
    """Fetch user data with caching"""
    cache_key = f"user_{user_id}"
    cached = cache_lookup(cache_key)
    
    if cached:
        return cached
    
    result = database_query(f"SELECT * FROM users WHERE id={user_id}", "users")
    return result


@trace
def fetch_user_posts(user_id: int):
    """Fetch user posts"""
    return database_query(f"SELECT * FROM posts WHERE user_id={user_id}", "posts")


@trace
def fetch_user_comments(user_id: int):
    """Fetch user comments"""
    return database_query(f"SELECT * FROM comments WHERE user_id={user_id}", "comments")


@trace
def fetch_user_likes(user_id: int):
    """Fetch user likes"""
    return database_query(f"SELECT * FROM likes WHERE user_id={user_id}", "likes")


@trace
def aggregate_user_activity(user_id: int):
    """Aggregate all user activity"""
    user = fetch_user_data(user_id)
    posts = fetch_user_posts(user_id)
    comments = fetch_user_comments(user_id)
    likes = fetch_user_likes(user_id)
    
    return {
        'user': user,
        'posts': posts,
        'comments': comments,
        'likes': likes
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
    time.sleep(random.uniform(0.005, 0.015))
    return f"Notification sent to user {user_id}: {message}"


@trace
def validate_input(data: dict):
    """Validate input data"""
    time.sleep(random.uniform(0.002, 0.008))
    return True


@trace
def transform_data(data: dict):
    """Transform data for processing"""
    time.sleep(random.uniform(0.005, 0.015))
    return {**data, 'transformed': True}


@trace
def save_to_database(data: dict):
    """Save processed data to database"""
    database_query("INSERT INTO processed_data VALUES (...)", "processed_data")
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


@trace
def generate_report(data: dict):
    """Generate report from processed data"""
    time.sleep(random.uniform(0.02, 0.05))
    return f"Report generated: {len(data)} items"


@trace
def send_email_report(report: str):
    """Send report via email"""
    time.sleep(random.uniform(0.01, 0.03))
    return "Email sent successfully"


@trace
def main():
    """Main function to demonstrate the call flow"""
    print("🚀 Starting 3D Visualization Demo...")
    
    # Simulate some requests
    requests = [
        {'user_id': 1, 'data': {'action': 'update_profile', 'value': 'new_name'}},
        {'user_id': 2, 'data': {'action': 'create_post', 'content': 'Hello World'}},
        {'user_id': 3, 'data': {'action': 'add_comment', 'text': 'Great post!'}},
        {'user_id': 4, 'data': {'action': 'like_post', 'post_id': 123}},
    ]
    
    # Process batch
    results = batch_process_requests(requests)
    
    # Generate and send report
    report = generate_report(results)
    send_email_report(report)
    
    print(f"✅ Processed {len(results['results'])} requests")
    print(f"📊 Analytics generated for {len(results['analytics'])} users")
    print(f"📧 Report sent: {report}")


if __name__ == "__main__":
    print("=" * 80)
    print("3D VISUALIZATION DEMO - CallFlow Tracer")
    print("=" * 80)
    print()
    print("This demo will generate an interactive 3D visualization with:")
    print("  🌐 Five 3D layout algorithms:")
    print("     • Force-Directed 3D - Random distribution in 3D space")
    print("     • Sphere - Nodes arranged on sphere surface")
    print("     • Helix - Spiral arrangement")
    print("     • Grid 3D - Cubic grid pattern")
    print("     • Tree 3D - Hierarchical tree in 3D")
    print()
    print("  🎮 Interactive controls:")
    print("     • Mouse drag - Rotate view")
    print("     • Mouse wheel - Zoom in/out")
    print("     • Layout selector - Switch between layouts")
    print("     • Node size slider - Adjust node sizes")
    print("     • Spread slider - Control layout density")
    print("     • Rotation speed - Auto-rotate nodes")
    print()
    print("  🎨 Visual features:")
    print("     • Color-coded performance (Green=Fast, Yellow=Medium, Red=Slow)")
    print("     • Node labels with function names")
    print("     • Connecting lines showing call relationships")
    print("     • Real-time statistics panel")
    print()
    print("=" * 80)
    print()
    
    # Run the traced code
    main()
    
    # Get the call graph
    graph = get_current_graph()
    
    # Export to 3D HTML
    output_file = "3d_visualization_demo.html"
    export_html_3d(graph, output_file, title="CallFlow 3D Visualization Demo")
    
    print()
    print("=" * 80)
    print("✅ 3D Visualization Generated!")
    print("=" * 80)
    print()
    print(f"📁 Output file: {output_file}")
    print()
    print("🌐 Open the HTML file in your browser to explore the 3D visualization!")
    print()
    print("💡 Tips:")
    print("  • Try different layout algorithms from the dropdown")
    print("  • Adjust the spread slider to see nodes closer or farther apart")
    print("  • Use the rotation speed slider for automatic rotation")
    print("  • Click 'Reset View' to return to default camera position")
    print("  • Drag with mouse to rotate, scroll to zoom")
    print()
    print("🎯 Use Cases:")
    print("  • Understanding complex call hierarchies in 3D space")
    print("  • Presentations and demos with impressive visuals")
    print("  • Exploring large codebases with spatial relationships")
    print("  • Educational purposes to teach program flow")
    print()
    print("=" * 80)
