"""
Complete example demonstrating AI enhancements in CallFlow Tracer v0.4.0

This example shows:
1. Using advanced LLM providers with retry logic
2. Enhanced prompt engineering with domain-specific templates
3. Performance analysis with expert personas
4. Root cause analysis with chain-of-thought reasoning
5. Auto-fix generation with confidence scores
6. Anomaly detection with statistical analysis
"""

import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from callflow_tracer import trace_scope
from callflow_tracer.ai import (
    OpenAIProvider,
    AnthropicProvider,
    GeminiProvider,
    QueryEngine,
    RootCauseAnalyzer,
    AutoFixer,
    AnomalyDetector,
    get_prompt_for_task,
)


# ============================================================================
# EXAMPLE 1: Performance Analysis with Enhanced Prompts
# ============================================================================

def example_performance_analysis():
    """Analyze performance issues using enhanced prompts."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Performance Analysis with Enhanced Prompts")
    print("="*70)
    
    # Trace your application
    def slow_function():
        """Intentionally slow function for demonstration."""
        total = 0
        for i in range(1000000):
            total += i
        return total
    
    def database_query():
        """Simulated database query."""
        import time
        time.sleep(0.1)
        return "data"
    
    def main_app():
        """Main application."""
        results = []
        for i in range(5):
            results.append(database_query())  # N+1 pattern
        slow_function()
        return results
    
    # Trace execution
    with trace_scope() as graph:
        main_app()
    
    # Create provider with retry logic
    provider = OpenAIProvider(
        model="gpt-4o",
        max_retries=3,
        retry_delay=1.0
    )
    
    # Create query engine
    engine = QueryEngine(provider=provider)
    
    # Ask performance questions
    questions = [
        "Which functions are slowest?",
        "What are the N+1 query patterns?",
        "Where should I add caching?",
    ]
    
    print("\nPerformance Analysis Results:")
    print("-" * 70)
    
    for question in questions:
        print(f"\nQ: {question}")
        result = engine.query(graph, question)
        print(f"A: {result['answer'][:200]}...")  # First 200 chars


# ============================================================================
# EXAMPLE 2: Root Cause Analysis with Chain-of-Thought
# ============================================================================

def example_root_cause_analysis():
    """Perform root cause analysis with enhanced prompts."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Root Cause Analysis with Chain-of-Thought")
    print("="*70)
    
    # Trace application
    def expensive_operation():
        """Expensive operation."""
        import time
        time.sleep(0.5)
    
    def inefficient_loop():
        """Inefficient loop calling expensive operation."""
        for i in range(10):
            expensive_operation()
    
    def main():
        inefficient_loop()
    
    with trace_scope() as graph:
        main()
    
    # Create provider with Claude 3 Opus for best reasoning
    provider = AnthropicProvider(
        model="claude-3-opus-20240229",
        max_retries=3,
        retry_delay=1.0
    )
    
    # Perform root cause analysis
    analyzer = RootCauseAnalyzer(provider=provider)
    analysis = analyzer.analyze(graph, issue_type="performance")
    
    print("\nRoot Cause Analysis Results:")
    print("-" * 70)
    print(f"Total Issues Found: {analysis['total_issues']}")
    print(f"Total Root Causes: {analysis['total_root_causes']}")
    
    print("\nTop Root Causes:")
    for i, cause in enumerate(analysis['root_causes'][:3], 1):
        print(f"\n{i}. {cause['function']}")
        print(f"   Total Time: {cause['total_time']:.3f}s")
        print(f"   Affected Nodes: {cause['affected_nodes']}")
        print(f"   Confidence: {cause['confidence']:.0%}")
    
    print("\nLLM Insights:")
    print(analysis['llm_insights'][:300] if analysis['llm_insights'] else "N/A")


# ============================================================================
# EXAMPLE 3: Auto-Fix Generation with LLM
# ============================================================================

def example_auto_fix_generation():
    """Generate code fixes using enhanced prompts."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Auto-Fix Generation with LLM")
    print("="*70)
    
    # Create provider with GPT-4 Turbo for code generation
    provider = OpenAIProvider(
        model="gpt-4-turbo",
        max_retries=3,
        retry_delay=1.0
    )
    
    # Create auto-fixer
    fixer = AutoFixer(llm_provider=provider)
    
    # Example issue
    issue = {
        'type': 'n_plus_one',
        'function': 'get_user_orders',
        'description': 'N+1 query problem: fetching orders one by one in a loop',
        'file': 'app.py'
    }
    
    # Generate fix
    print("\nGenerating fix for N+1 query pattern...")
    print("-" * 70)
    
    # Note: This is a simplified example
    # In production, you would pass actual root cause analysis results
    
    print("\nExample Fix Template:")
    print("""
    Issue: N+1 Query Problem
    Confidence: 95%
    Severity: HIGH
    Estimated Improvement: 80%
    
    BEFORE:
    def get_user_orders(user_id):
        orders = []
        for order_id in get_order_ids(user_id):
            orders.append(get_order(order_id))  # N+1!
        return orders
    
    AFTER:
    def get_user_orders(user_id):
        order_ids = get_order_ids(user_id)
        return get_orders_batch(order_ids)  # Batched!
    """)


# ============================================================================
# EXAMPLE 4: Anomaly Detection with Statistical Analysis
# ============================================================================

def example_anomaly_detection():
    """Detect anomalies using statistical analysis."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Anomaly Detection with Statistical Analysis")
    print("="*70)
    
    # Trace application with anomalies
    def normal_function():
        """Normal execution."""
        total = 0
        for i in range(100):
            total += i
        return total
    
    def anomalous_function():
        """Anomalously slow function."""
        import time
        time.sleep(1.0)  # Much slower than normal
    
    def main():
        for i in range(5):
            normal_function()
        anomalous_function()
    
    with trace_scope() as graph:
        main()
    
    # Detect anomalies
    detector = AnomalyDetector(sensitivity=2.0)
    anomalies = detector.detect(graph)
    
    print("\nAnomaly Detection Results:")
    print("-" * 70)
    print(f"Total Anomalies: {anomalies['severity_summary']['total']}")
    print(f"Critical: {anomalies['severity_summary']['critical']}")
    print(f"High: {anomalies['severity_summary']['high']}")
    print(f"Medium: {anomalies['severity_summary']['medium']}")
    print(f"Low: {anomalies['severity_summary']['low']}")
    
    print("\nTime Anomalies:")
    for anomaly in anomalies['time_anomalies'][:3]:
        print(f"  - {anomaly['function']}")
        print(f"    Value: {anomaly['value']:.3f}s")
        print(f"    Expected: {anomaly['expected']:.3f}s")
        print(f"    Deviation: {anomaly['deviation']:.3f}s")
        print(f"    Severity: {anomaly['severity']}")
    
    print("\nRecommendations:")
    for rec in anomalies['recommendations']:
        print(f"  - {rec}")


# ============================================================================
# EXAMPLE 5: Using Enhanced Prompts Directly
# ============================================================================

def example_enhanced_prompts():
    """Use enhanced prompt templates directly."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Using Enhanced Prompts Directly")
    print("="*70)
    
    # Get enhanced prompt for performance analysis
    system_prompt, user_prompt = get_prompt_for_task(
        'performance_analysis',
        graph_summary="""
        Total execution time: 5.234s
        Total functions: 42
        Total calls: 1523
        
        Top functions by execution time:
        1. database_query: 3.500s (66.9%) - 50 calls
        2. process_data: 1.200s (22.9%) - 100 calls
        3. validate_input: 0.300s (5.7%) - 500 calls
        """,
        question="What are the main performance bottlenecks?"
    )
    
    print("\nSystem Prompt:")
    print("-" * 70)
    print(system_prompt[:300] + "...")
    
    print("\nUser Prompt:")
    print("-" * 70)
    print(user_prompt[:300] + "...")
    
    # Show other available prompts
    print("\n\nAvailable Prompt Templates:")
    print("-" * 70)
    templates = [
        'performance_analysis',
        'root_cause_analysis',
        'code_fix',
        'anomaly_analysis',
        'security_analysis',
        'refactoring',
        'test_generation',
        'documentation',
    ]
    
    for i, template in enumerate(templates, 1):
        print(f"{i}. {template}")


# ============================================================================
# EXAMPLE 6: Model Comparison
# ============================================================================

def example_model_comparison():
    """Compare different LLM models."""
    print("\n" + "="*70)
    print("EXAMPLE 6: Model Comparison and Selection")
    print("="*70)
    
    models = {
        'OpenAI': [
            ('gpt-4-turbo', 128000, 'Best for code generation'),
            ('gpt-4o', 128000, 'Balanced performance'),
            ('gpt-4o-mini', 128000, 'Cost-effective'),
        ],
        'Anthropic': [
            ('claude-3-opus-20240229', 200000, 'Best reasoning'),
            ('claude-3-5-sonnet-20241022', 200000, 'Latest model'),
            ('claude-3-haiku-20240307', 200000, 'Fast & cheap'),
        ],
        'Google': [
            ('gemini-1.5-pro', 1000000, 'Largest context'),
            ('gemini-1.5-flash', 1000000, 'Fast'),
        ],
    }
    
    print("\nAvailable Models:")
    print("-" * 70)
    
    for provider, model_list in models.items():
        print(f"\n{provider}:")
        for model, context, description in model_list:
            print(f"  - {model}")
            print(f"    Context: {context:,} tokens")
            print(f"    Best for: {description}")


# ============================================================================
# EXAMPLE 7: Retry Logic Demonstration
# ============================================================================

def example_retry_logic():
    """Demonstrate retry logic with exponential backoff."""
    print("\n" + "="*70)
    print("EXAMPLE 7: Retry Logic with Exponential Backoff")
    print("="*70)
    
    print("\nRetry Configuration:")
    print("-" * 70)
    
    provider = OpenAIProvider(
        model="gpt-4o",
        max_retries=5,
        retry_delay=2.0
    )
    
    print(f"Provider: OpenAI")
    print(f"Model: {provider.model}")
    print(f"Max Retries: {provider.max_retries}")
    print(f"Initial Retry Delay: {provider.retry_delay}s")
    
    print("\nRetry Schedule (with exponential backoff):")
    print("-" * 70)
    
    delay = provider.retry_delay
    for attempt in range(1, provider.max_retries + 1):
        if attempt == 1:
            print(f"Attempt {attempt}: Immediate")
        else:
            print(f"Attempt {attempt}: {delay:.1f}s + jitter")
            delay *= 2
    
    print("\nAutomatic Retry Triggers:")
    print("-" * 70)
    print("  - Rate limiting (429 Too Many Requests)")
    print("  - Server errors (5xx)")
    print("  - Timeout errors")
    print("  - Connection errors")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("CallFlow Tracer AI Enhancements - Complete Examples")
    print("Version 0.4.0")
    print("="*70)
    
    try:
        # Run examples
        example_performance_analysis()
        example_root_cause_analysis()
        example_auto_fix_generation()
        example_anomaly_detection()
        example_enhanced_prompts()
        example_model_comparison()
        example_retry_logic()
        
        print("\n" + "="*70)
        print("All examples completed successfully!")
        print("="*70)
        
    except Exception as e:
        print(f"\nError running examples: {str(e)}")
        print("\nNote: Some examples require API keys to be configured:")
        print("  export OPENAI_API_KEY='sk-...'")
        print("  export ANTHROPIC_API_KEY='sk-ant-...'")
        print("  export GEMINI_API_KEY='...'")


if __name__ == "__main__":
    main()
