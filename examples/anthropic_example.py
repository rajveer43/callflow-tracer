"""
Example using Anthropic Claude for AI-powered trace analysis.

This demonstrates how to use Anthropic's Claude models with CallFlow Tracer.

Setup:
    pip install anthropic
    export ANTHROPIC_API_KEY="your-key-here"
    
Get API Key:
    https://console.anthropic.com/settings/keys
"""

import time
from callflow_tracer import trace_scope
from callflow_tracer.ai import summarize_trace, query_trace, AnthropicProvider


def slow_database_operation():
    """Simulates a slow database operation."""
    time.sleep(0.2)
    return {"users": [1, 2, 3, 4, 5]}


def process_data(data):
    """Process data with some computation."""
    time.sleep(0.05)
    return [x * 2 for x in data.get("users", [])]


def cache_results(results):
    """Cache processed results."""
    time.sleep(0.01)
    return f"cached_{len(results)}_items"


def main_application():
    """Main application workflow."""
    print("Fetching data...")
    data = slow_database_operation()
    
    print("Processing data...")
    results = process_data(data)
    
    print("Caching results...")
    cache_key = cache_results(results)
    
    print(f"Done! Cache key: {cache_key}")
    return results


def demo_anthropic_summarization():
    """Demo 1: Trace Summarization with Claude"""
    print("\n" + "="*70)
    print("DEMO 1: Trace Summarization with Anthropic Claude")
    print("="*70)
    
    # Configure Anthropic provider
    provider = AnthropicProvider(model="claude-3-5-sonnet-20241022")
    
    # Check if available
    if not provider.is_available():
        print("❌ Anthropic not configured!")
        print("Set ANTHROPIC_API_KEY environment variable")
        print("Get your key at: https://console.anthropic.com/settings/keys")
        return
    
    print("✓ Anthropic provider configured")
    print(f"  Model: {provider.model}")
    
    # Trace application
    print("\n📊 Running application with tracing...")
    with trace_scope() as graph:
        main_application()
    
    # Get AI summary using Claude
    print("\n🤖 Generating AI summary with Claude...")
    try:
        summary = summarize_trace(graph, provider=provider, include_recommendations=True)
        
        print("\n" + "-"*70)
        print("CLAUDE AI SUMMARY:")
        print("-"*70)
        print(summary['summary'])
        
        print("\n" + "-"*70)
        print("KEY METRICS:")
        print("-"*70)
        print(f"⏱️  Total time: {summary['total_execution_time']}s")
        print(f"📦 Functions: {summary['total_functions']}")
        print(f"📞 Calls: {summary['total_calls']}")
        
        print("\n" + "-"*70)
        print("TOP BOTTLENECKS:")
        print("-"*70)
        for i, bottleneck in enumerate(summary['bottlenecks'][:3], 1):
            print(f"{i}. {bottleneck['function']}")
            print(f"   ⏱️  {bottleneck['total_time']}s ({bottleneck['percentage']}%)")
            print(f"   📞 {bottleneck['call_count']} calls")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_anthropic_queries():
    """Demo 2: Natural Language Queries with Claude"""
    print("\n" + "="*70)
    print("DEMO 2: Natural Language Queries with Anthropic Claude")
    print("="*70)
    
    # Configure Anthropic
    provider = AnthropicProvider(model="claude-3-5-sonnet-20241022")
    
    if not provider.is_available():
        print("❌ Anthropic not configured!")
        return
    
    print("✓ Anthropic provider configured")
    
    # Trace application
    print("\n📊 Running application...")
    with trace_scope() as graph:
        main_application()
    
    # Ask questions using Claude
    questions = [
        "Which function is the slowest?",
        "How can I optimize this code for better performance?",
        "What's causing the performance bottleneck?",
        "Analyze the code structure and suggest improvements",
        "What are the potential scalability issues?",
    ]
    
    print("\n🤖 Asking Claude about the trace...\n")
    
    for i, question in enumerate(questions, 1):
        print("-"*70)
        print(f"Q{i}: {question}")
        print("-"*70)
        
        try:
            # Use LLM for complex questions
            result = query_trace(graph, question, provider=provider, use_llm=True)
            print(result['answer'])
            print()
        except Exception as e:
            print(f"Error: {e}\n")


def demo_anthropic_model_comparison():
    """Demo 3: Compare Different Claude Models"""
    print("\n" + "="*70)
    print("DEMO 3: Anthropic Claude Model Comparison")
    print("="*70)
    
    # Test different Claude models
    models = [
        ("claude-3-5-sonnet-20241022", "Latest Sonnet - Best balance"),
        ("claude-3-5-haiku-20241022", "Haiku - Fast and efficient"),
        ("claude-3-opus-20240229", "Opus - Highest intelligence"),
    ]
    
    print("\n📊 Running application...")
    with trace_scope() as graph:
        main_application()
    
    print("\n🤖 Testing different Claude models...\n")
    
    for model, description in models:
        print("-"*70)
        print(f"Model: {model}")
        print(f"Description: {description}")
        print("-"*70)
        
        try:
            provider = AnthropicProvider(model=model)
            if not provider.is_available():
                print("❌ Not configured")
                continue
            
            start = time.time()
            summary = summarize_trace(graph, provider=provider, include_recommendations=False)
            duration = time.time() - start
            
            print(f"✓ Generated in {duration:.2f}s")
            print(f"Summary length: {len(summary['summary'])} chars")
            print(f"First 150 chars: {summary['summary'][:150]}...")
            print()
            
        except Exception as e:
            print(f"❌ Error: {e}\n")


def demo_anthropic_code_analysis():
    """Demo 4: Advanced Code Analysis with Claude"""
    print("\n" + "="*70)
    print("DEMO 4: Advanced Code Analysis with Claude")
    print("="*70)
    
    provider = AnthropicProvider(model="claude-3-5-sonnet-20241022")
    
    if not provider.is_available():
        print("❌ Anthropic not configured!")
        return
    
    print("✓ Using Claude 3.5 Sonnet for advanced analysis")
    
    # Create a more complex trace
    def recursive_fibonacci(n):
        if n <= 1:
            return n
        return recursive_fibonacci(n-1) + recursive_fibonacci(n-2)
    
    def io_operation():
        time.sleep(0.01)
        return "data"
    
    def complex_app():
        # Mix of operations
        for i in range(3):
            main_application()
        
        result = recursive_fibonacci(8)
        data = io_operation()
        
        return result
    
    print("\n📊 Running complex application...")
    with trace_scope() as graph:
        complex_app()
    
    # Advanced code analysis questions
    advanced_questions = [
        "Provide a detailed performance analysis of this code",
        "What are the algorithmic complexity issues?",
        "Suggest specific code refactoring opportunities",
        "How would you optimize the database operations?",
        "Explain the performance characteristics in detail",
    ]
    
    print("\n🤖 Advanced code analysis with Claude...\n")
    
    for i, question in enumerate(advanced_questions, 1):
        print("-"*70)
        print(f"Q{i}: {question}")
        print("-"*70)
        
        try:
            result = query_trace(graph, question, provider=provider, use_llm=True)
            print(result['answer'])
            print()
        except Exception as e:
            print(f"Error: {e}\n")


def demo_anthropic_comparison_with_others():
    """Demo 5: Compare Claude with Other Providers"""
    print("\n" + "="*70)
    print("DEMO 5: Claude vs Other Providers")
    print("="*70)
    
    print("\n📊 Running application...")
    with trace_scope() as graph:
        main_application()
    
    # Test question
    question = "Analyze this code and suggest optimizations"
    
    print(f"\n🤖 Asking: '{question}'\n")
    
    # Try different providers
    from callflow_tracer.ai import OpenAIProvider, GeminiProvider
    
    providers = [
        ("Claude 3.5 Sonnet", AnthropicProvider(model="claude-3-5-sonnet-20241022")),
        ("GPT-4o Mini", OpenAIProvider(model="gpt-4o-mini")),
        ("Gemini 1.5 Flash", GeminiProvider(model="gemini-1.5-flash")),
    ]
    
    for name, provider in providers:
        print("-"*70)
        print(f"Provider: {name}")
        print("-"*70)
        
        if not provider.is_available():
            print(f"❌ {name} not configured")
            print()
            continue
        
        try:
            start = time.time()
            result = query_trace(graph, question, provider=provider, use_llm=True)
            duration = time.time() - start
            
            print(f"✓ Response time: {duration:.2f}s")
            print(f"Answer length: {len(result['answer'])} chars")
            print(f"Preview: {result['answer'][:200]}...")
            print()
            
        except Exception as e:
            print(f"❌ Error: {e}\n")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║       CallFlow Tracer - Anthropic Claude Integration Demo           ║
║                                                                      ║
║  This demo shows how to use Anthropic's Claude models for           ║
║  intelligent trace analysis and natural language queries.           ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        demo_anthropic_summarization()
        demo_anthropic_queries()
        demo_anthropic_model_comparison()
        demo_anthropic_code_analysis()
        demo_anthropic_comparison_with_others()
        
        print("\n" + "="*70)
        print("✅ All demos completed!")
        print("="*70)
        print("\nWhy use Anthropic Claude?")
        print("• Excellent code understanding and analysis")
        print("• Strong reasoning capabilities")
        print("• Great for complex performance analysis")
        print("• Detailed and thoughtful responses")
        print("• Multiple model tiers for different needs")
        print("\nModel recommendations:")
        print("• Claude 3.5 Sonnet: Best balance (recommended)")
        print("• Claude 3.5 Haiku: Fast and cost-effective")
        print("• Claude 3 Opus: Highest quality for critical analysis")
        print("\nClaude Strengths:")
        print("✓ Superior code analysis")
        print("✓ Detailed explanations")
        print("✓ Strong reasoning about performance")
        print("✓ Excellent at suggesting optimizations")
        print("\nGet your API key: https://console.anthropic.com/settings/keys")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted")
    except Exception as e:
        print(f"\n\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
