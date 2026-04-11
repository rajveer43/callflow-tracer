"""Analysis, forecasting, anomaly, and quality helpers."""


class _MissingOptionalDep:
    """Sentinel raised when an optional dependency group is not installed."""

    def __init__(self, symbol: str, extra: str = "analysis"):
        self._symbol = symbol
        self._extra = extra

    def __call__(self, *args, **kwargs):
        raise ImportError(
            f"'{self._symbol}' requires optional dependencies. "
            f"Install them with: pip install callflow-tracer[{self._extra}]"
        )

    def __repr__(self):
        return f"<missing optional: {self._symbol}>"

    def __bool__(self):
        return False


try:
    from .anomaly_detection import (
        AnomalyAlert,
        AnomalyDetector,
        BaselineLearner,
        BaselineStats,
        analyze_custom_metric,
        analyze_function_duration,
        export_anomaly_report,
        generate_anomaly_report,
        get_anomaly_detector,
    )
except ImportError as _anomaly_err:
    _msg = str(_anomaly_err)
    AnomalyAlert = _MissingOptionalDep("AnomalyAlert")
    AnomalyDetector = _MissingOptionalDep("AnomalyDetector")
    BaselineLearner = _MissingOptionalDep("BaselineLearner")
    BaselineStats = _MissingOptionalDep("BaselineStats")
    analyze_custom_metric = _MissingOptionalDep("analyze_custom_metric")
    analyze_function_duration = _MissingOptionalDep("analyze_function_duration")
    export_anomaly_report = _MissingOptionalDep("export_anomaly_report")
    generate_anomaly_report = _MissingOptionalDep("generate_anomaly_report")
    get_anomaly_detector = _MissingOptionalDep("get_anomaly_detector")
from .code_churn import (
    ChurnCorrelation,
    ChurnCorrelationAnalyzer,
    ChurnMetrics,
    CodeChurnAnalyzer,
    generate_churn_report,
)
from .code_quality import (
    ComplexityAnalyzer,
    ComplexityMetrics,
    MaintainabilityAnalyzer,
    MaintainabilityMetrics,
    QualityTrend,
    QualityTrendAnalyzer,
    TechnicalDebtAnalyzer,
    TechnicalDebtIndicator,
    analyze_codebase,
)
from .debug_summary import format_debug_summary, summarize_graph, summarize_trace_data
from .regression_explainer import (
    explain_regression,
    format_regression_report,
)
from ..visualization.comparison import compare_graphs, export_comparison_html
from .predictive_analysis import (
    CapacityPlanner,
    CapacityPrediction,
    PerformancePrediction,
    PerformancePredictor,
    ResourceForecast,
    ResourceForecaster,
    ScalabilityAnalysis,
    ScalabilityAnalyzer,
    generate_predictive_report,
)

__all__ = [
    "analyze_codebase",
    "ComplexityAnalyzer",
    "MaintainabilityAnalyzer",
    "TechnicalDebtAnalyzer",
    "QualityTrendAnalyzer",
    "ComplexityMetrics",
    "MaintainabilityMetrics",
    "TechnicalDebtIndicator",
    "QualityTrend",
    "PerformancePredictor",
    "CapacityPlanner",
    "ScalabilityAnalyzer",
    "ResourceForecaster",
    "generate_predictive_report",
    "PerformancePrediction",
    "CapacityPrediction",
    "ScalabilityAnalysis",
    "ResourceForecast",
    "CodeChurnAnalyzer",
    "ChurnCorrelationAnalyzer",
    "generate_churn_report",
    "ChurnMetrics",
    "ChurnCorrelation",
    "compare_graphs",
    "export_comparison_html",
    "summarize_graph",
    "summarize_trace_data",
    "format_debug_summary",
    "explain_regression",
    "format_regression_report",
    "get_anomaly_detector",
    "analyze_function_duration",
    "analyze_custom_metric",
    "generate_anomaly_report",
    "export_anomaly_report",
    "AnomalyDetector",
    "BaselineLearner",
    "AnomalyAlert",
    "BaselineStats",
]
