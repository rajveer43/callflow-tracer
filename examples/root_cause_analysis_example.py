"""
Root Cause Analysis Example for CallFlow Tracer.

Demonstrates how to use graph algorithms + LLM to identify root causes
of performance issues and debug faster.

Setup:
    pip install openai  # or anthropic, google-generativeai
    export OPENAI_API_KEY="your-key"  # or ANTHROPIC_API_KEY, GEMINI_API_KEY
"""

import time
import random
from callflow_tracer import trace_scope
from callflow_tracer.ai import analyze_root_cause, RootCauseAnalyzer


# Simulated application with performance issues
def slow_database_query(query_id):
    """ROOT CAUSE: Slow database operation."""
    time.sleep(0.15)  # Simulates slow DB
    return {"id": query_id, "data": "result"}


def process_query_result(result):
    """Processes query result - depends on slow DB."""
    time.sleep(0.02)
    return result["data"].upper()


def fetch_user_data(user_id):
    """Fetches user data - calls slow DB."""
    query = slow_database_query(user_id)
    processed = process_query_result(query)
    return processed


def generate_report(user_ids):
    """Generates report - calls fetch_user_data multiple times."""
    results = []
    for user_id in user_ids:
        data = fetch_user_data(user_id)
        results.append(data)
    return results


def main_workflow():
    """Main workflow - entry point."""
    print("Starting workflow...")
    user_ids = [1, 2, 3, 4, 5]
    report = generate_report(user_ids)
    print(f"Generated report with {len(report)} entries")
    return report


def demo_basic_root_cause_analysis():
    """Demo 1: Basic Root Cause Analysis"""
    print("\n" + "="*70)
    print("DEMO 1: Basic Root Cause Analysis")
    print("="*70)
    
    print("\n📊 Running application with performance issues...")
    with trace_scope() as graph:
        main_workflow()
    
    print("\n🔍 Analyzing root causes...")
    analysis = analyze_root_cause(graph, issue_type='performance')
    
    print("\n" + "-"*70)
    print("ROOT CAUSE ANALYSIS RESULTS:")
    print("-"*70)
    
    print(f"\nIssue Type: {analysis['issue_type']}")
    print(f"Total Issues Found: {analysis['total_issues']}")
    print(f"Root Causes Identified: {analysis['total_root_causes']}")
    
    print("\n" + "-"*70)
    print("TOP ROOT CAUSES:")
    print("-"*70)
    
    for i, root in enumerate(analysis['root_causes'][:5], 1):
        print(f"\n{i}. {root['function']} (module: {root['module']})")
        print(f"   ⏱️  Total time: {root['total_time']:.3f}s")
        print(f"   🔥 Self time: {root['self_time']:.3f}s")
        print(f"   📞 Call count: {root['call_count']}")
        print(f"   💥 Affected nodes: {root['affected_nodes']}")
        print(f"   📊 Impact time: {root['total_impact_time']:.3f}s")
        print(f"   ✅ Confidence: {root['confidence']:.2f}")
        
        if root['upstream_path']:
            print(f"   📍 Call path: {' -> '.join([analysis['root_causes'][0]['function'] for _ in root['upstream_path']])}")
    
    print("\n" + "-"*70)
    print("IMPACT ANALYSIS:")
    print("-"*70)
    impact = analysis['impact_analysis']
    print(f"Total affected functions: {impact['total_affected_functions']}")
    print(f"Total time impact: {impact['total_time_impact']:.3f}s")
    print(f"Impact percentage: {impact['impact_percentage']:.1f}%")


def demo_root_cause_with_llm():
    """Demo 2: Root Cause Analysis with LLM Insights"""
    print("\n" + "="*70)
    print("DEMO 2: Root Cause Analysis with LLM Insights")
    print("="*70)
    
    print("\n📊 Running application...")
    with trace_scope() as graph:
        main_workflow()
    
    print("\n🤖 Analyzing with LLM insights...")
    try:
        analysis = analyze_root_cause(graph, issue_type='performance')
        
        if analysis['llm_insights']:
            print("\n" + "-"*70)
            print("AI INSIGHTS:")
            print("-"*70)
            print(analysis['llm_insights'])
        else:
            print("\n⚠️  LLM not configured - showing basic analysis only")
            print("Configure an LLM provider for enhanced insights")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")


def demo_custom_threshold():
    """Demo 3: Root Cause Analysis with Custom Threshold"""
    print("\n" + "="*70)
    print("DEMO 3: Custom Threshold Analysis")
    print("="*70)
    
    print("\n📊 Running application...")
    with trace_scope() as graph:
        main_workflow()
    
    # Try different thresholds
    thresholds = [0.05, 0.1, 0.2]
    
    for threshold in thresholds:
        print(f"\n--- Threshold: {threshold}s ---")
        analysis = analyze_root_cause(graph, issue_type='performance', threshold=threshold)
        print(f"Root causes found: {analysis['total_root_causes']}")
        
        if analysis['root_causes']:
            top = analysis['root_causes'][0]
            print(f"Top cause: {top['function']} ({top['total_time']:.3f}s)")


def demo_error_root_cause():
    """Demo 4: Root Cause Analysis for Errors"""
    print("\n" + "="*70)
    print("DEMO 4: Error Root Cause Analysis")
    print("="*70)
    
    def buggy_function():
        """Function that might cause errors."""
        if random.random() > 0.5:
            time.sleep(0.1)
        return "ok"
    
    def caller_function():
        """Calls buggy function."""
        return buggy_function()
    
    print("\n📊 Running application with potential errors...")
    with trace_scope() as graph:
        try:
            for i in range(5):
                caller_function()
        except:
            pass
    
    print("\n🔍 Analyzing error root causes...")
    analysis = analyze_root_cause(graph, issue_type='error')
    
    print(f"\nError root causes found: {analysis['total_root_causes']}")
    if analysis['root_causes']:
        for root in analysis['root_causes']:
            print(f"- {root['function']}: {root['call_count']} calls")


def demo_bottleneck_analysis():
    """Demo 5: Bottleneck Root Cause Analysis"""
    print("\n" + "="*70)
    print("DEMO 5: Bottleneck Root Cause Analysis")
    print("="*70)
    
    def cpu_intensive():
        """CPU-intensive operation."""
        time.sleep(0.08)
        return sum(range(1000))
    
    def io_operation():
        """I/O operation."""
        time.sleep(0.05)
        return "data"
    
    def mixed_workload():
        """Mixed CPU and I/O."""
        for i in range(3):
            cpu_intensive()
        for i in range(5):
            io_operation()
    
    print("\n📊 Running mixed workload...")
    with trace_scope() as graph:
        mixed_workload()
    
    print("\n🔍 Analyzing bottlenecks...")
    analysis = analyze_root_cause(graph, issue_type='bottleneck')
    
    print(f"\nBottleneck root causes: {analysis['total_root_causes']}")
    for i, root in enumerate(analysis['root_causes'][:3], 1):
        print(f"\n{i}. {root['function']}")
        print(f"   Self time: {root['self_time']:.3f}s (bottleneck indicator)")
        print(f"   Total time: {root['total_time']:.3f}s")


def demo_advanced_analyzer():
    """Demo 6: Advanced RootCauseAnalyzer Usage"""
    print("\n" + "="*70)
    print("DEMO 6: Advanced RootCauseAnalyzer")
    print("="*70)
    
    from callflow_tracer.ai import OpenAIProvider
    
    # Create analyzer with specific provider
    try:
        provider = OpenAIProvider(model="gpt-4o-mini")
        analyzer = RootCauseAnalyzer(provider=provider)
        print("✓ Using OpenAI GPT-4o-mini for analysis")
    except:
        analyzer = RootCauseAnalyzer()
        print("⚠️  Using basic analysis (no LLM)")
    
    print("\n📊 Running application...")
    with trace_scope() as graph:
        main_workflow()
    
    print("\n🔍 Performing detailed analysis...")
    analysis = analyzer.analyze(graph, issue_type='performance', threshold=0.1)
    
    print("\n" + "-"*70)
    print("DETAILED ANALYSIS:")
    print("-"*70)
    
    # Show detailed root cause information
    for root in analysis['root_causes'][:3]:
        print(f"\n📍 {root['function']}")
        print(f"   Confidence: {root['confidence']:.0%}")
        print(f"   Impact: {root['total_impact_time']:.3f}s affecting {root['affected_nodes']} nodes")
        
        if root['upstream_path']:
            print(f"   Call chain depth: {len(root['upstream_path'])}")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║           CallFlow Tracer - Root Cause Analysis Demo                ║
║                                                                      ║
║  Uses graph algorithms + LLM to identify root causes of issues      ║
║  and help you debug faster!                                         ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        demo_basic_root_cause_analysis()
        demo_root_cause_with_llm()
        demo_custom_threshold()
        demo_error_root_cause()
        demo_bottleneck_analysis()
        demo_advanced_analyzer()
        
        print("\n" + "="*70)
        print("✅ All demos completed!")
        print("="*70)
        print("\n🔥 Root Cause Analysis Benefits:")
        print("• Identifies the true source of performance issues")
        print("• Traces problems through call chains")
        print("• Calculates impact and confidence scores")
        print("• Provides AI-powered insights and recommendations")
        print("• Helps debug faster by focusing on root causes")
        print("\n💡 Use Cases:")
        print("• Performance debugging")
        print("• Error tracing")
        print("• Bottleneck identification")
        print("• Production incident analysis")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted")
    except Exception as e:
        print(f"\n\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
