"""
Example: Custom Metrics Tracking

This example demonstrates how to use CallFlow Tracer's custom metrics feature
to track business logic, monitor SLAs, and export metrics.

Features demonstrated:
1. @custom_metric decorator for automatic tracking
2. Manual metric tracking with track_metric()
3. SLA monitoring and compliance reporting
4. Business metrics tracking (counters and gauges)
5. Metrics export to JSON and CSV
"""


import time
import random
import os
import sys

CURRENT_DIR = os.path.dirname(__file__)
REPO_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from callflow_tracer import (
    custom_metric,
    track_metric,
    MetricsCollector,
    SLAMonitor,
    get_business_tracker,
    trace_scope
)
# Example 1: Using @custom_metric decorator
@custom_metric("order_processing_time", sla_threshold=1.0, tags={"service": "orders"})
def process_order(order_id: int, amount: float) -> dict:
    """Process an order and track the time taken."""
    # Simulate processing
    processing_time = random.uniform(0.5, 1.5)
    time.sleep(processing_time)
    
    return {
        "order_id": order_id,
        "amount": amount,
        "status": "completed",
        "processing_time": processing_time
    }


@custom_metric("payment_processing_time", sla_threshold=0.5)
def process_payment(order_id: int, amount: float) -> bool:
    """Process payment for an order."""
    payment_time = random.uniform(0.2, 0.8)
    time.sleep(payment_time)
    return True


@custom_metric("inventory_update_time", sla_threshold=0.3)
def update_inventory(product_id: int, quantity: int) -> bool:
    """Update inventory for a product."""
    update_time = random.uniform(0.1, 0.5)
    time.sleep(update_time)
    return True


# Example 2: Manual metric tracking
def calculate_order_total(items: list) -> float:
    """Calculate order total with manual metric tracking."""
    total = sum(item['price'] * item['quantity'] for item in items)
    
    # Track custom metrics
    track_metric(
        "order_item_count",
        len(items),
        tags={"order_type": "standard"},
        metadata={"total_amount": total}
    )
    
    track_metric(
        "order_total_amount",
        total,
        tags={"currency": "USD"},
        metadata={"item_count": len(items)}
    )
    
    return total


# Example 3: Business metrics tracking
def process_batch_orders(orders: list) -> dict:
    """Process a batch of orders and track business metrics."""
    tracker = get_business_tracker()
    
    successful_orders = 0
    failed_orders = 0
    total_revenue = 0
    
    for order in orders:
        try:
            result = process_order(order['id'], order['amount'])
            successful_orders += 1
            total_revenue += order['amount']
            tracker.increment_counter("orders_processed")
        except Exception as e:
            failed_orders += 1
            tracker.increment_counter("orders_failed")
    
    # Set gauge for current metrics
    tracker.set_gauge("total_revenue", total_revenue)
    tracker.set_gauge("success_rate", (successful_orders / len(orders) * 100) if orders else 0)
    
    return {
        "total": len(orders),
        "successful": successful_orders,
        "failed": failed_orders,
        "revenue": total_revenue
    }


# Example 4: SLA Monitoring
def setup_sla_monitoring():
    """Setup SLA thresholds and monitoring."""
    sla_monitor = SLAMonitor()
    
    # Set SLA thresholds
    sla_monitor.set_threshold("order_processing_time", 1.0)  # 1 second
    sla_monitor.set_threshold("payment_processing_time", 0.5)  # 500ms
    sla_monitor.set_threshold("inventory_update_time", 0.3)  # 300ms
    
    return sla_monitor


def main():
    """Main example demonstrating custom metrics."""
    print("=" * 60)
    print("CallFlow Tracer - Custom Metrics Example")
    print("=" * 60)
    
    # Setup SLA monitoring
    sla_monitor = setup_sla_monitoring()
    
    # Trace the entire workflow
    with trace_scope("custom_metrics_trace.html"):
        print("\n1. Processing individual orders...")
        for i in range(5):
            order = {
                'id': i + 1,
                'amount': random.uniform(50, 500)
            }
            result = process_order(order['id'], order['amount'])
            print(f"   Order {result['order_id']}: ${result['amount']:.2f} - {result['status']}")
        
        print("\n2. Processing payments...")
        for i in range(5):
            process_payment(i + 1, random.uniform(50, 500))
        
        print("\n3. Updating inventory...")
        for i in range(3):
            update_inventory(i + 1, random.randint(1, 100))
        
        print("\n4. Processing batch orders...")
        orders = [
            {'id': i, 'amount': random.uniform(50, 500)}
            for i in range(10)
        ]
        batch_result = process_batch_orders(orders)
        print(f"   Batch Result: {batch_result}")
        
        print("\n5. Calculating order totals...")
        items = [
            {'price': 10.0, 'quantity': 2},
            {'price': 25.0, 'quantity': 1},
            {'price': 15.0, 'quantity': 3}
        ]
        total = calculate_order_total(items)
        print(f"   Order Total: ${total:.2f}")
    
    # Get and display metrics
    print("\n" + "=" * 60)
    print("METRICS SUMMARY")
    print("=" * 60)
    
    # Display individual metric statistics
    print("\nMetric Statistics:")
    all_stats = MetricsCollector.get_all_stats()
    for metric_name, stats in all_stats.items():
        print(f"\n  {metric_name}:")
        print(f"    Count: {stats['count']}")
        print(f"    Mean: {stats['mean']:.4f}")
        print(f"    Min: {stats['min']:.4f}")
        print(f"    Max: {stats['max']:.4f}")
        print(f"    Median: {stats['median']:.4f}")
        print(f"    StdDev: {stats['stddev']:.4f}")
    
    # Display SLA compliance report
    print("\n" + "-" * 60)
    print("SLA Compliance Report:")
    print("-" * 60)
    compliance_report = sla_monitor.get_compliance_report()
    for metric_name, compliance in compliance_report.items():
        print(f"\n  {metric_name}:")
        print(f"    Threshold: {compliance['threshold']}s")
        print(f"    Total Calls: {compliance['total_calls']}")
        print(f"    Violations: {compliance['violations']}")
        print(f"    Compliance Rate: {compliance['compliance_rate']}%")
        print(f"    Status: {compliance['status']}")
    
    # Display business metrics
    print("\n" + "-" * 60)
    print("Business Metrics:")
    print("-" * 60)
    tracker = get_business_tracker()
    print("\n  Counters:")
    for counter_name, value in tracker.get_counters().items():
        print(f"    {counter_name}: {value}")
    
    print("\n  Gauges:")
    for gauge_name, value in tracker.get_gauges().items():
        print(f"    {gauge_name}: {value:.2f}")
    
    # Export metrics
    print("\n" + "=" * 60)
    print("Exporting Metrics...")
    print("=" * 60)
    
    MetricsCollector.export_metrics("metrics_report.json", format="json")
    print("✓ Exported metrics to: metrics_report.json")
    
    MetricsCollector.export_metrics("metrics_report.csv", format="csv")
    print("✓ Exported metrics to: metrics_report.csv")
    
    sla_monitor.export_report("sla_compliance_report.json")
    print("✓ Exported SLA report to: sla_compliance_report.json")
    
    tracker.export_metrics("business_metrics.json")
    print("✓ Exported business metrics to: business_metrics.json")
    
    print("\n✓ Trace exported to: custom_metrics_trace.html")
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
