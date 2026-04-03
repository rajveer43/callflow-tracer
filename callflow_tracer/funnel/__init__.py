"""Funnel analysis, visualization, monitoring, and reporting APIs."""

from .models import FunnelSession, FunnelStep, FunnelType, StepStatus
from .analysis import (
    CallGraphFunnelAdapter,
    FunnelAnalyzer,
    analyze_call_graph_funnel,
    create_funnel,
    funnel_scope,
    track_funnel_step,
)
from .algorithms import (
    FunnelAnomalyDetector,
    FunnelOptimizer,
    FunnelPatternRecognizer,
    FunnelPredictor,
    analyze_funnel_anomalies,
    generate_optimization_plan,
    predict_funnel_performance,
    recognize_funnel_patterns,
)
from .monitor import (
    AlertSeverity,
    FunnelAlert,
    FunnelDashboard,
    MonitoringMode,
    MonitoringThreshold,
    RealTimeFunnelMonitor,
    create_funnel_dashboard,
    create_funnel_monitor,
    monitored_funnel,
)
from .reporting import (
    FunnelExporter,
    FunnelReporter,
    export_funnel_data,
    generate_funnel_report,
)
from .visualizer import (
    FunnelVisualizer,
    create_funnel_visualizer,
    generate_funnel_dashboard,
)

try:
    from .cli import add_funnel_cli
except Exception:  # pragma: no cover - optional CLI dependency

    def add_funnel_cli(*args, **kwargs):
        raise RuntimeError("Funnel CLI is unavailable. Install click to enable it.")


__all__ = [
    "FunnelStep",
    "FunnelSession",
    "FunnelType",
    "StepStatus",
    "FunnelAnalyzer",
    "funnel_scope",
    "track_funnel_step",
    "create_funnel",
    "analyze_call_graph_funnel",
    "CallGraphFunnelAdapter",
    "FunnelAnomalyDetector",
    "FunnelPredictor",
    "FunnelPatternRecognizer",
    "FunnelOptimizer",
    "analyze_funnel_anomalies",
    "predict_funnel_performance",
    "recognize_funnel_patterns",
    "generate_optimization_plan",
    "AlertSeverity",
    "MonitoringMode",
    "FunnelAlert",
    "MonitoringThreshold",
    "RealTimeFunnelMonitor",
    "FunnelDashboard",
    "create_funnel_monitor",
    "create_funnel_dashboard",
    "monitored_funnel",
    "FunnelExporter",
    "FunnelReporter",
    "export_funnel_data",
    "generate_funnel_report",
    "FunnelVisualizer",
    "create_funnel_visualizer",
    "generate_funnel_dashboard",
    "add_funnel_cli",
]
