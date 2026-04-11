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
from callflow_tracer.observability.opentelemetry_exporter import (
    export_callgraph_to_otel,
    export_callgraph_with_metrics,
    CallFlowExemplar,
)
from callflow_tracer.observability.otel_config import OTelConfig


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

    def test_func(n):
        if n <= 0:
            return 0
        return n + test_func(n - 1)

    with trace_scope() as graph:
        test_func(3)

    assert graph is not None and len(graph.nodes) > 0


def _build_test_graph():
    """Build a simple call graph for testing."""
    def helper(n):
        if n <= 0:
            return 0
        return n + helper(n - 1)

    with trace_scope() as graph:
        helper(3)
    return graph


def test_otel_export():
    """Test basic OTel export."""
    print_header("Test 2: OTel Export")

    graph = _build_test_graph()

    try:
        result = export_callgraph_to_otel(graph, service_name="test-service")
        passed = result["status"] == "success" and result["span_count"] > 0
        print_test("OTel export", passed, f"Exported {result['span_count']} spans")
        assert passed
    except Exception as e:
        if "OpenTelemetry SDK is not installed" in str(e):
            import pytest
            pytest.skip("OpenTelemetry SDK not installed")
        raise


def test_exemplars():
    """Test exemplar creation and linking."""
    print_header("Test 3: Exemplars")

    graph = _build_test_graph()

    exemplar = CallFlowExemplar(
        trace_id="test-trace",
        span_id="test-span",
        value=0.123,
        metric_name="test_func",
        attributes={"key": "value"},
    )

    assert exemplar.trace_id == "test-trace" and exemplar.value == 0.123

    try:
        result = export_callgraph_to_otel(
            graph, service_name="test-service", exemplars=[exemplar]
        )
        assert result["status"] == "success"
    except Exception as e:
        if "OpenTelemetry SDK is not installed" in str(e):
            import pytest
            pytest.skip("OpenTelemetry SDK not installed")
        raise


def test_sampling():
    """Test sampling functionality."""
    print_header("Test 4: Sampling")

    graph = _build_test_graph()

    try:
        result = export_callgraph_to_otel(
            graph, service_name="test-service", sampling_rate=0.5
        )
        assert result["sampling_rate"] == 0.5
    except Exception as e:
        if "OpenTelemetry SDK is not installed" in str(e):
            import pytest
            pytest.skip("OpenTelemetry SDK not installed")
        raise


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


def test_metrics_bridging():
    """Test metrics bridging."""
    print_header("Test 6: Metrics Bridging")

    graph = _build_test_graph()

    try:
        metrics = MetricsCollector.get_metrics()
        result = export_callgraph_with_metrics(
            graph, metrics, service_name="test-service"
        )
        assert result["status"] == "success"
    except Exception as e:
        if "OpenTelemetry SDK is not installed" in str(e):
            import pytest
            pytest.skip("OpenTelemetry SDK not installed")
        raise


def test_cli():
    """Test CLI integration."""
    print_header("Test 7: CLI Integration")

    try:
        # Test help command
        result = subprocess.run(
            ["callflow-tracer", "otel", "--help"],
            capture_output=True,
            text=True,
            timeout=5,
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
