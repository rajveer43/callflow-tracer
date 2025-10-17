"""
Anomaly Detection Example for CallFlow Tracer.

Demonstrates how to use statistical analysis to detect anomalies
in execution patterns proactively.

Setup:
    No LLM required! Uses statistical methods.
    pip install callflow-tracer
"""

import time
import random
from callflow_tracer import trace_scope
from callflow_tracer.ai import detect_anomalies, AnomalyDetector


# Normal application behavior
def normal_function():
    """Normal execution time."""
    time.sleep(0.01)
    return "normal"


def fast_function():
    """Fast execution."""
    time.sleep(0.001)
    return "fast"


def sometimes_slow_function():
    """Sometimes slow - ANOMALY!"""
    if random.random() > 0.7:
        time.sleep(0.5)  # Anomalous slow execution
    else:
        time.sleep(0.01)
    return "variable"


def frequently_called_function():
    """Called many times - potential ANOMALY!"""
    time.sleep(0.001)
    return "frequent"


def normal_application():
    """Normal application behavior."""
    for i in range(5):
        normal_function()
    
    for i in range(3):
        fast_function()
    
    sometimes_slow_function()


def anomalous_application():
    """Application with anomalies."""
    # Normal calls
    for i in range(5):
        normal_function()
    
    # Anomaly: Too many calls
    for i in range(50):
        frequently_called_function()
    
    # Anomaly: Slow execution
    for i in range(3):
        sometimes_slow_function()


def demo_basic_anomaly_detection():
    """Demo 1: Basic Anomaly Detection"""
    print("\n" + "="*70)
    print("DEMO 1: Basic Anomaly Detection")
    print("="*70)
    
    print("\n📊 Running application...")
    with trace_scope() as graph:
        anomalous_application()
    
    print("\n🔍 Detecting anomalies...")
    anomalies = detect_anomalies(graph)
    
    print("\n" + "-"*70)
    print("ANOMALY DETECTION RESULTS:")
    print("-"*70)
    
    severity = anomalies['severity_summary']
    print(f"\nTotal anomalies: {severity['total']}")
    print(f"  🔴 Critical: {severity['critical']}")
    print(f"  🟠 High: {severity['high']}")
    print(f"  🟡 Medium: {severity['medium']}")
    print(f"  🟢 Low: {severity['low']}")
    print(f"\nOverall severity: {severity['overall_severity'].upper()}")
    
    # Time anomalies
    if anomalies['time_anomalies']:
        print("\n" + "-"*70)
        print("⏱️  TIME ANOMALIES:")
        print("-"*70)
        for i, anomaly in enumerate(anomalies['time_anomalies'][:5], 1):
            print(f"\n{i}. {anomaly['function']}")
            print(f"   Actual: {anomaly['value']:.3f}s")
            print(f"   Expected: {anomaly['expected']:.3f}s")
            print(f"   Deviation: +{anomaly['deviation']:.3f}s")
            print(f"   Z-score: {anomaly['z_score']:.2f}")
            print(f"   Severity: {anomaly['severity']}")
    
    # Frequency anomalies
    if anomalies['frequency_anomalies']:
        print("\n" + "-"*70)
        print("📞 FREQUENCY ANOMALIES:")
        print("-"*70)
        for i, anomaly in enumerate(anomalies['frequency_anomalies'][:5], 1):
            print(f"\n{i}. {anomaly['function']}")
            print(f"   Actual calls: {anomaly['value']}")
            print(f"   Expected calls: {anomaly['expected']:.0f}")
            print(f"   Deviation: +{anomaly['deviation']:.0f}")
            print(f"   Severity: {anomaly['severity']}")
    
    # Recommendations
    print("\n" + "-"*70)
    print("💡 RECOMMENDATIONS:")
    print("-"*70)
    for rec in anomalies['recommendations']:
        print(f"  {rec}")


def demo_baseline_comparison():
    """Demo 2: Anomaly Detection with Baseline"""
    print("\n" + "="*70)
    print("DEMO 2: Baseline Comparison")
    print("="*70)
    
    # Create baseline graphs (normal behavior)
    print("\n📊 Creating baseline from normal executions...")
    baseline_graphs = []
    for i in range(5):
        with trace_scope() as graph:
            normal_application()
        baseline_graphs.append(graph)
    print(f"✓ Created baseline from {len(baseline_graphs)} executions")
    
    # Detect anomalies in new execution
    print("\n📊 Running potentially anomalous execution...")
    with trace_scope() as test_graph:
        anomalous_application()
    
    print("\n🔍 Detecting anomalies against baseline...")
    anomalies = detect_anomalies(test_graph, baseline_graphs=baseline_graphs)
    
    print(f"\nAnomalies detected: {anomalies['severity_summary']['total']}")
    print(f"Severity: {anomalies['severity_summary']['overall_severity']}")
    
    # Show anomalies with baseline deviation
    for anomaly in anomalies['time_anomalies'][:3]:
        if 'baseline_deviation' in anomaly:
            print(f"\n⚠️  {anomaly['function']}")
            print(f"   Baseline deviation: +{anomaly['baseline_deviation']:.3f}s")


def demo_sensitivity_tuning():
    """Demo 3: Sensitivity Tuning"""
    print("\n" + "="*70)
    print("DEMO 3: Sensitivity Tuning")
    print("="*70)
    
    print("\n📊 Running application...")
    with trace_scope() as graph:
        anomalous_application()
    
    # Try different sensitivity levels
    sensitivities = [1.5, 2.0, 2.5, 3.0]
    
    print("\n🔍 Testing different sensitivity levels...")
    for sensitivity in sensitivities:
        anomalies = detect_anomalies(graph, sensitivity=sensitivity)
        total = anomalies['severity_summary']['total']
        print(f"  Sensitivity {sensitivity}: {total} anomalies detected")


def demo_specific_anomaly_types():
    """Demo 4: Detect Specific Anomaly Types"""
    print("\n" + "="*70)
    print("DEMO 4: Specific Anomaly Types")
    print("="*70)
    
    print("\n📊 Running application...")
    with trace_scope() as graph:
        anomalous_application()
    
    # Detect only time anomalies
    print("\n⏱️  Time anomalies only:")
    time_anomalies = detect_anomalies(graph, detect_types=['time'])
    print(f"  Found: {len(time_anomalies['time_anomalies'])}")
    
    # Detect only frequency anomalies
    print("\n📞 Frequency anomalies only:")
    freq_anomalies = detect_anomalies(graph, detect_types=['frequency'])
    print(f"  Found: {len(freq_anomalies['frequency_anomalies'])}")
    
    # Detect only pattern anomalies
    print("\n🔄 Pattern anomalies only:")
    pattern_anomalies = detect_anomalies(graph, detect_types=['pattern'])
    print(f"  Found: {len(pattern_anomalies['pattern_anomalies'])}")


def demo_pattern_anomalies():
    """Demo 5: Pattern Anomaly Detection"""
    print("\n" + "="*70)
    print("DEMO 5: Pattern Anomaly Detection")
    print("="*70)
    
    def database_query(id):
        """Simulates database query."""
        time.sleep(0.01)
        return f"result_{id}"
    
    def n_plus_one_problem():
        """Demonstrates N+1 query pattern."""
        # Get list
        items = list(range(10))
        
        # N+1: Query for each item individually
        results = []
        for item in items:
            result = database_query(item)
            results.append(result)
        
        return results
    
    print("\n📊 Running application with N+1 pattern...")
    with trace_scope() as graph:
        n_plus_one_problem()
    
    print("\n🔍 Detecting pattern anomalies...")
    anomalies = detect_anomalies(graph, detect_types=['pattern'])
    
    if anomalies['pattern_anomalies']:
        print("\n" + "-"*70)
        print("🔥 PATTERN ANOMALIES DETECTED:")
        print("-"*70)
        for anomaly in anomalies['pattern_anomalies']:
            print(f"\n⚠️  {anomaly['subtype'].upper()}: {anomaly['function']}")
            print(f"   {anomaly['description']}")
            print(f"   Severity: {anomaly['severity']}")


def demo_outlier_detection():
    """Demo 6: Statistical Outlier Detection"""
    print("\n" + "="*70)
    print("DEMO 6: Statistical Outlier Detection")
    print("="*70)
    
    def mixed_performance():
        """Mix of normal and outlier functions."""
        # Most functions are fast
        for i in range(20):
            fast_function()
        
        # One outlier
        time.sleep(0.5)  # Outlier!
        
        # More normal functions
        for i in range(10):
            normal_function()
    
    print("\n📊 Running application with outliers...")
    with trace_scope() as graph:
        mixed_performance()
    
    print("\n🔍 Detecting statistical outliers (IQR method)...")
    anomalies = detect_anomalies(graph, detect_types=['outlier'])
    
    if anomalies['outlier_anomalies']:
        print("\n" + "-"*70)
        print("📊 STATISTICAL OUTLIERS:")
        print("-"*70)
        for anomaly in anomalies['outlier_anomalies']:
            print(f"\n⚠️  {anomaly['function']}")
            print(f"   Type: {anomaly['subtype']}")
            print(f"   Value: {anomaly['value']}")
            print(f"   Threshold: {anomaly['threshold']}")
            print(f"   {anomaly['description']}")


def demo_continuous_monitoring():
    """Demo 7: Continuous Monitoring Setup"""
    print("\n" + "="*70)
    print("DEMO 7: Continuous Monitoring")
    print("="*70)
    
    # Create detector with baseline
    detector = AnomalyDetector(sensitivity=2.0)
    
    # Build baseline
    print("\n📊 Building baseline (5 normal executions)...")
    for i in range(5):
        with trace_scope() as graph:
            normal_application()
        detector.add_baseline(graph)
    print("✓ Baseline established")
    
    # Monitor new executions
    print("\n🔍 Monitoring new executions...")
    
    for i in range(3):
        print(f"\n--- Execution {i+1} ---")
        
        with trace_scope() as graph:
            if i == 1:
                # Inject anomaly in second execution
                anomalous_application()
            else:
                normal_application()
        
        anomalies = detector.detect(graph)
        severity = anomalies['severity_summary']
        
        if severity['total'] > 0:
            print(f"⚠️  {severity['total']} anomalies detected!")
            print(f"   Severity: {severity['overall_severity']}")
        else:
            print("✓ No anomalies detected")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║          CallFlow Tracer - Anomaly Detection Demo                   ║
║                                                                      ║
║  Uses statistical analysis to detect anomalies proactively          ║
║  No LLM required!                                                   ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        demo_basic_anomaly_detection()
        demo_baseline_comparison()
        demo_sensitivity_tuning()
        demo_specific_anomaly_types()
        demo_pattern_anomalies()
        demo_outlier_detection()
        demo_continuous_monitoring()
        
        print("\n" + "="*70)
        print("✅ All demos completed!")
        print("="*70)
        print("\n⚡ Anomaly Detection Benefits:")
        print("• Proactive issue detection")
        print("• No LLM required (statistical methods)")
        print("• Baseline comparison support")
        print("• Multiple anomaly types (time, frequency, pattern, outlier)")
        print("• Configurable sensitivity")
        print("• Continuous monitoring capability")
        print("\n💡 Use Cases:")
        print("• Production monitoring")
        print("• Performance regression detection")
        print("• N+1 query detection")
        print("• Unusual behavior alerting")
        print("• CI/CD performance gates")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted")
    except Exception as e:
        print(f"\n\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
