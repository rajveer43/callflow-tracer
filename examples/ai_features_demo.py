"""
Demo of AI-powered features in CallFlow Tracer.

This example demonstrates:
1. Trace Summarization - Get AI-powered insights about your execution
2. Natural Language Queries - Ask questions about your traces in plain English

Requirements:
    pip install openai  # or anthropic, google-generativeai, or run ollama locally
    
Setup:
    export OPENAI_API_KEY="your-key-here"
    # OR
    export ANTHROPIC_API_KEY="your-key-here"
    # OR
    export GEMINI_API_KEY="your-key-here"  # or GOOGLE_API_KEY
    # OR
    ollama pull llama3.1  # for local LLM
"""

import time
import random
from callflow_tracer import trace_scope
from callflow_tracer.ai import summarize_trace, query_trace


# Example application with various performance characteristics
def slow_database_query(user_id):
    """Simulates a slow database query."""
    time.sleep(0.15)
    return {"id": user_id, "name": f"User{user_id}"}


def fast_cache_lookup(key):
    """Simulates a fast cache lookup."""
    time.sleep(0.001)
    return f"cached_value_{key}"


def process_user_data(user_id):
    """Process user data with mixed operations."""
    # Check cache first
    cached = fast_cache_lookup(f"user_{user_id}")
    
    if not cached:
        # Cache miss - query database
        user = slow_database_query(user_id)
        return user
    
    return cached


def calculate_statistics(data):
    """CPU-intensive calculation."""
    time.sleep(0.05)
    return sum(data) / len(data) if data else 0


def main_application():
    """Main application entry point."""
    print("Starting application...")
    
    # Process multiple users
    for i in range(5):
        user_data = process_user_data(i)
        print(f"Processed: {user_data}")
    
    # Do some calculations
    data = [random.randint(1, 100) for _ in range(1000)]
    result = calculate_statistics(data)
    print(f"Statistics result: {result}")
    
    print("Application complete!")


def demo_trace_summarization():
    """Demo 1: AI-Powered Trace Summarization"""
    print("\n" + "="*70)
    print("DEMO 1: AI-Powered Trace Summarization")
    print("="*70)
    
    # Trace the application
    print("\n📊 Running application with tracing...")
    with trace_scope() as graph:
        main_application()
    
    print("\n🤖 Generating AI summary...")
    try:
        summary = summarize_trace(graph, include_recommendations=True)
        
        print("\n" + "-"*70)
        print("AI SUMMARY:")
        print("-"*70)
        print(summary['summary'])
        
        print("\n" + "-"*70)
        print("STATISTICS:")
        print("-"*70)
        stats = summary['statistics']
        print(f"Total execution time: {stats['total_time']}s")
        print(f"Total functions: {stats['total_functions']}")
        print(f"Total calls: {stats['total_calls']}")
        print(f"Max call depth: {stats['max_depth']}")
        
        print("\n" + "-"*70)
        print("TOP BOTTLENECKS:")
        print("-"*70)
        for i, bottleneck in enumerate(summary['bottlenecks'], 1):
            print(f"{i}. {bottleneck['function']}")
            print(f"   Time: {bottleneck['total_time']}s ({bottleneck['percentage']}%)")
            print(f"   Calls: {bottleneck['call_count']}x, Avg: {bottleneck['avg_time']}s")
            print()
        
    except ImportError as e:
        print(f"\n⚠️  AI features not available: {e}")
        print("Install with: pip install openai")
    except Exception as e:
        print(f"\n❌ Error: {e}")


def demo_natural_language_queries():
    """Demo 2: Natural Language Query Interface"""
    print("\n" + "="*70)
    print("DEMO 2: Natural Language Query Interface")
    print("="*70)
    
    # Trace the application
    print("\n📊 Running application with tracing...")
    with trace_scope() as graph:
        main_application()
    
    # List of example queries
    queries = [
        "Which functions are the slowest?",
        "Show me the top 3 most called functions",
        "What functions do database operations?",
        "How many times was each function called?",
        "What is the total execution time?",
        "Show me functions with 'user' in the name",
    ]
    
    print("\n🤖 Asking questions about the trace...\n")
    
    try:
        for i, question in enumerate(queries, 1):
            print("-"*70)
            print(f"Q{i}: {question}")
            print("-"*70)
            
            result = query_trace(graph, question, use_llm=False)  # Use pattern matching
            print(result['answer'])
            print()
        
        # Try an LLM-powered query
        print("-"*70)
        print("Q: Why is this application slow? (LLM-powered)")
        print("-"*70)
        try:
            result = query_trace(graph, "Why is this application slow?", use_llm=True)
            print(result['answer'])
        except Exception as e:
            print(f"LLM query failed: {e}")
            print("(This requires an LLM provider to be configured)")
        
    except ImportError as e:
        print(f"\n⚠️  AI features not available: {e}")
        print("Install with: pip install openai")
    except Exception as e:
        print(f"\n❌ Error: {e}")


def demo_custom_provider():
    """Demo 3: Using Different LLM Providers"""
    print("\n" + "="*70)
    print("DEMO 3: Using Different LLM Providers")
    print("="*70)
    
    from callflow_tracer.ai import OpenAIProvider, AnthropicProvider, GeminiProvider, OllamaProvider
    
    print("\n📋 Available providers:")
    print("1. OpenAI (GPT-4) - Requires OPENAI_API_KEY")
    print("2. Anthropic (Claude) - Requires ANTHROPIC_API_KEY")
    print("3. Google Gemini - Requires GEMINI_API_KEY or GOOGLE_API_KEY")
    print("4. Ollama (Local) - Requires Ollama running locally")
    
    # Check which providers are available
    providers = {
        "OpenAI": OpenAIProvider(),
        "Anthropic": AnthropicProvider(),
        "Google Gemini": GeminiProvider(),
        "Ollama": OllamaProvider()
    }
    
    print("\n✅ Provider availability:")
    for name, provider in providers.items():
        status = "✓ Available" if provider.is_available() else "✗ Not configured"
        print(f"   {name}: {status}")
    
    # Trace application
    with trace_scope() as graph:
        main_application()
    
    # Try each available provider
    print("\n🤖 Testing available providers...")
    for name, provider in providers.items():
        if provider.is_available():
            print(f"\n--- Using {name} ---")
            try:
                summary = summarize_trace(graph, provider=provider)
                print(summary['summary'][:200] + "...")  # Show first 200 chars
            except Exception as e:
                print(f"Error with {name}: {e}")


def demo_advanced_queries():
    """Demo 4: Advanced Query Patterns"""
    print("\n" + "="*70)
    print("DEMO 4: Advanced Query Patterns")
    print("="*70)
    
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
            process_user_data(i)
        
        result = recursive_fibonacci(8)
        data = io_operation()
        
        return result
    
    print("\n📊 Running complex application...")
    with trace_scope() as graph:
        complex_app()
    
    # Advanced queries
    advanced_queries = [
        "Show me recursive functions",
        "What functions do I/O operations?",
        "Which function has the highest average execution time?",
        "Show functions in the __main__ module",
    ]
    
    print("\n🔍 Advanced queries:\n")
    try:
        for question in advanced_queries:
            print("-"*70)
            print(f"Q: {question}")
            print("-"*70)
            result = query_trace(graph, question, use_llm=False)
            print(result['answer'])
            print()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║           CallFlow Tracer - AI Features Demo                        ║
║                                                                      ║
║  This demo showcases AI-powered trace analysis and natural          ║
║  language query capabilities.                                       ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    # Run all demos
    try:
        demo_trace_summarization()
        demo_natural_language_queries()
        demo_custom_provider()
        demo_advanced_queries()
        
        print("\n" + "="*70)
        print("✅ All demos completed!")
        print("="*70)
        print("\nNext steps:")
        print("1. Configure an LLM provider (OpenAI, Anthropic, or Ollama)")
        print("2. Try your own queries with query_trace()")
        print("3. Integrate AI summaries into your CI/CD pipeline")
        print("4. Explore the API documentation for more features")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
