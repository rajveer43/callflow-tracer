# Custom Metrics Guide

## Overview

CallFlow Tracer's Custom Metrics feature allows you to track business logic metrics, monitor SLA compliance, and export performance data. This guide covers all aspects of custom metrics tracking.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Decorator-Based Tracking](#decorator-based-tracking)
3. [Manual Metric Tracking](#manual-metric-tracking)
4. [SLA Monitoring](#sla-monitoring)
5. [Business Metrics Tracking](#business-metrics-tracking)
6. [Metrics Export](#metrics-export)
7. [Advanced Usage](#advanced-usage)
8. [API Reference](#api-reference)

## Quick Start

### Basic Usage

```python
from callflow_tracer import custom_metric, track_metric

# Using decorator
@custom_metric("orders_processed")
def process_order(order):
    # Metric automatically tracked
    return order.process()

# Manual tracking
track_metric("api_response_time", 0.234)

# Run your code
process_order(order)

# Export metrics
from callflow_tracer import MetricsCollector
MetricsCollector.export_metrics("metrics.json")
```

## Decorator-Based Tracking

The `@custom_metric` decorator automatically tracks function execution time and records it as a metric.

### Basic Decorator

```python
from callflow_tracer import custom_metric

@custom_metric("function_execution_time")
def my_function():
    # Do work
    pass

my_function()  # Execution time is automatically tracked
```

### Decorator with SLA Threshold

```python
@custom_metric("api_call_time", sla_threshold=0.5)
def call_api(endpoint):
    # SLA: API calls should complete within 500ms
    response = requests.get(endpoint)
    return response

call_api("/api/users")  # Tracked and checked against SLA
```

### Decorator with Tags

```python
@custom_metric("database_query_time", tags={"database": "postgres", "environment": "production"})
def query_database(sql):
    # Execute query
    pass

query_database("SELECT * FROM users")  # Tagged for filtering
```

### Decorator with All Options

```python
@custom_metric(
    metric_name="payment_processing",
    sla_threshold=1.0,
    tags={"service": "payments", "region": "us-east-1"}
)
def process_payment(amount):
    # Process payment
    pass
```

## Manual Metric Tracking

For more control, use `track_metric()` to manually record metric values.

### Basic Manual Tracking

```python
from callflow_tracer import track_metric

# Track a single value
track_metric("items_processed", 42)
track_metric("response_time_ms", 234.5)
```

### Tracking with Tags

```python
track_metric(
    "api_request_count",
    1,
    tags={
        "endpoint": "/api/users",
        "method": "GET",
        "status": "200"
    }
)
```

### Tracking with Metadata

```python
track_metric(
    "order_total",
    99.99,
    tags={"currency": "USD"},
    metadata={
        "order_id": "ORD-12345",
        "customer_id": "CUST-789",
        "item_count": 5
    }
)
```

## SLA Monitoring

Monitor Service Level Agreement compliance for your metrics.

### Setup SLA Thresholds

```python
from callflow_tracer import SLAMonitor

sla_monitor = SLAMonitor()

# Set SLA thresholds (in seconds for time metrics)
sla_monitor.set_threshold("api_response_time", 0.5)  # 500ms
sla_monitor.set_threshold("database_query_time", 1.0)  # 1 second
sla_monitor.set_threshold("payment_processing", 2.0)  # 2 seconds
```

### Get Compliance Report

```python
# Get SLA compliance report
report = sla_monitor.get_compliance_report()

for metric_name, compliance in report.items():
    print(f"{metric_name}:")
    print(f"  Threshold: {compliance['threshold']}s")
    print(f"  Total Calls: {compliance['total_calls']}")
    print(f"  Violations: {compliance['violations']}")
    print(f"  Compliance Rate: {compliance['compliance_rate']}%")
    print(f"  Status: {compliance['status']}")
```

### Export Compliance Report

```python
# Export SLA compliance report to JSON
sla_monitor.export_report("sla_report.json")
```

### Example Output

```json
{
  "api_response_time": {
    "threshold": 0.5,
    "total_calls": 100,
    "violations": 5,
    "compliance_rate": 95.0,
    "mean_value": 0.45,
    "max_value": 0.78,
    "status": "PASS"
  },
  "database_query_time": {
    "threshold": 1.0,
    "total_calls": 50,
    "violations": 2,
    "compliance_rate": 96.0,
    "mean_value": 0.82,
    "max_value": 1.23,
    "status": "PASS"
  }
}
```

## Business Metrics Tracking

Track business-specific metrics like counters and gauges.

### Using BusinessMetricsTracker

```python
from callflow_tracer import get_business_tracker

tracker = get_business_tracker()

# Increment counters
tracker.increment_counter("orders_processed")
tracker.increment_counter("orders_processed", 5)  # Increment by 5
tracker.increment_counter("orders_failed")

# Set gauge values
tracker.set_gauge("current_queue_size", 42)
tracker.set_gauge("success_rate", 98.5)
tracker.set_gauge("average_response_time", 0.234)
```

### Get Current Values

```python
# Get all counter values
counters = tracker.get_counters()
print(f"Orders Processed: {counters.get('orders_processed', 0)}")

# Get all gauge values
gauges = tracker.get_gauges()
print(f"Success Rate: {gauges.get('success_rate', 0)}%")
```

### Export Business Metrics

```python
tracker.export_metrics("business_metrics.json")
```

### Example Output

```json
{
  "counters": {
    "orders_processed": 1250,
    "orders_failed": 12,
    "api_calls": 5430
  },
  "gauges": {
    "current_queue_size": 42,
    "success_rate": 98.4,
    "average_response_time": 0.234
  },
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

## Metrics Export

### Export to JSON

```python
from callflow_tracer import MetricsCollector

# Export all metrics to JSON
MetricsCollector.export_metrics("metrics.json", format="json")
```

### Export to CSV

```python
# Export all metrics to CSV
MetricsCollector.export_metrics("metrics.csv", format="csv")
```

### JSON Export Structure

```json
{
  "metrics": {
    "api_response_time": [
      {
        "name": "api_response_time",
        "value": 0.234,
        "timestamp": 1705318245.123,
        "datetime": "2024-01-15T10:30:45.123456",
        "tags": {"endpoint": "/api/users"},
        "metadata": {"function": "call_api", "module": "api"}
      }
    ]
  },
  "statistics": {
    "api_response_time": {
      "name": "api_response_time",
      "count": 100,
      "total": 23.45,
      "min": 0.1,
      "max": 0.8,
      "mean": 0.2345,
      "median": 0.22,
      "stddev": 0.15
    }
  },
  "sla_violations": {
    "api_response_time": [0.78, 0.82, 0.91]
  },
  "export_timestamp": "2024-01-15T10:30:45.123456"
}
```

### CSV Export Format

```csv
Metric,Value,Timestamp,Tags,Metadata
api_response_time,0.234,2024-01-15T10:30:45.123456,"{""endpoint"": ""/api/users""}","{""function"": ""call_api""}"
api_response_time,0.198,2024-01-15T10:30:46.234567,"{""endpoint"": ""/api/users""}","{""function"": ""call_api""}"
```

## Advanced Usage

### Filtering Metrics by Tag

```python
from callflow_tracer import MetricsCollector

# Get metrics filtered by tag
api_metrics = MetricsCollector.get_metric_by_tag("endpoint", "/api/users")

for metric in api_metrics:
    print(f"Value: {metric.value}, Time: {metric.timestamp}")
```

### Getting Metric Statistics

```python
# Get statistics for a specific metric
stats = MetricsCollector.get_metric_stats("api_response_time")

if stats:
    print(f"Count: {stats.count}")
    print(f"Mean: {stats.mean}")
    print(f"Median: {stats.median}")
    print(f"Min: {stats.min}")
    print(f"Max: {stats.max}")
    print(f"StdDev: {stats.stddev}")
```

### Getting All Statistics

```python
# Get statistics for all metrics
all_stats = MetricsCollector.get_all_stats()

for metric_name, stats in all_stats.items():
    print(f"{metric_name}: mean={stats['mean']}, max={stats['max']}")
```

### Getting SLA Violations

```python
# Get all SLA violations
violations = MetricsCollector.get_sla_violations()

for metric_name, violation_values in violations.items():
    print(f"{metric_name}: {len(violation_values)} violations")
    print(f"  Values: {violation_values}")
```

### Clearing Metrics

```python
# Clear all recorded metrics
MetricsCollector.clear_metrics()
```

## Integration with Tracing

Combine custom metrics with call tracing:

```python
from callflow_tracer import trace_scope, custom_metric

@custom_metric("process_order_time", sla_threshold=2.0)
def process_order(order):
    # Process order
    return order.process()

# Trace the entire workflow
with trace_scope("order_processing.html"):
    for order in orders:
        process_order(order)

# Export both trace and metrics
MetricsCollector.export_metrics("metrics.json")
```

## Real-World Example

```python
from callflow_tracer import (
    custom_metric,
    track_metric,
    MetricsCollector,
    SLAMonitor,
    get_business_tracker,
    trace_scope
)
import time

# Setup SLA monitoring
sla_monitor = SLAMonitor()
sla_monitor.set_threshold("api_response_time", 0.5)
sla_monitor.set_threshold("database_query_time", 1.0)

# Get business tracker
tracker = get_business_tracker()

@custom_metric("api_response_time", sla_threshold=0.5, tags={"service": "api"})
def call_api(endpoint):
    time.sleep(0.3)  # Simulate API call
    return {"status": "success"}

@custom_metric("database_query_time", sla_threshold=1.0, tags={"service": "database"})
def query_database(query):
    time.sleep(0.5)  # Simulate database query
    return [{"id": 1, "name": "User 1"}]

def process_request(request_id):
    try:
        # Call API
        api_result = call_api("/api/users")
        
        # Query database
        db_result = query_database("SELECT * FROM users")
        
        # Track business metrics
        tracker.increment_counter("requests_processed")
        track_metric("request_success", 1, tags={"request_id": str(request_id)})
        
        return {"success": True, "data": db_result}
    except Exception as e:
        tracker.increment_counter("requests_failed")
        track_metric("request_error", 1, tags={"request_id": str(request_id)})
        raise

# Run with tracing
with trace_scope("request_processing.html"):
    for i in range(10):
        try:
            process_request(i)
        except Exception as e:
            print(f"Error processing request {i}: {e}")

# Export all data
print("\n=== Metrics Summary ===")
stats = MetricsCollector.get_all_stats()
for metric_name, stat in stats.items():
    print(f"{metric_name}: mean={stat['mean']:.4f}, max={stat['max']:.4f}")

print("\n=== SLA Compliance ===")
compliance = sla_monitor.get_compliance_report()
for metric_name, comp in compliance.items():
    print(f"{metric_name}: {comp['compliance_rate']}% compliant")

print("\n=== Business Metrics ===")
print(f"Requests Processed: {tracker.get_counters().get('requests_processed', 0)}")
print(f"Requests Failed: {tracker.get_counters().get('requests_failed', 0)}")

# Export reports
MetricsCollector.export_metrics("metrics.json")
sla_monitor.export_report("sla_report.json")
tracker.export_metrics("business_metrics.json")
```

## API Reference

### custom_metric(metric_name, sla_threshold=None, tags=None)

Decorator for automatic metric tracking.

**Parameters:**
- `metric_name` (str): Name of the metric
- `sla_threshold` (float, optional): SLA threshold value
- `tags` (dict, optional): Tags for filtering

**Returns:** Decorated function

### track_metric(metric_name, value, tags=None, metadata=None)

Manually record a metric value.

**Parameters:**
- `metric_name` (str): Name of the metric
- `value` (float): Metric value
- `tags` (dict, optional): Tags for filtering
- `metadata` (dict, optional): Additional metadata

### MetricsCollector

Global metrics collector class.

**Methods:**
- `record_metric(name, value, tags=None, metadata=None)`: Record a metric
- `set_sla_threshold(metric_name, threshold)`: Set SLA threshold
- `get_metrics()`: Get all metrics
- `get_metric_stats(metric_name)`: Get statistics for a metric
- `get_all_stats()`: Get statistics for all metrics
- `get_sla_violations()`: Get SLA violations
- `export_metrics(output_file, format='json')`: Export metrics
- `clear_metrics()`: Clear all metrics

### SLAMonitor

Monitor SLA compliance.

**Methods:**
- `set_threshold(metric_name, threshold)`: Set SLA threshold
- `get_compliance_report()`: Get compliance report
- `export_report(output_file)`: Export compliance report

### BusinessMetricsTracker

Track business-specific metrics.

**Methods:**
- `increment_counter(counter_name, amount=1)`: Increment counter
- `set_gauge(gauge_name, value)`: Set gauge value
- `get_counters()`: Get all counter values
- `get_gauges()`: Get all gauge values
- `export_metrics(output_file)`: Export metrics

## Best Practices

1. **Use Meaningful Names**: Choose clear, descriptive metric names
2. **Set SLA Thresholds**: Define realistic SLA thresholds for critical metrics
3. **Use Tags**: Add tags for filtering and analysis
4. **Export Regularly**: Export metrics periodically for analysis
5. **Monitor Compliance**: Review SLA compliance reports regularly
6. **Clean Up**: Clear metrics when starting new analysis sessions
7. **Combine with Tracing**: Use metrics alongside call tracing for complete visibility

## Troubleshooting

### Metrics Not Being Recorded

- Ensure the decorator or `track_metric()` is being called
- Check that the function/code path is being executed
- Verify metric names are correct

### SLA Violations Not Detected

- Ensure `sla_threshold` is set correctly
- Check that metric values exceed the threshold
- Verify the metric is being tracked

### Export Failing

- Ensure output directory exists or is writable
- Check file permissions
- Verify output file path is valid

## See Also

- [Main Documentation](./README.md)
- [Tracing Guide](./TRACING_GUIDE.md)
- [Performance Analysis](./PERFORMANCE_ANALYSIS.md)
