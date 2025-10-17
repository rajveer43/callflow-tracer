"""
Example using OpenAI GPT for AI-powered trace analysis.

This demonstrates how to use OpenAI's GPT models with CallFlow Tracer.

Setup:
    pip install openai
    export OPENAI_API_KEY="your-key-here"
    
Get API Key:
    https://platform.openai.com/api-keys
"""

import time
from callflow_tracer import trace_scope
from callflow_tracer.ai import summarize_trace, query_trace, OpenAIProvider


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


def demo_openai_summarization():
    """Demo 1: Trace Summarization with OpenAI"""
    print("\n" + "="*70)
    print("DEMO 1: Trace Summarization with OpenAI GPT")
    print("="*70)
    
    # Configure OpenAI provider
    provider = OpenAIProvider(model="gpt-4o-mini")  # or "gpt-4o", "gpt-4-turbo"
    
    # Check if available
    if not provider.is_available():
        print("❌ OpenAI not configured!")
        print("Set OPENAI_API_KEY environment variable")
        print("Get your key at: https://platform.openai.com/api-keys")
        return
    
    print("✓ OpenAI provider configured")
    print(f"  Model: {provider.model}")
    
    # Trace application
    print("\n📊 Running application with tracing...")
    with trace_scope() as graph:
        main_application()
    
    # Get AI summary using OpenAI
    print("\n🤖 Generating AI summary with OpenAI GPT...")
    try:
        summary = summarize_trace(graph, provider=provider, include_recommendations=True)
        
        print("\n" + "-"*70)
        print("OPENAI GPT AI SUMMARY:")
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


def demo_openai_queries():
    """Demo 2: Natural Language Queries with OpenAI"""
    print("\n" + "="*70)
    print("DEMO 2: Natural Language Queries with OpenAI GPT")
    print("="*70)
    
    # Configure OpenAI
    provider = OpenAIProvider(model="gpt-4o-mini")
    
    if not provider.is_available():
        print("❌ OpenAI not configured!")
        return
    
    print("✓ OpenAI provider configured")
    
    # Trace application
    print("\n📊 Running application...")
    with trace_scope() as graph:
        main_application()
    
    # Ask questions using OpenAI
    questions = [
        "Which function is the slowest?",
        "How can I optimize this code?",
        "What's causing the performance bottleneck?",
        "Are there any N+1 query patterns?",
        "Suggest specific code improvements",
    ]
    
    print("\n🤖 Asking OpenAI GPT about the trace...\n")
    
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


def demo_openai_model_comparison():
    """Demo 3: Compare Different OpenAI Models"""
    print("\n" + "="*70)
    print("DEMO 3: OpenAI Model Comparison")
    print("="*70)
    
    # Test different OpenAI models
    models = [
        ("gpt-4o-mini", "Fast and cost-effective"),
        ("gpt-4o", "Best quality and speed balance"),
        ("gpt-4-turbo", "High quality analysis"),
    ]
    
    print("\n📊 Running application...")
    with trace_scope() as graph:
        main_application()
    
    print("\n🤖 Testing different OpenAI models...\n")
    
    for model, description in models:
        print("-"*70)
        print(f"Model: {model}")
        print(f"Description: {description}")
        print("-"*70)
        
        try:
            provider = OpenAIProvider(model=model)
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


def demo_openai_advanced():
    """Demo 4: Advanced OpenAI Features"""
    print("\n" + "="*70)
    print("DEMO 4: Advanced OpenAI Analysis")
    print("="*70)
    
    provider = OpenAIProvider(model="gpt-4o")
    
    if not provider.is_available():
        print("❌ OpenAI not configured!")
        return
    
    print("✓ Using GPT-4o for advanced analysis")
    
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
    
    # Advanced questions
    advanced_questions = [
        "Analyze the algorithmic complexity of this code",
        "What are the top 3 optimization opportunities?",
        "Explain the execution flow in simple terms",
        "What would happen if I doubled the input size?",
    ]
    
    print("\n🤖 Advanced analysis with GPT-4o...\n")
    
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


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║         CallFlow Tracer - OpenAI GPT Integration Demo               ║
║                                                                      ║
║  This demo shows how to use OpenAI's GPT models for intelligent     ║
║  trace analysis and natural language queries.                       ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        demo_openai_summarization()
        demo_openai_queries()
        demo_openai_model_comparison()
        demo_openai_advanced()
        
        print("\n" + "="*70)
        print("✅ All demos completed!")
        print("="*70)
        print("\nWhy use OpenAI?")
        print("• Best quality AI analysis")
        print("• Excellent code understanding")
        print("• Multiple model options")
        print("• Fast and reliable")
        print("\nModel recommendations:")
        print("• gpt-4o-mini: Fast, cost-effective for most use cases")
        print("• gpt-4o: Best balance of quality and speed")
        print("• gpt-4-turbo: Highest quality for critical analysis")
        print("\nGet your API key: https://platform.openai.com/api-keys")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted")
    except Exception as e:
        print(f"\n\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
