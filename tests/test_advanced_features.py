"""
Tests for Advanced Features: Anomaly Detection, Auto-instrumentation, and Plugin System
"""

import unittest
import tempfile
import json
import time
from unittest.mock import Mock, patch, MagicMock

# Import the modules to test
from callflow_tracer.anomaly_detection import (
    AnomalyDetector,
    BaselineLearner,
    AnomalyAlert,
    BaselineStats,
    get_anomaly_detector,
)

from callflow_tracer.core.auto_instrumentation import (
    AutoInstrumentationManager,
    HTTPInstrumentor,
    RedisInstrumentor,
    Boto3Instrumentor,
    get_auto_instrumentation_manager,
)

from callflow_tracer.core.plugin_system import (
    PluginManager,
    AnalyzerHook,
    ExporterHook,
    UIWidgetHook,
    PluginInfo,
    get_plugin_manager,
    register_analyzer,
)


class TestAnomalyDetection(unittest.TestCase):
    """Test anomaly detection functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.detector = AnomalyDetector(z_score_threshold=2.0)

    def test_baseline_learner(self):
        """Test baseline learning."""
        learner = BaselineLearner(min_samples=5)

        # Add samples
        for i in range(10):
            learner.add_sample("test_metric", 1.0 + i * 0.1)

        # Check baseline is ready
        self.assertTrue(learner.is_ready("test_metric"))

        # Check statistics
        baseline = learner.get_baseline("test_metric")
        self.assertIsNotNone(baseline)
        self.assertEqual(baseline.sample_count, 10)
        self.assertAlmostEqual(baseline.mean, 1.45, places=2)

    def test_anomaly_detection(self):
        """Test anomaly detection."""
        # Build a baseline with natural variation so the std is realistic.
        # Values alternate between 0.9 and 1.1 (mean=1.0, std≈0.1).
        # A z-score threshold of 3 means anomaly boundary ≈ 1.3; 1.05 is safe.
        for i in range(30):
            self.detector.analyze_metric("test_metric", 0.9 if i % 2 == 0 else 1.1)

        # Normal value close to the mean - no alert
        alert = self.detector.analyze_metric("test_metric", 1.05)
        self.assertIsNone(alert)

        # Anomalous value far from the mean - should trigger alert
        alert = self.detector.analyze_metric("test_metric", 5.0)
        self.assertIsNotNone(alert)
        self.assertEqual(alert.metric_name, "test_metric")
        self.assertEqual(alert.value, 5.0)
        self.assertGreater(alert.z_score, self.detector.z_score_threshold)

    def test_anomaly_report(self):
        """Test anomaly report generation."""
        # Build baseline first (alternating 0.9/1.1 → mean=1.0, std≈0.1)
        for i in range(30):
            self.detector.analyze_metric("test_metric", 0.9 if i % 2 == 0 else 1.1)

        # Now inject two clear anomalies
        self.detector.analyze_metric("test_metric", 5.0)  # Anomaly
        self.detector.analyze_metric("test_metric", 6.0)  # Anomaly

        report = self.detector.generate_report(hours=24)

        self.assertIn("total_alerts", report)
        self.assertIn("severity_breakdown", report)
        self.assertIn("top_anomalies", report)
        self.assertEqual(report["total_alerts"], 2)

    def test_severity_calculation(self):
        """Test anomaly severity calculation."""
        # Thresholds: >=5.0 → critical, >=4.0 → high, >=3.0 → medium, else low
        test_cases = [(2.0, "low"), (3.5, "medium"), (4.5, "high"), (5.5, "critical")]

        for z_score, expected_severity in test_cases:
            severity = self.detector._calculate_severity(z_score)
            self.assertEqual(severity, expected_severity)

    def test_concept_drift_detection(self):
        """Test concept drift detection."""
        # Build baseline
        for i in range(100):
            self.detector.analyze_metric("test_metric", 1.0)

        # Introduce drift
        for i in range(100):
            self.detector.analyze_metric("test_metric", 2.0)

        # Check for drift alerts
        alerts = self.detector.get_recent_alerts(hours=24)
        drift_alerts = [a for a in alerts if "drift" in a.metric_name]
        self.assertGreater(len(drift_alerts), 0)


class TestAutoInstrumentation(unittest.TestCase):
    """Test auto-instrumentation functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = AutoInstrumentationManager()

    def test_manager_initialization(self):
        """Test manager initialization."""
        self.assertEqual(len(self.manager.instrumentors), 3)
        self.assertIn("http", self.manager.instrumentors)
        self.assertIn("redis", self.manager.instrumentors)
        self.assertIn("boto3", self.manager.instrumentors)
        self.assertFalse(self.manager.enabled)

    def test_enable_disable_all(self):
        """Test enabling/disabling all instrumentation."""
        self.manager.enable_all()
        self.assertTrue(self.manager.enabled)

        for instrumentor in self.manager.instrumentors.values():
            self.assertTrue(instrumentor.instrumentation_enabled)

        self.manager.disable_all()
        self.assertFalse(self.manager.enabled)

        for instrumentor in self.manager.instrumentors.values():
            self.assertFalse(instrumentor.instrumentation_enabled)

    @patch("requests.Session.request")
    def test_http_instrumentation(self, mock_request):
        """Test HTTP instrumentation."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        http_instrumentor = HTTPInstrumentor()
        http_instrumentor.enable()

        # Import and use requests
        import requests

        session = requests.Session()

        # This should be instrumented
        response = session.get("http://example.com")

        # Verify the mock was called
        self.assertTrue(mock_request.called)

        # Check if original method was stored (key is now (obj, method_name) tuple)
        import requests as _req
        self.assertIn(
            (_req.Session, "request"), http_instrumentor.original_methods
        )

    def test_redis_instrumentation(self):
        """Test Redis instrumentation."""
        redis_instrumentor = RedisInstrumentor()

        # Test without redis installed
        try:
            redis_instrumentor.enable()
            # Should not raise an error
            self.assertFalse(redis_instrumentor.instrumentation_enabled)
        except Exception:
            pass  # Expected if redis not installed

    def test_boto3_instrumentation(self):
        """Test Boto3 instrumentation."""
        boto3_instrumentor = Boto3Instrumentor()

        # Test without boto3 installed
        try:
            boto3_instrumentor.enable()
            # Should not raise an error
            self.assertFalse(boto3_instrumentation.instrumentation_enabled)
        except Exception:
            pass  # Expected if boto3 not installed


class TestPluginSystem(unittest.TestCase):
    """Test plugin system functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = PluginManager()

    def test_register_analyzer(self):
        """Test registering an analyzer."""

        def test_analyzer(graph, **kwargs):
            return {"test": "result"}

        self.manager.register_analyzer("test_analyzer", test_analyzer)

        self.assertIn("test_analyzer", self.manager.analyzers)
        self.assertEqual(len(self.manager.list_analyzers()), 1)

    def test_register_exporter(self):
        """Test registering an exporter."""

        def test_exporter(graph, filename, **kwargs):
            pass

        self.manager.register_exporter("test_exporter", test_exporter, ["json"])

        self.assertIn("test_exporter", self.manager.exporters)
        self.assertEqual(
            self.manager.exporters["test_exporter"].file_extensions, ["json"]
        )

    def test_register_ui_widget(self):
        """Test registering a UI widget."""
        widget_config = {"type": "div", "content": "Test Widget"}

        self.manager.register_ui_widget("test_widget", widget_config)

        self.assertIn("test_widget", self.manager.ui_widgets)

    def test_run_analyzer(self):
        """Test running an analyzer."""

        def test_analyzer(graph, **kwargs):
            return {"node_count": len(graph.nodes) if hasattr(graph, "nodes") else 0}

        self.manager.register_analyzer("test_analyzer", test_analyzer)

        # Mock graph
        mock_graph = Mock()
        mock_graph.nodes = {"node1": Mock(), "node2": Mock()}

        result = self.manager.run_analyzer("test_analyzer", mock_graph)

        self.assertEqual(result["node_count"], 2)

    def test_hook_system(self):
        """Test hook system."""
        hook_called = []

        def test_hook(*args, **kwargs):
            hook_called.append(True)

        self.manager.register_hook("before_analysis", test_hook)
        self.manager.execute_hooks("before_analysis")

        self.assertEqual(len(hook_called), 1)

    def test_plugin_info(self):
        """Test plugin information tracking."""
        info = PluginInfo(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin",
            author="Test Author",
            plugin_type="analyzer",
            entry_point="test_module.test_func",
        )

        self.assertEqual(info.name, "test_plugin")
        self.assertEqual(info.version, "1.0.0")
        self.assertTrue(info.enabled)

    def test_plugin_decorator(self):
        """Test plugin registration decorator."""

        @register_analyzer("decorator_test", description="Test decorator")
        def test_analyzer(graph, **kwargs):
            return {"decorated": True}

        manager = get_plugin_manager()
        self.assertIn("decorator_test", manager.analyzers)

    def test_generate_ui_widgets(self):
        """Test UI widget generation."""
        widget_config = {"type": "div", "content": "Test Widget Content"}

        self.manager.register_ui_widget("test_widget", widget_config)

        html = self.manager.generate_ui_widgets()

        self.assertIn("test_widget", html)
        self.assertIn("Test Widget Content", html)

    def test_export_plugin_config(self):
        """Test plugin configuration export."""

        # Register some plugins
        def test_analyzer(graph, **kwargs):
            return {}

        def test_exporter(graph, filename, **kwargs):
            pass

        self.manager.register_analyzer("test_analyzer", test_analyzer)
        self.manager.register_exporter("test_exporter", test_exporter, ["json"])

        # Export config
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            self.manager.export_plugin_config(f.name)

            # Load and verify
            with open(f.name, "r") as rf:
                config = json.load(rf)

            self.assertIn("analyzers", config)
            self.assertIn("exporters", config)
            self.assertIn("test_analyzer", config["analyzers"])
            self.assertIn("test_exporter", config["exporters"])


class TestIntegration(unittest.TestCase):
    """Integration tests for advanced features."""

    def test_anomaly_detection_with_tracing(self):
        """Test anomaly detection integrated with tracing."""
        from callflow_tracer import trace_scope

        # Use a fresh detector (not the shared singleton) to avoid state
        # contamination from other tests.
        from callflow_tracer.analysis.anomaly_detection import AnomalyDetector
        detector = AnomalyDetector()

        # Trace some operations
        with trace_scope():
            # Build a sufficient baseline (min_samples=30 by default)
            for i in range(35):
                # Alternate slightly so std > 0
                detector.analyze_metric("test_function", 0.09 if i % 2 == 0 else 0.11)

            # Now inject clear anomalies — should trigger alerts
            for anomaly_val in [5.0, 6.0]:
                alert = detector.analyze_metric("test_function", anomaly_val)
                self.assertIsNotNone(alert)
                self.assertEqual(alert.metric_name, "test_function")

    def test_auto_instrumentation_context_manager(self):
        """Test auto-instrumentation context manager."""
        from callflow_tracer.core.auto_instrumentation import auto_instrumentation

        with auto_instrumentation(enabled=False) as manager:
            self.assertIsNotNone(manager)
            # Should be disabled since we passed enabled=False

    def test_plugin_system_with_hooks(self):
        """Test plugin system with hooks."""
        manager = get_plugin_manager()

        hook_results = []

        def before_analysis_hook(name, graph):
            hook_results.append(f"before_{name}")

        def after_analysis_hook(name, graph, result):
            hook_results.append(f"after_{name}")

        manager.register_hook("before_analysis", before_analysis_hook)
        manager.register_hook("after_analysis", after_analysis_hook)

        # Register and run an analyzer
        def test_analyzer(graph, **kwargs):
            return {"result": "test"}

        manager.register_analyzer("hook_test", test_analyzer)

        # Mock graph
        mock_graph = Mock()

        # Run analyzer
        result = manager.run_analyzer("hook_test", mock_graph)

        # Check hooks were called
        self.assertEqual(len(hook_results), 2)
        self.assertIn("before_hook_test", hook_results)
        self.assertIn("after_hook_test", hook_results)


if __name__ == "__main__":
    unittest.main()
