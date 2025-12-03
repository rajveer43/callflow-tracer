"""
Unit tests for OpenTelemetry export functionality.

Tests cover:
- Basic OTel export
- Exemplars linking
- Sampling
- Config loading
- Metrics bridging
"""

import unittest
import json
import os
import sys
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from callflow_tracer import trace_scope, custom_metric, MetricsCollector
from callflow_tracer.opentelemetry_exporter import (
    export_callgraph_to_otel,
    export_callgraph_with_metrics,
    CallFlowExemplar,
    OpenTelemetryNotAvailable,
)
from callflow_tracer.otel_config import OTelConfig


class TestCallFlowExemplar(unittest.TestCase):
    """Test CallFlowExemplar class."""

    def test_exemplar_creation(self):
        """Test creating an exemplar."""
        exemplar = CallFlowExemplar(
            trace_id="trace-123",
            span_id="span-456",
            value=0.234,
            metric_name="test_metric",
            attributes={"key": "value"}
        )
        self.assertEqual(exemplar.trace_id, "trace-123")
        self.assertEqual(exemplar.span_id, "span-456")
        self.assertEqual(exemplar.value, 0.234)
        self.assertEqual(exemplar.metric_name, "test_metric")

    def test_exemplar_to_dict(self):
        """Test exemplar serialization."""
        exemplar = CallFlowExemplar(
            trace_id="trace-123",
            span_id="span-456",
            value=0.5,
            metric_name="metric",
            attributes={"tag": "value"}
        )
        data = exemplar.to_dict()
        self.assertIn("trace_id", data)
        self.assertIn("span_id", data)
        self.assertIn("value", data)
        self.assertIn("metric_name", data)
        self.assertIn("attributes", data)


class TestOTelExport(unittest.TestCase):
    """Test OpenTelemetry export functions."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a simple trace
        @custom_metric("test_func", sla_threshold=0.1)
        def test_func():
            return 42

        with trace_scope(None) as graph:
            test_func()
            self.graph = graph

    def test_export_basic(self):
        """Test basic OTel export."""
        try:
            result = export_callgraph_to_otel(
                self.graph,
                service_name="test-service"
            )
            self.assertEqual(result["status"], "success")
            self.assertGreater(result["span_count"], 0)
            self.assertEqual(result["service_name"], "test-service")
        except OpenTelemetryNotAvailable:
            self.skipTest("OpenTelemetry SDK not installed")

    def test_export_with_environment(self):
        """Test export with environment tag."""
        try:
            result = export_callgraph_to_otel(
                self.graph,
                service_name="test-service",
                environment="staging"
            )
            self.assertEqual(result["environment"], "staging")
        except OpenTelemetryNotAvailable:
            self.skipTest("OpenTelemetry SDK not installed")

    def test_export_with_sampling(self):
        """Test export with sampling."""
        try:
            result = export_callgraph_to_otel(
                self.graph,
                service_name="test-service",
                sampling_rate=0.5
            )
            self.assertEqual(result["sampling_rate"], 0.5)
        except OpenTelemetryNotAvailable:
            self.skipTest("OpenTelemetry SDK not installed")

    def test_export_with_exemplars(self):
        """Test export with exemplars."""
        exemplars = [
            CallFlowExemplar(
                trace_id="test-trace",
                span_id="test-span",
                value=0.1,
                metric_name="test_func"
            )
        ]
        try:
            result = export_callgraph_to_otel(
                self.graph,
                service_name="test-service",
                exemplars=exemplars
            )
            self.assertGreaterEqual(result["exemplar_count"], 0)
        except OpenTelemetryNotAvailable:
            self.skipTest("OpenTelemetry SDK not installed")

    def test_export_with_resource_attributes(self):
        """Test export with resource attributes."""
        attrs = {
            "service.version": "1.0.0",
            "deployment.environment": "test"
        }
        try:
            result = export_callgraph_to_otel(
                self.graph,
                service_name="test-service",
                resource_attributes=attrs
            )
            self.assertEqual(result["status"], "success")
        except OpenTelemetryNotAvailable:
            self.skipTest("OpenTelemetry SDK not installed")

    def test_export_with_metrics(self):
        """Test export with metrics bridging."""
        metrics = MetricsCollector.get_metrics()
        try:
            result = export_callgraph_with_metrics(
                self.graph,
                metrics,
                service_name="test-service"
            )
            self.assertEqual(result["status"], "success")
        except OpenTelemetryNotAvailable:
            self.skipTest("OpenTelemetry SDK not installed")


class TestOTelConfig(unittest.TestCase):
    """Test OTel configuration management."""

    def test_default_config(self):
        """Test default configuration."""
        config = OTelConfig()
        self.assertEqual(config.get("service_name"), "callflow-tracer")
        self.assertEqual(config.get("sampling_rate"), 1.0)

    def test_config_get_nested(self):
        """Test nested config access."""
        config = OTelConfig()
        exporter_type = config.get("exporter.type")
        self.assertIsNotNone(exporter_type)

    def test_config_to_dict(self):
        """Test config serialization."""
        config = OTelConfig()
        data = config.to_dict()
        self.assertIn("service_name", data)
        self.assertIn("exporter", data)
        self.assertIn("resource_attributes", data)

    def test_config_to_json(self):
        """Test config JSON serialization."""
        config = OTelConfig()
        json_str = config.to_json()
        data = json.loads(json_str)
        self.assertIn("service_name", data)

    def test_config_save_and_load(self):
        """Test saving and loading config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "test_config.yaml")
            
            # Save config
            config = OTelConfig()
            config.save_to_file(config_path, format="yaml")
            self.assertTrue(os.path.exists(config_path))
            
            # Load config
            config2 = OTelConfig(config_path)
            self.assertEqual(
                config2.get("service_name"),
                config.get("service_name")
            )

    def test_config_env_override(self):
        """Test environment variable override."""
        os.environ["CALLFLOW_OTEL_SERVICE_NAME"] = "env-service"
        config = OTelConfig()
        config.load_from_env()
        self.assertEqual(config.get("service_name"), "env-service")
        del os.environ["CALLFLOW_OTEL_SERVICE_NAME"]

    def test_config_merge(self):
        """Test config merging."""
        config = OTelConfig()
        new_config = {
            "service_name": "merged-service",
            "exporter": {
                "type": "otlp_grpc"
            }
        }
        config._merge_config(new_config)
        self.assertEqual(config.get("service_name"), "merged-service")
        self.assertEqual(config.get("exporter.type"), "otlp_grpc")


class TestOTelIntegration(unittest.TestCase):
    """Integration tests for OTel export."""

    def setUp(self):
        """Set up test fixtures."""
        @custom_metric("integration_test", sla_threshold=0.1)
        def func_a():
            return func_b()

        def func_b():
            return 42

        with trace_scope(None) as graph:
            func_a()
            self.graph = graph

    def test_full_export_workflow(self):
        """Test complete export workflow."""
        try:
            # Get metrics
            metrics = MetricsCollector.get_metrics()

            # Create exemplars
            exemplars = []
            for metric_name, metric_data in metrics.items():
                if isinstance(metric_data, dict) and "value" in metric_data:
                    exemplar = CallFlowExemplar(
                        trace_id="integration-test",
                        span_id="test-span",
                        value=metric_data.get("value", 0),
                        metric_name=metric_name
                    )
                    exemplars.append(exemplar)

            # Export with all features
            result = export_callgraph_to_otel(
                self.graph,
                service_name="integration-test",
                environment="test",
                exemplars=exemplars,
                sampling_rate=1.0,
                resource_attributes={"service.version": "1.0.0"}
            )

            self.assertEqual(result["status"], "success")
            self.assertGreater(result["span_count"], 0)
            self.assertEqual(result["service_name"], "integration-test")
            self.assertEqual(result["environment"], "test")

        except OpenTelemetryNotAvailable:
            self.skipTest("OpenTelemetry SDK not installed")


if __name__ == "__main__":
    unittest.main()
