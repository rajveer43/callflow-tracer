"""
Example: OpenTelemetry Export with CallFlow Tracer

This example demonstrates:
1. Basic trace capture
2. Custom metrics tracking
3. Advanced OTel export with exemplars
4. Sampling and resource attributes
"""

import time
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from callflow_tracer import (
    trace_scope,
    custom_metric,
    MetricsCollector,
    export_html,
)
from callflow_tracer.opentelemetry_exporter import (
    export_callgraph_to_otel,
    export_callgraph_with_metrics,
    CallFlowExemplar,
)
from callflow_tracer.otel_config import OTelConfig


# Example 1: Simple functions with custom metrics
@custom_metric("fibonacci", sla_threshold=0.1)
def fibonacci(n):
    """Calculate fibonacci number (with SLA monitoring)."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


@custom_metric("process_data", sla_threshold=0.05)
def process_data(items):
    """Process a list of items."""
    results = []
    for item in items:
        time.sleep(0.01)  # Simulate work
        results.append(item * 2)
    return results


@custom_metric("fetch_user", sla_threshold=0.2)
def fetch_user(user_id):
    """Fetch user from database (simulated)."""
    time.sleep(0.05)  # Simulate DB call
    return {"id": user_id, "name": f"User {user_id}"}


def main():
    """Main function to demonstrate OTel export."""
    print("=" * 60)
    print("CallFlow Tracer - OpenTelemetry Export Example")
    print("=" * 60)

    # Step 1: Capture trace with custom metrics
    print("\n[1] Capturing trace with custom metrics...")
    with trace_scope("trace_output.json") as graph:
        # Call functions to generate trace
        fib_result = fibonacci(5)
        print(f"   Fibonacci(5) = {fib_result}")

        data = process_data([1, 2, 3, 4, 5])
        print(f"   Processed data: {data}")

        user = fetch_user(123)
        print(f"   Fetched user: {user}")

    print("   ✓ Trace captured to trace_output.json")

    # Step 2: Get custom metrics
    print("\n[2] Collecting custom metrics...")
    metrics = MetricsCollector.get_metrics()
    print(f"   ✓ Collected {len(metrics)} metrics")
    for metric_name, metric_data in metrics.items():
        if isinstance(metric_data, dict):
            print(f"     - {metric_name}: {metric_data.get('value', 'N/A')}")

    # Step 3: Basic OTel export
    print("\n[3] Exporting to OpenTelemetry (basic)...")
    try:
        result = export_callgraph_to_otel(
            graph,
            service_name="example-service",
            environment="development"
        )
        print(f"   ✓ Export successful!")
        print(f"     - Spans exported: {result['span_count']}")
        print(f"     - Service: {result['service_name']}")
        print(f"     - Environment: {result['environment']}")
    except Exception as e:
        print(f"   ✗ Export failed: {e}")
        print("   (Install opentelemetry-sdk to enable OTel export)")

    # Step 4: Advanced OTel export with exemplars
    print("\n[4] Exporting with exemplars (advanced)...")
    try:
        # Create exemplars from metrics
        exemplars = []
        for metric_name, metric_data in metrics.items():
            if isinstance(metric_data, dict) and "value" in metric_data:
                exemplar = CallFlowExemplar(
                    trace_id="example-trace-001",
                    span_id="example-span-001",
                    value=metric_data.get("value", 0),
                    metric_name=metric_name,
                    attributes=metric_data.get("tags", {})
                )
                exemplars.append(exemplar)

        result = export_callgraph_to_otel(
            graph,
            service_name="example-service",
            environment="development",
            exemplars=exemplars,
            sampling_rate=1.0,
            resource_attributes={
                "service.version": "1.0.0",
                "deployment.environment": "development",
            }
        )
        print(f"   ✓ Export with exemplars successful!")
        print(f"     - Spans exported: {result['span_count']}")
        print(f"     - Exemplars linked: {result['exemplar_count']}")
    except Exception as e:
        print(f"   ✗ Export failed: {e}")

    # Step 5: Export with metrics bridging
    print("\n[5] Exporting with metrics bridging...")
    try:
        result = export_callgraph_with_metrics(
            graph,
            metrics,
            service_name="example-service",
            resource_attributes={"service.version": "1.0.0"}
        )
        print(f"   ✓ Metrics bridging successful!")
        print(f"     - Spans exported: {result['span_count']}")
        print(f"     - Exemplars linked: {result['exemplar_count']}")
    except Exception as e:
        print(f"   ✗ Export failed: {e}")

    # Step 6: Export with sampling
    print("\n[6] Exporting with sampling (0.5)...")
    try:
        result = export_callgraph_to_otel(
            graph,
            service_name="example-service",
            environment="development",
            sampling_rate=0.5  # Only export functions called >= 2 times
        )
        print(f"   ✓ Sampling export successful!")
        print(f"     - Spans exported (sampled): {result['span_count']}")
    except Exception as e:
        print(f"   ✗ Export failed: {e}")

    # Step 7: Load and use OTel config
    print("\n[7] Using OTel configuration...")
    try:
        config = OTelConfig()
        config.load_from_env()
        print(f"   ✓ Config loaded!")
        print(f"     - Service name: {config.get('service_name')}")
        print(f"     - Environment: {config.get('environment')}")
        print(f"     - Exporter type: {config.get('exporter.type')}")
    except Exception as e:
        print(f"   ✗ Config load failed: {e}")

    # Step 8: Export HTML visualization
    print("\n[8] Exporting HTML visualization...")
    try:
        export_html(graph, "trace_visualization.html", title="CallFlow Trace")
        print(f"   ✓ HTML visualization exported to trace_visualization.html")
    except Exception as e:
        print(f"   ✗ HTML export failed: {e}")

    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Review trace_output.json for captured trace data")
    print("2. Open trace_visualization.html in a browser")
    print("3. Run CLI commands:")
    print("   - callflow-tracer otel trace_output.json --init-config")
    print("   - callflow-tracer otel trace_output.json --service-name example")
    print("4. Check docs/OTEL_ADVANCED_GUIDE.md for more examples")
    print()


if __name__ == "__main__":
    main()
