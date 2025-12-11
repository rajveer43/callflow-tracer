# AI Enhancements Quick Start Guide

## 5-Minute Setup

### 1. Install Dependencies
```bash
pip install openai anthropic google-generativeai
```

### 2. Set API Keys
```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GEMINI_API_KEY="..."
```

### 3. Use Enhanced AI Features

#### Performance Analysis
```python
from callflow_tracer import trace_scope
from callflow_tracer.ai import OpenAIProvider, QueryEngine

with trace_scope() as graph:
    my_app()

provider = OpenAIProvider(model="gpt-4o")
engine = QueryEngine(provider=provider)

result = engine.query(graph, "What are the bottlenecks?")
print(result['answer'])
```

#### Root Cause Analysis
```python
from callflow_tracer.ai import AnthropicProvider, RootCauseAnalyzer

provider = AnthropicProvider(model="claude-3-opus-20240229")
analyzer = RootCauseAnalyzer(provider=provider)

analysis = analyzer.analyze(graph, issue_type="performance")
print(analysis['llm_insights'])
```

#### Auto-Fix Generation
```python
from callflow_tracer.ai import OpenAIProvider, AutoFixer

provider = OpenAIProvider(model="gpt-4-turbo")
fixer = AutoFixer(llm_provider=provider)

fixes = fixer.generate_fixes(graph, analysis)
for fix in fixes:
    print(f"{fix['issue']}: {fix['estimated_improvement']}% improvement")
```

---

## Model Comparison

| Model | Context | Speed | Cost | Best For |
|-------|---------|-------|------|----------|
| GPT-4 Turbo | 128K | Slow | $$ | Code generation |
| GPT-4o | 128K | Fast | $$ | Balanced |
| GPT-4o-mini | 128K | Fast | $ | Budget |
| Claude 3 Opus | 200K | Slow | $$ | Analysis |
| Claude 3.5 Sonnet | 200K | Fast | $$ | Latest |
| Gemini 1.5 Pro | 1M | Slow | $ | Large context |
| Gemini 1.5 Flash | 1M | Fast | $ | Speed |

---

## Common Tasks

### Task 1: Analyze Performance Issues
```python
from callflow_tracer.ai import OpenAIProvider, QueryEngine

provider = OpenAIProvider(model="gpt-4o")
engine = QueryEngine(provider=provider)

# Ask specific questions
questions = [
    "Which functions are slowest?",
    "What are the N+1 query patterns?",
    "Where should I add caching?",
]

for q in questions:
    result = engine.query(graph, q)
    print(f"Q: {q}")
    print(f"A: {result['answer']}\n")
```

### Task 2: Find Root Causes
```python
from callflow_tracer.ai import AnthropicProvider, RootCauseAnalyzer

provider = AnthropicProvider(model="claude-3-opus-20240229")
analyzer = RootCauseAnalyzer(provider=provider)

analysis = analyzer.analyze(graph, issue_type="performance")

print("Root Causes:")
for cause in analysis['root_causes']:
    print(f"  - {cause['function']}: {cause['total_impact_time']:.3f}s")

print("\nLLM Insights:")
print(analysis['llm_insights'])
```

### Task 3: Generate Fixes
```python
from callflow_tracer.ai import OpenAIProvider, AutoFixer

provider = OpenAIProvider(model="gpt-4-turbo")
fixer = AutoFixer(llm_provider=provider)

fixes = fixer.generate_fixes(graph, analysis, source_code)

for fix in fixes:
    print(f"Issue: {fix['issue']}")
    print(f"Confidence: {fix['confidence']:.0%}")
    print(f"Expected Improvement: {fix['estimated_improvement']:.0f}%")
    print(f"Diff:\n{fix['diff']}\n")
```

### Task 4: Detect Anomalies
```python
from callflow_tracer.ai import AnomalyDetector

detector = AnomalyDetector(sensitivity=2.0)
anomalies = detector.detect(graph)

print(f"Found {anomalies['severity_summary']['total']} anomalies:")
for anomaly in anomalies['time_anomalies']:
    print(f"  - {anomaly['function']}: {anomaly['deviation']:.3f}s deviation")

print("\nRecommendations:")
for rec in anomalies['recommendations']:
    print(f"  - {rec}")
```

---

## Retry Logic

Automatic retries with exponential backoff:

```python
provider = OpenAIProvider(
    model="gpt-4o",
    max_retries=5,      # Number of retries
    retry_delay=2.0     # Initial delay in seconds
)

# Automatically retries on:
# - Rate limiting (429)
# - Server errors (5xx)
# - Timeout errors
# - Connection errors
```

---

## Temperature Settings

```python
# For precise analysis (lower = more focused)
provider.generate(prompt, temperature=0.2)

# For balanced output
provider.generate(prompt, temperature=0.5)

# For creative suggestions (higher = more varied)
provider.generate(prompt, temperature=0.7)
```

---

## Troubleshooting

### "API key not configured"
```python
import os
# Check key is set
print(os.getenv("OPENAI_API_KEY"))

# Or pass directly
provider = OpenAIProvider(api_key="sk-...")
```

### "Rate limit exceeded"
```python
provider = OpenAIProvider(
    model="gpt-4o",
    max_retries=10,     # Increase retries
    retry_delay=5.0     # Increase delay
)
```

### "Context window exceeded"
```python
# Use larger context model
provider = GeminiProvider(model="gemini-1.5-pro")
```

---

## Next Steps

1. **Read Full Guide**: See `AI_ENHANCEMENTS_GUIDE.md`
2. **Check Examples**: See `examples/` directory
3. **Review Implementation**: See `IMPLEMENTATION_SUMMARY.md`
4. **Explore Prompts**: See `callflow_tracer/ai/prompts.py`

---

## Quick Reference

### Imports
```python
from callflow_tracer.ai import (
    OpenAIProvider,
    AnthropicProvider,
    GeminiProvider,
    OllamaProvider,
    get_prompt_for_task,
    QueryEngine,
    RootCauseAnalyzer,
    AutoFixer,
    AnomalyDetector,
)
```

### Providers
```python
# OpenAI
OpenAIProvider(model="gpt-4-turbo")
OpenAIProvider(model="gpt-4o")
OpenAIProvider(model="gpt-4o-mini")

# Anthropic
AnthropicProvider(model="claude-3-opus-20240229")
AnthropicProvider(model="claude-3-5-sonnet-20241022")

# Google
GeminiProvider(model="gemini-1.5-pro")
GeminiProvider(model="gemini-1.5-flash")

# Local
OllamaProvider(model="llama3.1")
```

### Prompt Tasks
```python
get_prompt_for_task('performance_analysis', ...)
get_prompt_for_task('root_cause_analysis', ...)
get_prompt_for_task('code_fix', ...)
get_prompt_for_task('anomaly_analysis', ...)
get_prompt_for_task('security_analysis', ...)
get_prompt_for_task('refactoring', ...)
get_prompt_for_task('test_generation', ...)
get_prompt_for_task('documentation', ...)
```

---

**Version**: 0.4.0  
**Status**: Production Ready  
**Last Updated**: 2024-12-06
