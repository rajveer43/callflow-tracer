"""
AI-powered features for CallFlow Tracer.

This module provides comprehensive intelligent analysis capabilities including:
- Trace summarization with natural language insights
- Natural language query interface for exploring traces
- Performance analysis and recommendations
- Root cause analysis with graph algorithms
- Anomaly detection with statistical analysis
- Trace comparison and regression detection
- Continuous profiling and monitoring
- Auto-fix generation and code suggestions
- Distributed tracing integration
- Test generation and load analysis
- Cost analysis and dependency analysis
- Trend analysis and forecasting
- Security and privacy analysis
- Alert management and webhooks
- Documentation generation
- Smart instrumentation suggestions
- Visual debugging tools
"""

from .llm_provider import LLMProvider, OpenAIProvider, AnthropicProvider, GeminiProvider, OllamaProvider
from .summarizer import TraceSummarizer, summarize_trace
from .query_engine import QueryEngine, query_trace
from .root_cause_analyzer import RootCauseAnalyzer, analyze_root_cause
from .anomaly_detector import AnomalyDetector, detect_anomalies

# New AI features
from .comparison import TraceComparator, compare_traces
from .regression_detector import RegressionDetector, detect_regressions
from .continuous_profiler import ContinuousProfiler
from .auto_fixer import AutoFixer, generate_fixes
from .distributed_tracer import DistributedTracer
from .test_generator import TestGenerator, generate_performance_tests
from .refactoring_suggester import RefactoringSuggester, suggest_refactoring
from .cost_analyzer import CostAnalyzer, analyze_costs
from .dependency_analyzer import DependencyAnalyzer, analyze_dependencies
from .trend_analyzer import TrendAnalyzer, analyze_trends
from .security_analyzer import SecurityAnalyzer, analyze_security
from .alert_manager import AlertManager, create_alert_manager
from .load_analyzer import LoadAnalyzer, analyze_load_behavior
from .doc_generator import DocumentationGenerator, generate_documentation
from .instrumentation_suggester import InstrumentationSuggester, suggest_instrumentation
from .visual_debugger import VisualDebugger, create_visual_debugger

__all__ = [
    # Core LLM providers
    'LLMProvider',
    'OpenAIProvider', 
    'AnthropicProvider',
    'GeminiProvider',
    'OllamaProvider',
    
    # Original AI features
    'TraceSummarizer',
    'summarize_trace',
    'QueryEngine',
    'query_trace',
    'RootCauseAnalyzer',
    'analyze_root_cause',
    'AnomalyDetector',
    'detect_anomalies',
    
    # Trace comparison & regression
    'TraceComparator',
    'compare_traces',
    'RegressionDetector',
    'detect_regressions',
    
    # Continuous profiling
    'ContinuousProfiler',
    
    # Auto-fix generation
    'AutoFixer',
    'generate_fixes',
    
    # Distributed tracing
    'DistributedTracer',
    
    # Test generation
    'TestGenerator',
    'generate_performance_tests',
    
    # Refactoring suggestions
    'RefactoringSuggester',
    'suggest_refactoring',
    
    # Cost analysis
    'CostAnalyzer',
    'analyze_costs',
    
    # Dependency analysis
    'DependencyAnalyzer',
    'analyze_dependencies',
    
    # Trend analysis
    'TrendAnalyzer',
    'analyze_trends',
    
    # Security analysis
    'SecurityAnalyzer',
    'analyze_security',
    
    # Alert management
    'AlertManager',
    'create_alert_manager',
    
    # Load analysis
    'LoadAnalyzer',
    'analyze_load_behavior',
    
    # Documentation generation
    'DocumentationGenerator',
    'generate_documentation',
    
    # Instrumentation suggestions
    'InstrumentationSuggester',
    'suggest_instrumentation',
    
    # Visual debugging
    'VisualDebugger',
    'create_visual_debugger',
]
