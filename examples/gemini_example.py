"""
Example using Google Gemini for AI-powered trace analysis.

This demonstrates how to use Google's Gemini model with CallFlow Tracer.

Setup:
    pip install google-generativeai
    export GEMINI_API_KEY="your-key-here"
    # OR
    export GOOGLE_API_KEY="your-key-here"
    
Get API Key:
    https://makersuite.google.com/app/apikey
"""

import time
from callflow_tracer import trace_scope
from callflow_tracer.ai import summarize_trace, query_trace, GeminiProvider


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


def demo_gemini_summarization():
    """Demo 1: Trace Summarization with Gemini"""
    print("\n" + "="*70)
    print("DEMO 1: Trace Summarization with Google Gemini")
    print("="*70)
    
    # Configure Gemini provider
    provider = GeminiProvider(model="gemini-1.5-flash")
    
    # Check if available
    if not provider.is_available():
        print("❌ Gemini not configured!")
        print("Set GEMINI_API_KEY or GOOGLE_API_KEY environment variable")
        print("Get your key at: https://makersuite.google.com/app/apikey")
        return
    
    print("✓ Gemini provider configured")
    print(f"  Model: {provider.model}")
    
    # Trace application
    print("\n📊 Running application with tracing...")
    with trace_scope() as graph:
        main_application()
    
    # Get AI summary using Gemini
    print("\n🤖 Generating AI summary with Gemini...")
    try:
        summary = summarize_trace(graph, provider=provider, include_recommendations=True)
        
        print("\n" + "-"*70)
        print("GEMINI AI SUMMARY:")
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


def demo_gemini_queries():
    """Demo 2: Natural Language Queries with Gemini"""
    print("\n" + "="*70)
    print("DEMO 2: Natural Language Queries with Google Gemini")
    print("="*70)
    
    # Configure Gemini
    provider = GeminiProvider(model="gemini-1.5-flash")
    
    if not provider.is_available():
        print("❌ Gemini not configured!")
        return
    
    print("✓ Gemini provider configured")
    
    # Trace application
    print("\n📊 Running application...")
    with trace_scope() as graph:
        main_application()
    
    # Ask questions using Gemini
    questions = [
        "Which function is the slowest?",
        "How can I optimize this code?",
        "What's causing the performance bottleneck?",
        "Show me database-related functions",
    ]
    
    print("\n🤖 Asking Gemini about the trace...\n")
    
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


def demo_gemini_comparison():
    """Demo 3: Compare Gemini with other models"""
    print("\n" + "="*70)
    print("DEMO 3: Gemini Model Comparison")
    print("="*70)
    
    # Test different Gemini models
    models = [
        "gemini-1.5-flash",      # Fast and efficient
        "gemini-1.5-pro",        # More capable
    ]
    
    print("\n📊 Running application...")
    with trace_scope() as graph:
        main_application()
    
    print("\n🤖 Testing different Gemini models...\n")
    
    for model in models:
        print("-"*70)
        print(f"Model: {model}")
        print("-"*70)
        
        try:
            provider = GeminiProvider(model=model)
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


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║        CallFlow Tracer - Google Gemini Integration Demo             ║
║                                                                      ║
║  This demo shows how to use Google's Gemini AI model for            ║
║  intelligent trace analysis and natural language queries.           ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        demo_gemini_summarization()
        demo_gemini_queries()
        demo_gemini_comparison()
        
        print("\n" + "="*70)
        print("✅ All demos completed!")
        print("="*70)
        print("\nWhy use Gemini?")
        print("• Fast response times")
        print("• Cost-effective")
        print("• Good quality analysis")
        print("• Free tier available")
        print("\nGet your API key: https://makersuite.google.com/app/apikey")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted")
    except Exception as e:
        print(f"\n\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
