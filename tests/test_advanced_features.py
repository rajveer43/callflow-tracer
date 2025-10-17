"""
Tests for advanced AI features: Root Cause Analysis and Anomaly Detection.
"""

import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from callflow_tracer import trace_scope
from callflow_tracer.ai import (
    analyze_root_cause,
    RootCauseAnalyzer,
    detect_anomalies,
    AnomalyDetector
)


# Test application functions
def slow_function():
    """Simulates a slow function."""
    time.sleep(0.1)
    return "slow"


def fast_function():
    """Simulates a fast function."""
    time.sleep(0.001)
    return "fast"


def caller_function():
    """Calls slow function."""
    return slow_function()


def root_caller():
    """Root of the call chain."""
    return caller_function()


def frequently_called():
    """Called many times."""
    time.sleep(0.001)
    return "frequent"


def test_application():
    """Test application with performance issues."""
    root_caller()
    for i in range(20):
        frequently_called()


# Test 1: Basic root cause analysis
def test_root_cause_analysis_basic():
    """Test basic root cause analysis."""
    print("\n" + "="*70)
    print("TEST 1: Basic Root Cause Analysis")
    print("="*70)
    
    try:
        with trace_scope() as graph:
            test_application()
        
        analysis = analyze_root_cause(graph, issue_type='performance')
        
        assert 'root_causes' in analysis
        assert 'impact_analysis' in analysis
        assert analysis['total_root_causes'] > 0
        
        print(f"✓ Root causes identified: {analysis['total_root_causes']}")
        print(f"✓ Total issues: {analysis['total_issues']}")
        
        # Check root cause structure
        if analysis['root_causes']:
            root = analysis['root_causes'][0]
            assert 'function' in root
            assert 'confidence' in root
            assert 'affected_nodes' in root
            print(f"✓ Top root cause: {root['function']} (confidence: {root['confidence']:.2f})")
        
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


# Test 2: Root cause analyzer class
def test_root_cause_analyzer_class():
    """Test RootCauseAnalyzer class."""
    print("\n" + "="*70)
    print("TEST 2: RootCauseAnalyzer Class")
    print("="*70)
    
    try:
        with trace_scope() as graph:
            test_application()
        
        analyzer = RootCauseAnalyzer()
        analysis = analyzer.analyze(graph, issue_type='performance', threshold=0.05)
        
        assert analysis is not None
        assert 'root_causes' in analysis
        print(f"✓ Analyzer created and executed")
        print(f"✓ Found {len(analysis['root_causes'])} root causes")
        
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


# Test 3: Basic anomaly detection
def test_anomaly_detection_basic():
    """Test basic anomaly detection."""
    print("\n" + "="*70)
    print("TEST 3: Basic Anomaly Detection")
    print("="*70)
    
    try:
        with trace_scope() as graph:
            test_application()
        
        anomalies = detect_anomalies(graph)
        
        assert 'time_anomalies' in anomalies
        assert 'frequency_anomalies' in anomalies
        assert 'severity_summary' in anomalies
        
        severity = anomalies['severity_summary']
        print(f"✓ Total anomalies: {severity['total']}")
        print(f"✓ Overall severity: {severity['overall_severity']}")
        
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


# Test 4: Anomaly detector class
def test_anomaly_detector_class():
    """Test AnomalyDetector class."""
    print("\n" + "="*70)
    print("TEST 4: AnomalyDetector Class")
    print("="*70)
    
    try:
        detector = AnomalyDetector(sensitivity=2.0)
        
        with trace_scope() as graph:
            test_application()
        
        anomalies = detector.detect(graph)
        
        assert anomalies is not None
        print(f"✓ Detector created with sensitivity 2.0")
        print(f"✓ Detected {anomalies['severity_summary']['total']} anomalies")
        
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


# Test 5: Baseline comparison
def test_baseline_comparison():
    """Test anomaly detection with baseline."""
    print("\n" + "="*70)
    print("TEST 5: Baseline Comparison")
    print("="*70)
    
    try:
        # Create baseline
        baseline_graphs = []
        for i in range(3):
            with trace_scope() as graph:
                for j in range(5):
                    fast_function()
            baseline_graphs.append(graph)
        
        print(f"✓ Created baseline with {len(baseline_graphs)} graphs")
        
        # Detect anomalies against baseline
        with trace_scope() as test_graph:
            test_application()
        
        anomalies = detect_anomalies(test_graph, baseline_graphs=baseline_graphs)
        
        assert anomalies is not None
        print(f"✓ Baseline comparison completed")
        print(f"✓ Anomalies: {anomalies['severity_summary']['total']}")
        
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


# Test 6: Specific anomaly types
def test_specific_anomaly_types():
    """Test detecting specific anomaly types."""
    print("\n" + "="*70)
    print("TEST 6: Specific Anomaly Types")
    print("="*70)
    
    try:
        with trace_scope() as graph:
            test_application()
        
        # Test each type
        time_anomalies = detect_anomalies(graph, detect_types=['time'])
        assert 'time_anomalies' in time_anomalies
        print(f"✓ Time anomalies: {len(time_anomalies['time_anomalies'])}")
        
        freq_anomalies = detect_anomalies(graph, detect_types=['frequency'])
        assert 'frequency_anomalies' in freq_anomalies
        print(f"✓ Frequency anomalies: {len(freq_anomalies['frequency_anomalies'])}")
        
        pattern_anomalies = detect_anomalies(graph, detect_types=['pattern'])
        assert 'pattern_anomalies' in pattern_anomalies
        print(f"✓ Pattern anomalies: {len(pattern_anomalies['pattern_anomalies'])}")
        
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


# Test 7: Root cause with different issue types
def test_root_cause_issue_types():
    """Test root cause analysis with different issue types."""
    print("\n" + "="*70)
    print("TEST 7: Root Cause Issue Types")
    print("="*70)
    
    try:
        with trace_scope() as graph:
            test_application()
        
        # Performance issues
        perf_analysis = analyze_root_cause(graph, issue_type='performance')
        assert perf_analysis['issue_type'] == 'performance'
        print(f"✓ Performance analysis: {perf_analysis['total_root_causes']} causes")
        
        # Bottleneck issues
        bottleneck_analysis = analyze_root_cause(graph, issue_type='bottleneck')
        assert bottleneck_analysis['issue_type'] == 'bottleneck'
        print(f"✓ Bottleneck analysis: {bottleneck_analysis['total_root_causes']} causes")
        
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


# Test 8: Sensitivity tuning
def test_sensitivity_tuning():
    """Test anomaly detection sensitivity."""
    print("\n" + "="*70)
    print("TEST 8: Sensitivity Tuning")
    print("="*70)
    
    try:
        with trace_scope() as graph:
            test_application()
        
        # Test different sensitivities
        sensitivities = [1.5, 2.0, 2.5]
        results = []
        
        for sensitivity in sensitivities:
            anomalies = detect_anomalies(graph, sensitivity=sensitivity)
            count = anomalies['severity_summary']['total']
            results.append(count)
            print(f"✓ Sensitivity {sensitivity}: {count} anomalies")
        
        # Higher sensitivity should detect fewer anomalies
        assert results[0] >= results[1] >= results[2] or all(r == 0 for r in results)
        print("✓ Sensitivity tuning works correctly")
        
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


# Test 9: Impact analysis
def test_impact_analysis():
    """Test impact analysis in root cause."""
    print("\n" + "="*70)
    print("TEST 9: Impact Analysis")
    print("="*70)
    
    try:
        with trace_scope() as graph:
            test_application()
        
        analysis = analyze_root_cause(graph, issue_type='performance')
        impact = analysis['impact_analysis']
        
        assert 'total_affected_functions' in impact
        assert 'total_time_impact' in impact
        assert 'impact_percentage' in impact
        
        print(f"✓ Affected functions: {impact['total_affected_functions']}")
        print(f"✓ Time impact: {impact['total_time_impact']:.3f}s")
        print(f"✓ Impact percentage: {impact['impact_percentage']:.1f}%")
        
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


# Test 10: Recommendations
def test_recommendations():
    """Test recommendation generation."""
    print("\n" + "="*70)
    print("TEST 10: Recommendations")
    print("="*70)
    
    try:
        with trace_scope() as graph:
            test_application()
        
        anomalies = detect_anomalies(graph)
        
        assert 'recommendations' in anomalies
        assert isinstance(anomalies['recommendations'], list)
        
        print(f"✓ Generated {len(anomalies['recommendations'])} recommendations")
        for i, rec in enumerate(anomalies['recommendations'][:3], 1):
            print(f"  {i}. {rec}")
        
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def run_all_tests():
    """Run all tests and report results."""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║         Advanced Features Tests - Root Cause + Anomaly              ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    tests = [
        ("Root Cause Analysis Basic", test_root_cause_analysis_basic),
        ("RootCauseAnalyzer Class", test_root_cause_analyzer_class),
        ("Anomaly Detection Basic", test_anomaly_detection_basic),
        ("AnomalyDetector Class", test_anomaly_detector_class),
        ("Baseline Comparison", test_baseline_comparison),
        ("Specific Anomaly Types", test_specific_anomaly_types),
        ("Root Cause Issue Types", test_root_cause_issue_types),
        ("Sensitivity Tuning", test_sensitivity_tuning),
        ("Impact Analysis", test_impact_analysis),
        ("Recommendations", test_recommendations),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print("="*70)
    print(f"Results: {passed}/{total} tests passed")
    print("="*70)
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
