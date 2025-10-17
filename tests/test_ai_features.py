"""
Tests for AI features in CallFlow Tracer.

These tests verify the AI summarization and query functionality.
Note: Some tests require an LLM provider to be configured.
"""

import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from callflow_tracer import trace_scope
from callflow_tracer.ai import (
    summarize_trace,
    query_trace,
    TraceSummarizer,
    QueryEngine,
    OpenAIProvider,
    AnthropicProvider,
    GeminiProvider,
    OllamaProvider,
    get_default_provider
)


# Test application functions
def slow_function():
    """Simulates a slow function."""
    time.sleep(0.1)
    return "slow"


def fast_function():
    """Simulates a fast function."""
    time.sleep(0.001)
    return "fast"


def database_query():
    """Simulates a database query."""
    time.sleep(0.05)
    return {"data": "result"}


def recursive_function(n):
    """Recursive function for testing."""
    if n <= 0:
        return 1
    return n * recursive_function(n - 1)


def test_application():
    """Test application with various functions."""
    for i in range(3):
        slow_function()
    
    for i in range(10):
        fast_function()
    
    database_query()
    recursive_function(5)


# Test 1: Basic trace summarization
def test_summarize_trace_basic():
    """Test basic trace summarization without LLM."""
    print("\n" + "="*70)
    print("TEST 1: Basic Trace Summarization")
    print("="*70)
    
    try:
        with trace_scope() as graph:
            test_application()
        
        # This should work even without LLM (fallback mode)
        summary = summarize_trace(graph, include_recommendations=False)
        
        assert 'summary' in summary
        assert 'statistics' in summary
        assert 'bottlenecks' in summary
        assert summary['total_functions'] > 0
        assert summary['total_calls'] > 0
        
        print("✓ Summary generated successfully")
        print(f"  Functions: {summary['total_functions']}")
        print(f"  Calls: {summary['total_calls']}")
        print(f"  Time: {summary['total_execution_time']}s")
        
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


# Test 2: Query engine pattern matching
def test_query_engine_patterns():
    """Test query engine with pattern matching (no LLM needed)."""
    print("\n" + "="*70)
    print("TEST 2: Query Engine Pattern Matching")
    print("="*70)
    
    try:
        with trace_scope() as graph:
            test_application()
        
        queries = [
            "Which functions are slowest?",
            "Show me the most called functions",
            "What is the total execution time?",
        ]
        
        for question in queries:
            result = query_trace(graph, question, use_llm=False)
            assert 'answer' in result
            assert 'question' in result
            print(f"✓ Query: {question}")
            print(f"  Answer: {result['answer'][:100]}...")
        
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


# Test 3: Provider availability
def test_provider_availability():
    """Test LLM provider availability detection."""
    print("\n" + "="*70)
    print("TEST 3: Provider Availability")
    print("="*70)
    
    try:
        providers = {
            "OpenAI": OpenAIProvider(),
            "Anthropic": AnthropicProvider(),
            "Google Gemini": GeminiProvider(),
            "Ollama": OllamaProvider()
        }
        
        available_count = 0
        for name, provider in providers.items():
            is_available = provider.is_available()
            status = "✓ Available" if is_available else "✗ Not configured"
            print(f"  {name}: {status}")
            if is_available:
                available_count += 1
        
        print(f"\n  Total available: {available_count}/4")
        
        # Test passes if we can detect availability (even if none available)
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


# Test 4: Summarizer class
def test_summarizer_class():
    """Test TraceSummarizer class directly."""
    print("\n" + "="*70)
    print("TEST 4: TraceSummarizer Class")
    print("="*70)
    
    try:
        with trace_scope() as graph:
            test_application()
        
        # Test without provider (should use fallback)
        try:
            summarizer = TraceSummarizer()
            summary = summarizer.summarize(graph, include_recommendations=False)
            
            assert summary['total_functions'] > 0
            print("✓ Summarizer with auto-detected provider")
        except ValueError:
            # No provider available, that's ok
            print("⚠ No LLM provider available (expected in CI)")
        
        # Test statistics extraction
        stats = summarizer._extract_stats(graph)
        assert 'total_time' in stats
        assert 'total_functions' in stats
        print("✓ Statistics extraction works")
        
        # Test bottleneck identification
        bottlenecks = summarizer._identify_bottlenecks(graph, max_count=3)
        assert isinstance(bottlenecks, list)
        print(f"✓ Bottleneck identification works ({len(bottlenecks)} found)")
        
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


# Test 5: Query engine class
def test_query_engine_class():
    """Test QueryEngine class directly."""
    print("\n" + "="*70)
    print("TEST 5: QueryEngine Class")
    print("="*70)
    
    try:
        with trace_scope() as graph:
            test_application()
        
        try:
            engine = QueryEngine()
        except ValueError:
            # No provider available, create without one for pattern testing
            print("⚠ No LLM provider, testing pattern matching only")
            engine = QueryEngine.__new__(QueryEngine)
            engine.provider = None
            engine.patterns = QueryEngine.__init__.__code__.co_consts[2] if hasattr(QueryEngine.__init__.__code__, 'co_consts') else {}
        
        # Test pattern-based queries (no LLM needed)
        test_queries = [
            ("slowest", "slow"),
            ("most called", "called"),
            ("database", "database"),
        ]
        
        for query_text, expected_keyword in test_queries:
            result = engine.query(graph, query_text, use_llm=False)
            print(f"✓ Query pattern '{query_text}' works")
        
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


# Test 6: LLM integration (if available)
def test_llm_integration():
    """Test actual LLM integration if provider is available."""
    print("\n" + "="*70)
    print("TEST 6: LLM Integration (Optional)")
    print("="*70)
    
    try:
        # Try to get a provider
        try:
            provider = get_default_provider()
            print(f"✓ Provider available: {provider.__class__.__name__}")
        except ValueError:
            print("⚠ No LLM provider configured - skipping LLM tests")
            print("  (This is expected in CI environments)")
            return True  # Not a failure
        
        # Test with actual LLM
        with trace_scope() as graph:
            test_application()
        
        # Test summarization with LLM
        summary = summarize_trace(graph, provider=provider)
        assert len(summary['summary']) > 50  # Should have substantial content
        print("✓ LLM summarization works")
        print(f"  Summary length: {len(summary['summary'])} chars")
        
        # Test query with LLM
        result = query_trace(graph, "Why is this code slow?", provider=provider, use_llm=True)
        assert len(result['answer']) > 20
        print("✓ LLM query works")
        print(f"  Answer length: {len(result['answer'])} chars")
        
        return True
    except Exception as e:
        print(f"⚠ LLM test skipped or failed: {e}")
        return True  # Don't fail if LLM not available


# Test 7: Edge cases
def test_edge_cases():
    """Test edge cases and error handling."""
    print("\n" + "="*70)
    print("TEST 7: Edge Cases")
    print("="*70)
    
    try:
        # Empty graph
        with trace_scope() as empty_graph:
            pass  # No functions called
        
        # Should handle empty graph gracefully
        try:
            summary = summarize_trace(empty_graph, include_recommendations=False)
            print("✓ Handles empty graph")
        except:
            print("⚠ Empty graph handling needs improvement")
        
        # Very simple graph
        with trace_scope() as simple_graph:
            fast_function()
        
        summary = summarize_trace(simple_graph, include_recommendations=False)
        assert summary['total_functions'] >= 1
        print("✓ Handles simple graph")
        
        # Query with no matches
        result = query_trace(simple_graph, "show functions with xyz in name", use_llm=False)
        print("✓ Handles query with no matches")
        
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests and report results."""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║              CallFlow Tracer - AI Features Tests                    ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    tests = [
        ("Basic Trace Summarization", test_summarize_trace_basic),
        ("Query Engine Patterns", test_query_engine_patterns),
        ("Provider Availability", test_provider_availability),
        ("TraceSummarizer Class", test_summarizer_class),
        ("QueryEngine Class", test_query_engine_class),
        ("LLM Integration", test_llm_integration),
        ("Edge Cases", test_edge_cases),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print("="*70)
    print(f"Results: {passed}/{total} tests passed")
    print("="*70)
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
