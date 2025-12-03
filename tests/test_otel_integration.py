#!/usr/bin/env python
"""
Quick integration test for OpenTelemetry export.

Run this script to verify OTel export is working correctly:
    python test_otel_integration.py

This script tests:
- Basic trace capture
- OTel export functionality
- Config file handling
- Metrics bridging
- CLI integration
"""

import sys
import os
import json
import subprocess
from pathlib import Path

# Add to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from callflow_tracer import trace_scope, custom_metric, MetricsCollector
from callflow_tracer.opentelemetry_exporter import (
    export_callgraph_to_otel,
    export_callgraph_with_metrics,
    CallFlowExemplar,
)
from callflow_tracer.otel_config import OTelConfig


def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_test(name, passed, message=""):
    """Print test result."""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"  {status}: {name}")
    if message:
        print(f"         {message}")


def test_trace_capture():
    """Test basic trace capture."""
    print_header("Test 1: Trace Capture")

    @custom_metric("test_func", sla_threshold=0.1)
    def test_func(n):
        if n <= 0:
            return 0
        return n + test_func(n - 1)

    try:
        with trace_scope(None) as graph:
            result = test_func(3)
        
        passed = graph is not None and len(graph.nodes) > 0
        print_test("Trace capture", passed, f"Captured {len(graph.nodes)} nodes")
        return graph
    except Exception as e:
        print_test("Trace capture", False, str(e))
        return None


def test_otel_export(graph):
    """Test basic OTel export."""
    print_header("Test 2: OTel Export")

    if graph is None:
        print_test("OTel export", False, "No graph available")
        return False

    try:
        result = export_callgraph_to_otel(
            graph,
            service_name="test-service"
        )
        passed = result["status"] == "success" and result["span_count"] > 0
        print_test(
            "OTel export",
            passed,
            f"Exported {result['span_count']} spans"
        )
        return passed
    except Exception as e:
        if "OpenTelemetry SDK is not installed" in str(e):
            print_test("OTel export", False, "OpenTelemetry SDK not installed (optional)")
        else:
            print_test("OTel export", False, str(e))
        return False


def test_exemplars(graph):
    """Test exemplar creation and linking."""
    print_header("Test 3: Exemplars")

    if graph is None:
        print_test("Exemplar creation", False, "No graph available")
        return False

    try:
        exemplar = CallFlowExemplar(
            trace_id="test-trace",
            span_id="test-span",
            value=0.123,
            metric_name="test_func",
            attributes={"key": "value"}
        )
        
        passed = (
            exemplar.trace_id == "test-trace" and
            exemplar.value == 0.123
        )
        print_test("Exemplar creation", passed)

        # Test exemplar linking
        result = export_callgraph_to_otel(
            graph,
            service_name="test-service",
            exemplars=[exemplar]
        )
        
        passed = result["status"] == "success"
        print_test(
            "Exemplar linking",
            passed,
            f"Linked {result['exemplar_count']} exemplars"
        )
        return passed
    except Exception as e:
        if "OpenTelemetry SDK is not installed" in str(e):
            print_test("Exemplar linking", False, "OpenTelemetry SDK not installed (optional)")
        else:
            print_test("Exemplar linking", False, str(e))
        return False


def test_sampling(graph):
    """Test sampling functionality."""
    print_header("Test 4: Sampling")

    if graph is None:
        print_test("Sampling", False, "No graph available")
        return False

    try:
        result = export_callgraph_to_otel(
            graph,
            service_name="test-service",
            sampling_rate=0.5
        )
        
        passed = result["sampling_rate"] == 0.5
        print_test(
            "Sampling",
            passed,
            f"Sampling rate: {result['sampling_rate']}"
        )
        return passed
    except Exception as e:
        if "OpenTelemetry SDK is not installed" in str(e):
            print_test("Sampling", False, "OpenTelemetry SDK not installed (optional)")
        else:
            print_test("Sampling", False, str(e))
        return False


def test_config():
    """Test OTel configuration."""
    print_header("Test 5: Configuration")

    try:
        # Test default config
        config = OTelConfig()
        passed = config.get("service_name") == "callflow-tracer"
        print_test("Default config", passed)

        # Test nested access
        exporter_type = config.get("exporter.type")
        passed = exporter_type is not None
        print_test("Nested config access", passed, f"Exporter type: {exporter_type}")

        # Test env override
        os.environ["CALLFLOW_OTEL_SERVICE_NAME"] = "env-test"
        config.load_from_env()
        passed = config.get("service_name") == "env-test"
        print_test("Environment override", passed)
        del os.environ["CALLFLOW_OTEL_SERVICE_NAME"]

        return True
    except Exception as e:
        print_test("Configuration", False, str(e))
        return False


def test_metrics_bridging(graph):
    """Test metrics bridging."""
    print_header("Test 6: Metrics Bridging")

    if graph is None:
        print_test("Metrics bridging", False, "No graph available")
        return False

    try:
        metrics = MetricsCollector.get_metrics()
        result = export_callgraph_with_metrics(
            graph,
            metrics,
            service_name="test-service"
        )
        
        passed = result["status"] == "success"
        print_test(
            "Metrics bridging",
            passed,
            f"Linked {result['exemplar_count']} metrics as exemplars"
        )
        return passed
    except Exception as e:
        if "OpenTelemetry SDK is not installed" in str(e):
            print_test("Metrics bridging", False, "OpenTelemetry SDK not installed (optional)")
        else:
            print_test("Metrics bridging", False, str(e))
        return False


def test_cli():
    """Test CLI integration."""
    print_header("Test 7: CLI Integration")

    try:
        # Test help command
        result = subprocess.run(
            ["callflow-tracer", "otel", "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        passed = result.returncode == 0
        print_test("CLI help", passed)
        return passed
    except FileNotFoundError:
        print_test("CLI help", False, "callflow-tracer command not found")
        return False
    except Exception as e:
        print_test("CLI help", False, str(e))
        return False


def main():
    """Run all integration tests."""
    print("\n" + "=" * 70)
    print("  OpenTelemetry Integration Test Suite")
    print("=" * 70)

    results = []

    # Run tests
    graph = test_trace_capture()
    results.append(("Trace Capture", graph is not None))

    results.append(("OTel Export", test_otel_export(graph)))
    results.append(("Exemplars", test_exemplars(graph)))
    results.append(("Sampling", test_sampling(graph)))
    results.append(("Configuration", test_config()))
    results.append(("Metrics Bridging", test_metrics_bridging(graph)))
    results.append(("CLI Integration", test_cli()))

    # Summary
    print_header("Test Summary")
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for name, passed in results:
        status = "✓" if passed else "✗"
        print(f"  {status} {name}")

    print(f"\n  Total: {passed_count}/{total_count} tests passed")

    if passed_count == total_count:
        print("\n  🎉 All tests passed!")
        return 0
    else:
        print(f"\n  ⚠️  {total_count - passed_count} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
