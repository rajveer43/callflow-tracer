"""
Advanced Debugging Example - Root Cause Analysis + Anomaly Detection

Demonstrates the power of combining both features for comprehensive debugging.

Setup:
    pip install openai  # optional, for enhanced root cause analysis
    export OPENAI_API_KEY="your-key"  # optional
"""

import time
import random
from callflow_tracer import trace_scope
from callflow_tracer.ai import analyze_root_cause, detect_anomalies


# Simulated e-commerce application with issues
def database_get_user(user_id):
    """Get user from database - SLOW!"""
    time.sleep(0.15)  # Slow database query
    return {"id": user_id, "name": f"User{user_id}"}


def database_get_orders(user_id):
    """Get user orders - called multiple times (N+1 pattern)"""
    time.sleep(0.05)
    return [{"id": i, "total": 100} for i in range(3)]


def calculate_discount(order):
    """Calculate discount - CPU intensive."""
    time.sleep(0.02)
    return order["total"] * 0.1


def process_user_orders(user_id):
    """Process orders for a user."""
    user = database_get_user(user_id)
    orders = database_get_orders(user_id)
    
    total_discount = 0
    for order in orders:
        discount = calculate_discount(order)
        total_discount += discount
    
    return {
        "user": user,
        "orders": len(orders),
        "discount": total_discount
    }


def generate_user_report(user_ids):
    """Generate report for multiple users - N+1 PROBLEM!"""
    results = []
    for user_id in user_ids:
        result = process_user_orders(user_id)
        results.append(result)
    return results


def checkout_workflow():
    """Main checkout workflow."""
    print("Processing checkout...")
    user_ids = [1, 2, 3, 4, 5]
    report = generate_user_report(user_ids)
    print(f"Processed {len(report)} users")
    return report


def demo_combined_analysis():
    """Demo 1: Combined Root Cause + Anomaly Detection"""
    print("\n" + "="*70)
    print("DEMO 1: Combined Analysis - The Full Picture")
    print("="*70)
    
    print("\n📊 Running e-commerce checkout workflow...")
    with trace_scope() as graph:
        checkout_workflow()
    
    # Step 1: Detect anomalies
    print("\n🔍 Step 1: Detecting anomalies...")
    anomalies = detect_anomalies(graph)
    
    print("\n" + "-"*70)
    print("ANOMALY DETECTION:")
    print("-"*70)
    severity = anomalies['severity_summary']
    print(f"Total anomalies: {severity['total']}")
    print(f"Overall severity: {severity['overall_severity'].upper()}")
    
    if anomalies['pattern_anomalies']:
        print("\n🔥 Pattern anomalies detected:")
        for anomaly in anomalies['pattern_anomalies']:
            print(f"  • {anomaly['subtype']}: {anomaly['description']}")
    
    # Step 2: Root cause analysis
    print("\n🔍 Step 2: Analyzing root causes...")
    root_analysis = analyze_root_cause(graph, issue_type='performance')
    
    print("\n" + "-"*70)
    print("ROOT CAUSE ANALYSIS:")
    print("-"*70)
    print(f"Root causes identified: {root_analysis['total_root_causes']}")
    
    for i, root in enumerate(root_analysis['root_causes'][:3], 1):
        print(f"\n{i}. {root['function']}")
        print(f"   Impact: {root['total_impact_time']:.3f}s affecting {root['affected_nodes']} nodes")
        print(f"   Confidence: {root['confidence']:.0%}")
    
    # Step 3: Combined insights
    print("\n" + "-"*70)
    print("COMBINED INSIGHTS:")
    print("-"*70)
    
    print("\n🎯 Key Findings:")
    print(f"  1. {severity['total']} anomalies detected")
    print(f"  2. {root_analysis['total_root_causes']} root causes identified")
    print(f"  3. Total impact: {root_analysis['impact_analysis']['total_time_impact']:.3f}s")
    
    print("\n💡 Recommendations:")
    for rec in anomalies['recommendations'][:3]:
        print(f"  {rec}")


def demo_debugging_workflow():
    """Demo 2: Step-by-Step Debugging Workflow"""
    print("\n" + "="*70)
    print("DEMO 2: Step-by-Step Debugging Workflow")
    print("="*70)
    
    print("\n📊 Running application...")
    with trace_scope() as graph:
        checkout_workflow()
    
    # Step 1: Quick anomaly scan
    print("\n🔍 Step 1: Quick Anomaly Scan")
    print("-" * 40)
    anomalies = detect_anomalies(graph, detect_types=['time', 'frequency'])
    
    if anomalies['time_anomalies']:
        print(f"⚠️  Found {len(anomalies['time_anomalies'])} time anomalies")
        top = anomalies['time_anomalies'][0]
        print(f"   Slowest: {top['function']} ({top['value']:.3f}s)")
    
    if anomalies['frequency_anomalies']:
        print(f"⚠️  Found {len(anomalies['frequency_anomalies'])} frequency anomalies")
        top = anomalies['frequency_anomalies'][0]
        print(f"   Most called: {top['function']} ({top['value']} times)")
    
    # Step 2: Pattern analysis
    print("\n🔍 Step 2: Pattern Analysis")
    print("-" * 40)
    patterns = detect_anomalies(graph, detect_types=['pattern'])
    
    if patterns['pattern_anomalies']:
        print(f"🔥 Found {len(patterns['pattern_anomalies'])} pattern issues:")
        for pattern in patterns['pattern_anomalies']:
            print(f"   • {pattern['subtype']}: {pattern['function']}")
    
    # Step 3: Root cause tracing
    print("\n🔍 Step 3: Root Cause Tracing")
    print("-" * 40)
    root_analysis = analyze_root_cause(graph, issue_type='performance', threshold=0.1)
    
    if root_analysis['root_causes']:
        print(f"📍 Traced to {root_analysis['total_root_causes']} root causes:")
        for root in root_analysis['root_causes'][:2]:
            print(f"   • {root['function']}: {root['total_time']:.3f}s")
    
    # Step 4: Action plan
    print("\n🔍 Step 4: Action Plan")
    print("-" * 40)
    print("Based on analysis:")
    print("  1. Fix N+1 query pattern in generate_user_report()")
    print("  2. Optimize database_get_user() - add caching")
    print("  3. Batch database_get_orders() calls")


def demo_before_after_comparison():
    """Demo 3: Before/After Optimization Comparison"""
    print("\n" + "="*70)
    print("DEMO 3: Before/After Optimization")
    print("="*70)
    
    # BEFORE optimization
    print("\n📊 BEFORE optimization:")
    with trace_scope() as before_graph:
        checkout_workflow()
    
    before_anomalies = detect_anomalies(before_graph)
    before_root = analyze_root_cause(before_graph)
    
    print(f"  Anomalies: {before_anomalies['severity_summary']['total']}")
    print(f"  Root causes: {before_root['total_root_causes']}")
    print(f"  Total impact: {before_root['impact_analysis']['total_time_impact']:.3f}s")
    
    # Simulated AFTER optimization (faster execution)
    def optimized_checkout():
        """Optimized version with caching and batching."""
        print("Processing optimized checkout...")
        # Simulated optimizations
        time.sleep(0.3)  # Much faster than before
        print("Processed 5 users (optimized)")
    
    print("\n📊 AFTER optimization:")
    with trace_scope() as after_graph:
        optimized_checkout()
    
    after_anomalies = detect_anomalies(after_graph)
    after_root = analyze_root_cause(after_graph)
    
    print(f"  Anomalies: {after_anomalies['severity_summary']['total']}")
    print(f"  Root causes: {after_root['total_root_causes']}")
    
    # Comparison
    print("\n" + "-"*70)
    print("IMPROVEMENT:")
    print("-"*70)
    anomaly_reduction = before_anomalies['severity_summary']['total'] - after_anomalies['severity_summary']['total']
    print(f"  Anomalies reduced: {anomaly_reduction}")
    print(f"  Root causes reduced: {before_root['total_root_causes'] - after_root['total_root_causes']}")


def demo_production_monitoring():
    """Demo 4: Production Monitoring Setup"""
    print("\n" + "="*70)
    print("DEMO 4: Production Monitoring Setup")
    print("="*70)
    
    from callflow_tracer.ai import AnomalyDetector
    
    # Setup baseline from normal operations
    print("\n📊 Establishing baseline (3 normal executions)...")
    baseline_graphs = []
    for i in range(3):
        with trace_scope() as graph:
            # Simulate normal operation
            time.sleep(0.1)
        baseline_graphs.append(graph)
    
    detector = AnomalyDetector(baseline_graphs=baseline_graphs, sensitivity=2.0)
    print("✓ Baseline established")
    
    # Monitor production traffic
    print("\n🔍 Monitoring production traffic...")
    
    for request_id in range(5):
        print(f"\n--- Request {request_id + 1} ---")
        
        with trace_scope() as graph:
            if request_id == 2:
                # Simulate slow request
                checkout_workflow()
            else:
                # Normal request
                time.sleep(0.1)
        
        # Detect anomalies
        anomalies = detector.detect(graph)
        severity = anomalies['severity_summary']
        
        if severity['total'] > 0:
            print(f"⚠️  ALERT: {severity['total']} anomalies detected!")
            print(f"   Severity: {severity['overall_severity']}")
            
            # Trigger root cause analysis
            root_analysis = analyze_root_cause(graph, issue_type='performance')
            if root_analysis['root_causes']:
                top_cause = root_analysis['root_causes'][0]
                print(f"   Root cause: {top_cause['function']}")
                print(f"   Action: Investigate immediately")
        else:
            print("✓ Normal operation")


def demo_ci_cd_integration():
    """Demo 5: CI/CD Performance Gate"""
    print("\n" + "="*70)
    print("DEMO 5: CI/CD Performance Gate")
    print("="*70)
    
    print("\n📊 Running performance test...")
    with trace_scope() as graph:
        checkout_workflow()
    
    # Detect anomalies
    anomalies = detect_anomalies(graph, sensitivity=2.5)
    severity = anomalies['severity_summary']
    
    # Root cause analysis
    root_analysis = analyze_root_cause(graph, issue_type='performance', threshold=0.1)
    
    # Performance gate logic
    print("\n" + "-"*70)
    print("CI/CD PERFORMANCE GATE:")
    print("-"*70)
    
    passed = True
    
    # Check 1: Critical anomalies
    if severity['critical'] > 0:
        print("❌ FAIL: Critical anomalies detected")
        passed = False
    else:
        print("✓ PASS: No critical anomalies")
    
    # Check 2: High severity anomalies
    if severity['high'] > 2:
        print("❌ FAIL: Too many high-severity anomalies")
        passed = False
    else:
        print("✓ PASS: Acceptable high-severity count")
    
    # Check 3: Root cause impact
    impact = root_analysis['impact_analysis']['total_time_impact']
    if impact > 2.0:
        print(f"❌ FAIL: Total impact too high ({impact:.3f}s)")
        passed = False
    else:
        print(f"✓ PASS: Impact within limits ({impact:.3f}s)")
    
    print("\n" + "-"*70)
    if passed:
        print("✅ BUILD PASSED - Performance acceptable")
    else:
        print("❌ BUILD FAILED - Performance issues detected")
        print("\nBlocking issues:")
        for rec in anomalies['recommendations'][:3]:
            print(f"  {rec}")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║        Advanced Debugging - Root Cause + Anomaly Detection          ║
║                                                                      ║
║  Comprehensive debugging with graph algorithms + statistics         ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        demo_combined_analysis()
        demo_debugging_workflow()
        demo_before_after_comparison()
        demo_production_monitoring()
        demo_ci_cd_integration()
        
        print("\n" + "="*70)
        print("✅ All demos completed!")
        print("="*70)
        print("\n🚀 Combined Power:")
        print("• Anomaly Detection: Finds WHAT is wrong")
        print("• Root Cause Analysis: Finds WHY it's wrong")
        print("• Together: Complete debugging solution")
        print("\n💡 Real-World Applications:")
        print("• Production monitoring and alerting")
        print("• CI/CD performance gates")
        print("• Performance regression detection")
        print("• Incident response and debugging")
        print("• Before/after optimization validation")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted")
    except Exception as e:
        print(f"\n\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
