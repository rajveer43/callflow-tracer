"""Analysis, forecasting, anomaly, and quality helpers."""

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
except ImportError:
    AnomalyAlert = None
    AnomalyDetector = None
    BaselineLearner = None
    BaselineStats = None
    analyze_custom_metric = None
    analyze_function_duration = None
    export_anomaly_report = None
    generate_anomaly_report = None
    get_anomaly_detector = None
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
