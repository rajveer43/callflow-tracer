"""
Advanced Features Example for CallFlow Tracer

Demonstrates:
1. Anomaly detection with baseline learning
2. Auto-instrumentation for HTTP/Redis/Boto3
3. Plugin system with custom analyzers
"""

import time
import random
from callflow_tracer import (
    trace_scope,
    # Anomaly detection
    get_anomaly_detector,
    analyze_function_duration,
    generate_anomaly_report,
    export_anomaly_report,
    # Auto-instrumentation
    enable_auto_instrumentation,
    auto_instrumentation,
    # Plugin system
    get_plugin_manager,
    register_analyzer
)

# Enable auto-instrumentation for HTTP libraries
enable_auto_instrumentation(['http', 'redis', 'boto3'])

# Custom analyzer plugin
@register_analyzer("performance_analyzer", description="Analyzes performance patterns")
def performance_analyzer(graph, **kwargs):
    """Custom analyzer for performance patterns."""
    nodes = list(graph.nodes.values()) if hasattr(graph, 'nodes') else []
    
    # Calculate performance metrics
    slow_functions = [
        node for node in nodes 
        if hasattr(node, 'avg_time') and node.avg_time > 0.1
    ]
    
    fast_functions = [
        node for node in nodes 
        if hasattr(node, 'avg_time') and node.avg_time < 0.01
    ]
    
    return {
        'total_functions': len(nodes),
        'slow_functions': len(slow_functions),
        'fast_functions': len(fast_functions),
        'slowest_function': max(
            (node.full_name for node in slow_functions),
            default='N/A',
            key=lambda name: next(
                node.avg_time for node in slow_functions 
                if node.full_name == name
            ) if slow_functions else 0
        ),
        'performance_ratio': len(fast_functions) / len(nodes) if nodes else 0
    }

def simulate_normal_operation():
    """Simulate normal operation with consistent timing."""
    time.sleep(0.05)  # Normal response time
    return "normal_result"

def simulate_slow_operation():
    """Simulate slow operation (anomaly)."""
    time.sleep(0.5)  # Slow response time - should trigger anomaly
    return "slow_result"

def simulate_http_requests():
    """Simulate HTTP requests (will be auto-instrumented)."""
    try:
        import requests
        
        # Normal request
        response = requests.get('https://httpbin.org/delay/0.1', timeout=1)
        print(f"HTTP Status: {response.status_code}")
        
        # Slow request (anomaly)
        response = requests.get('https://httpbin.org/delay/0.5', timeout=2)
        print(f"HTTP Status: {response.status_code}")
        
    except ImportError:
        print("requests not installed, skipping HTTP demo")
    except Exception as e:
        print(f"HTTP request failed: {e}")

def simulate_redis_operations():
    """Simulate Redis operations (will be auto-instrumented)."""
    try:
        import redis
        
        # Connect to Redis (if available)
        r = redis.Redis(host='localhost', port=6379, db=0)
        
        # Normal operations
        r.set('test_key', 'test_value')
        value = r.get('test_key')
        print(f"Redis Value: {value}")
        
        # Simulate some operations
        for i in range(5):
            r.set(f'key_{i}', f'value_{i}')
            r.get(f'key_{i}')
            
    except ImportError:
        print("redis not installed, skipping Redis demo")
    except Exception as e:
        print(f"Redis operation failed: {e}")

def simulate_boto3_operations():
    """Simulate AWS Boto3 operations (will be auto-instrumented)."""
    try:
        import boto3
        
        # Create S3 client (will be instrumented)
        s3 = boto3.client('s3')
        
        # List buckets (instrumented)
        try:
            buckets = s3.list_buckets()
            print(f"S3 Buckets: {len(buckets.get('Buckets', []))}")
        except Exception:
            print("S3 access not configured (expected)")
            
    except ImportError:
        print("boto3 not installed, skipping AWS demo")
    except Exception as e:
        print(f"Boto3 operation failed: {e}")

def main():
    """Main function demonstrating advanced features."""
    print("=== CallFlow Tracer Advanced Features Demo ===\n")
    
    # Get the global anomaly detector
    detector = get_anomaly_detector()
    
    print("1. Building baseline with normal operations...")
    
    # Build baseline with normal operations
    with trace_scope("baseline_trace.html"):
        for i in range(10):
            # Normal operations
            result = simulate_normal_operation()
            
            # Simulate some metrics
            analyze_function_duration("simulate_normal_operation", 0.05)
            
            # Add some variation
            time.sleep(random.uniform(0.04, 0.06))
    
    print("2. Running operations with anomalies...")
    
    # Run operations with anomalies
    with trace_scope("anomaly_trace.html"):
        for i in range(5):
            # Normal operations
            result = simulate_normal_operation()
            analyze_function_duration("simulate_normal_operation", 0.05)
            
            # Introduce anomalies
            if i % 2 == 0:
                result = simulate_slow_operation()
                analyze_function_duration("simulate_slow_operation", 0.5)  # Anomaly!
        
        # Auto-instrumented operations
        print("\n3. Testing auto-instrumentation...")
        simulate_http_requests()
        simulate_redis_operations()
        simulate_boto3_operations()
    
    print("\n4. Generating anomaly detection report...")
    
    # Generate anomaly report
    report = generate_anomaly_report(hours=1)
    
    print(f"\n=== Anomaly Detection Results ===")
    print(f"Total Alerts: {report['total_alerts']}")
    print(f"Severity Breakdown:")
    for severity, count in report['severity_breakdown'].items():
        print(f"  {severity}: {count}")
    
    # Show top anomalies
    if report['top_anomalies']:
        print(f"\nTop Anomalies:")
        for alert in report['top_anomalies'][:3]:
            print(f"  - {alert['metric_name']}: {alert['description']}")
    
    # Export anomaly report
    export_anomaly_report("anomaly_report.json", hours=1)
    print("\nAnomaly report exported to: anomaly_report.json")
    
    print("\n5. Testing plugin system...")
    
    # Get plugin manager and run custom analyzer
    manager = get_plugin_manager()
    
    # Get current graph for analysis
    from callflow_tracer import get_current_graph
    current_graph = get_current_graph()
    
    if current_graph:
        # Run custom analyzer
        result = manager.run_analyzer("performance_analyzer", current_graph)
        
        print(f"\n=== Custom Analyzer Results ===")
        print(f"Total Functions: {result.get('total_functions', 0)}")
        print(f"Slow Functions: {result.get('slow_functions', 0)}")
        print(f"Fast Functions: {result.get('fast_functions', 0)}")
        print(f"Performance Ratio: {result.get('performance_ratio', 0):.2%}")
        
        if result.get('slowest_function'):
            print(f"Slowest Function: {result['slowest_function']}")
    
    # Show available plugins
    print(f"\n=== Available Plugins ===")
    print(f"Analyzers: {manager.list_analyzers()}")
    print(f"Exporters: {manager.list_exporters()}")
    print(f"UI Widgets: {manager.list_ui_widgets()}")
    
    # Export plugin configuration
    manager.export_plugin_config("plugin_config.json")
    print("\nPlugin configuration exported to: plugin_config.json")
    
    print("\n=== Demo Complete ===")
    print("Generated files:")
    print("  - baseline_trace.html")
    print("  - anomaly_trace.html")
    print("  - anomaly_report.json")
    print("  - plugin_config.json")

if __name__ == "__main__":
    main()
