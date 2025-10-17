# AI Features Documentation

CallFlow Tracer includes powerful AI-driven features for intelligent trace analysis and natural language interaction.

## 🚀 Quick Start

### Installation

Install CallFlow Tracer with AI support:

```bash
pip install callflow-tracer

# Install LLM provider (choose one):
pip install openai                 # For OpenAI GPT
pip install anthropic              # For Anthropic Claude
pip install google-generativeai    # For Google Gemini
pip install requests               # For Ollama (local)
```

### Configuration

Set up your LLM provider:

```bash
# Option 1: OpenAI
export OPENAI_API_KEY="your-key-here"

# Option 2: Anthropic
export ANTHROPIC_API_KEY="your-key-here"

# Option 3: Google Gemini
export GEMINI_API_KEY="your-key-here"
# OR
export GOOGLE_API_KEY="your-key-here"

# Option 4: Ollama (local, no API key needed)
ollama pull llama3.1
```

## 📊 Feature 1: Trace Summarization

Get AI-powered insights about your execution traces.

### Basic Usage

```python
from callflow_tracer import trace_scope
from callflow_tracer.ai import summarize_trace

# Trace your application
with trace_scope() as graph:
    your_application()

# Get AI summary
summary = summarize_trace(graph)
print(summary['summary'])
```

### Output Example

```
Execution Summary:

Your application executed in 2.34s across 15 functions with 127 total calls.

Key Findings:
• Main bottleneck: database_query() consumed 1.85s (79% of total time)
• High call frequency: cache_lookup() was called 45 times
• Optimization opportunity: Consider batching database queries

Recommendations:
1. Implement query batching for database_query() to reduce round trips
2. Add caching layer for frequently accessed data
3. Consider async operations for I/O-bound functions
```

### Advanced Options

```python
summary = summarize_trace(
    graph,
    include_recommendations=True,  # Include optimization tips
    include_bottlenecks=True,      # Analyze bottlenecks
    max_bottlenecks=5              # Number of bottlenecks to analyze
)

# Access detailed data
print(f"Total time: {summary['total_execution_time']}s")
print(f"Functions: {summary['total_functions']}")

for bottleneck in summary['bottlenecks']:
    print(f"{bottleneck['function']}: {bottleneck['total_time']}s")
```

### Custom LLM Provider

```python
from callflow_tracer.ai import OpenAIProvider, AnthropicProvider, GeminiProvider, OllamaProvider

# Use specific provider
provider = OpenAIProvider(model="gpt-4o")
summary = summarize_trace(graph, provider=provider)

# Or use Anthropic
provider = AnthropicProvider(model="claude-3-5-sonnet-20241022")
summary = summarize_trace(graph, provider=provider)

# Or use Google Gemini
provider = GeminiProvider(model="gemini-1.5-flash")
summary = summarize_trace(graph, provider=provider)

# Or use local Ollama
provider = OllamaProvider(model="llama3.1")
summary = summarize_trace(graph, provider=provider)
```

## 🔍 Feature 2: Natural Language Queries

Ask questions about your traces in plain English.

### Basic Usage

```python
from callflow_tracer import trace_scope
from callflow_tracer.ai import query_trace

with trace_scope() as graph:
    your_application()

# Ask questions
result = query_trace(graph, "Which functions are slowest?")
print(result['answer'])
```

### Example Queries

#### Performance Questions
```python
# Find slow functions
query_trace(graph, "Which functions are slowest?")
query_trace(graph, "Show me the top 5 bottlenecks")
query_trace(graph, "What's taking the most time?")

# Find fast functions
query_trace(graph, "Which functions are fastest?")
```

#### Call Frequency Questions
```python
# Most called
query_trace(graph, "Which functions are called most often?")
query_trace(graph, "Show me the top 10 most called functions")

# Least called
query_trace(graph, "Which functions are rarely called?")
```

#### Domain-Specific Questions
```python
# Database operations
query_trace(graph, "Show me database functions")
query_trace(graph, "What functions query the database?")

# I/O operations
query_trace(graph, "Which functions do I/O?")
query_trace(graph, "Show me file operations")

# Recursive functions
query_trace(graph, "Are there any recursive functions?")
```

#### Module/Package Questions
```python
# By module
query_trace(graph, "Show functions in module myapp.api")
query_trace(graph, "What functions are in the database package?")
```

#### Statistics Questions
```python
# Overall stats
query_trace(graph, "What is the total execution time?")
query_trace(graph, "How many function calls were made?")
query_trace(graph, "What's the average time per function?")
```

### Advanced Queries with LLM

For complex questions, enable LLM mode:

```python
# Complex analysis
result = query_trace(
    graph, 
    "Why is my checkout flow slow?",
    use_llm=True  # Use AI for complex queries
)
print(result['answer'])

# Pattern detection
result = query_trace(
    graph,
    "Are there any N+1 query patterns?",
    use_llm=True
)
```

### Query Response Structure

```python
result = query_trace(graph, "Which functions are slowest?")

# Access different parts
print(result['question'])    # Original question
print(result['answer'])      # Natural language answer
print(result['data'])        # Structured data (if available)
print(result['query_type'])  # Type of query executed
```

## 🎛️ LLM Provider Configuration

### Provider Classes

```python
from callflow_tracer.ai import (
    LLMProvider,
    OpenAIProvider,
    AnthropicProvider,
    GeminiProvider,
    OllamaProvider
)
```

### OpenAI Configuration

```python
provider = OpenAIProvider(
    api_key="your-key",      # Or use OPENAI_API_KEY env var
    model="gpt-4o-mini"      # or "gpt-4o", "gpt-4-turbo"
)
```

### Anthropic Configuration

```python
provider = AnthropicProvider(
    api_key="your-key",                    # Or use ANTHROPIC_API_KEY env var
    model="claude-3-5-sonnet-20241022"     # or other Claude models
)
```

### Google Gemini Configuration

```python
provider = GeminiProvider(
    api_key="your-key",           # Or use GEMINI_API_KEY or GOOGLE_API_KEY env var
    model="gemini-1.5-flash"      # or "gemini-1.5-pro", "gemini-pro"
)
```

### Ollama Configuration (Local)

```python
provider = OllamaProvider(
    model="llama3.1",                # or "mistral", "codellama", etc.
    base_url="http://localhost:11434"  # Ollama server URL
)
```

### Auto-Detection

The library automatically detects available providers:

```python
from callflow_tracer.ai import get_default_provider

# Tries OpenAI, then Anthropic, then Gemini, then Ollama
provider = get_default_provider()

# Or specify explicitly
provider = get_default_provider("openai")
provider = get_default_provider("anthropic")
provider = get_default_provider("gemini")  # or "google"
provider = get_default_provider("ollama")
```

## 🔧 Advanced Usage

### Custom Summarizer

```python
from callflow_tracer.ai import TraceSummarizer

summarizer = TraceSummarizer(provider=your_provider)

# Customize summary
summary = summarizer.summarize(
    graph,
    include_recommendations=True,
    include_bottlenecks=True,
    max_bottlenecks=10
)
```

### Custom Query Engine

```python
from callflow_tracer.ai import QueryEngine

engine = QueryEngine(provider=your_provider)

# Multiple queries
questions = [
    "Which functions are slowest?",
    "Show database operations",
    "What's the total time?"
]

for question in questions:
    result = engine.query(graph, question)
    print(f"Q: {question}")
    print(f"A: {result['answer']}\n")
```

### Batch Processing

```python
# Process multiple traces
traces = []
for i in range(10):
    with trace_scope() as graph:
        run_test_case(i)
        traces.append(graph)

# Summarize all
for i, graph in enumerate(traces):
    summary = summarize_trace(graph)
    print(f"Test {i}: {summary['total_execution_time']}s")
```

## 💡 Use Cases

### 1. CI/CD Integration

```python
# In your test suite
def test_performance():
    with trace_scope() as graph:
        run_application()
    
    summary = summarize_trace(graph)
    
    # Check performance
    assert summary['total_execution_time'] < 5.0, \
        f"Too slow: {summary['summary']}"
```

### 2. Performance Monitoring

```python
# Regular performance checks
import schedule

def check_performance():
    with trace_scope() as graph:
        health_check()
    
    summary = summarize_trace(graph)
    if summary['total_execution_time'] > threshold:
        alert_team(summary['summary'])

schedule.every(1).hour.do(check_performance)
```

### 3. Interactive Debugging

```python
# Debug session
with trace_scope() as graph:
    problematic_function()

# Ask questions interactively
while True:
    question = input("Ask about the trace: ")
    if question == "quit":
        break
    result = query_trace(graph, question)
    print(result['answer'])
```

### 4. Documentation Generation

```python
# Generate performance docs
with trace_scope() as graph:
    main_workflow()

summary = summarize_trace(graph)

with open("PERFORMANCE.md", "w") as f:
    f.write("# Performance Analysis\n\n")
    f.write(summary['summary'])
    f.write("\n\n## Bottlenecks\n\n")
    for b in summary['bottlenecks']:
        f.write(f"- {b['function']}: {b['total_time']}s\n")
```

## 🚨 Error Handling

```python
from callflow_tracer.ai import summarize_trace, query_trace

try:
    summary = summarize_trace(graph)
except ImportError as e:
    print("AI features not available:", e)
    print("Install with: pip install openai")
except ValueError as e:
    print("LLM provider not configured:", e)
    print("Set OPENAI_API_KEY or ANTHROPIC_API_KEY")
except RuntimeError as e:
    print("LLM API error:", e)
```

## 📝 Best Practices

### 1. Choose the Right Provider

- **OpenAI GPT-4**: Best quality, most expensive
- **Anthropic Claude**: Great for code analysis, good balance
- **Google Gemini**: Fast, cost-effective, good quality
- **Ollama (Local)**: Free, private, requires local resources

### 2. Optimize Costs

```python
# Use cheaper models for simple queries
provider = OpenAIProvider(model="gpt-4o-mini")  # Cheaper than gpt-4

# Disable LLM for pattern-based queries
result = query_trace(graph, "slowest functions", use_llm=False)
```

### 3. Cache Results

```python
import json

# Cache summaries
summary = summarize_trace(graph)
with open("summary_cache.json", "w") as f:
    json.dump(summary, f)
```

### 4. Privacy Considerations

```python
# Traces may contain sensitive data
# Use local Ollama for sensitive applications
provider = OllamaProvider()  # Runs locally, no data sent to cloud
summary = summarize_trace(graph, provider=provider)
```

## 🔬 Examples

See `examples/ai_features_demo.py` for comprehensive examples including:
- Basic trace summarization
- Natural language queries
- Custom provider configuration
- Advanced query patterns
- Batch processing

Run the demo:
```bash
python examples/ai_features_demo.py
```

## 🐛 Troubleshooting

### "No LLM provider available"
- Install provider package: `pip install openai` or `pip install anthropic`
- Set API key: `export OPENAI_API_KEY="your-key"`
- Or run Ollama locally: `ollama pull llama3.1`

### "OpenAI API error: Rate limit"
- Reduce request frequency
- Use cheaper model (gpt-4o-mini)
- Switch to local Ollama

### "Query returns no results"
- Check if trace has data: `len(graph.nodes) > 0`
- Try different query phrasing
- Enable LLM mode: `use_llm=True`

## 📚 API Reference

### `summarize_trace(graph, provider=None, include_recommendations=True)`
Generate AI-powered summary of execution trace.

**Parameters:**
- `graph` (CallGraph): Trace to summarize
- `provider` (LLMProvider, optional): LLM provider to use
- `include_recommendations` (bool): Include optimization tips

**Returns:** Dict with summary, statistics, and bottlenecks

### `query_trace(graph, question, provider=None, use_llm=True)`
Query trace using natural language.

**Parameters:**
- `graph` (CallGraph): Trace to query
- `question` (str): Natural language question
- `provider` (LLMProvider, optional): LLM provider to use
- `use_llm` (bool): Use LLM for complex queries

**Returns:** Dict with question, answer, data, and query_type

## 🎯 Next Steps

1. Try the examples: `python examples/ai_features_demo.py`
2. Integrate into your workflow
3. Explore advanced features
4. Provide feedback and suggestions

For more information, see the [main README](../README.md) and [API documentation](API_DOCUMENTATION.md).
