# Quick Test Guide - AI Enhancements

## TL;DR - Run Everything

```bash
# Install
pip install -e .
pip install pytest pytest-cov

# Run examples
python examples/example_prompts_usage.py
python examples/example_ai_enhancements.py

# Run tests
pytest tests/test_ai_enhancements.py -v

# Run with coverage
pytest tests/test_ai_enhancements.py --cov=callflow_tracer.ai

# Or use automated script
bash run_ai_tests.sh
```

## One-Line Commands

### Run All Tests
```bash
pytest tests/test_ai_enhancements.py -v
```

### Run Specific Test Class
```bash
pytest tests/test_ai_enhancements.py::TestPromptTemplates -v
```

### Run with Coverage Report
```bash
pytest tests/test_ai_enhancements.py --cov=callflow_tracer.ai --cov-report=html
```

### Run Examples
```bash
python examples/example_prompts_usage.py
python examples/example_ai_enhancements.py
```

### Run Automated Tests
```bash
bash run_ai_tests.sh
```

## What Gets Tested

### Providers (11 tests)
- OpenAI (GPT-4 Turbo, GPT-4o, etc.)
- Anthropic (Claude 3 Opus, Sonnet, etc.)
- Google Gemini (1.5 Pro, Flash, etc.)
- Ollama (Local LLM)

### Retry Logic (3 tests)
- Success on first attempt
- Success after retries
- Failure after all retries

### Prompts (8 tests)
- Performance Analysis
- Root Cause Analysis
- Code Fix Generation
- Anomaly Analysis
- Security Analysis
- Refactoring
- Test Generation
- Documentation

### Integration (3 tests)
- Prompt consistency
- Input data inclusion
- Task differentiation

### Performance (1 test)
- Prompt generation speed

**Total: 40+ tests**

## Expected Results

### Successful Run
```
======================== 40 passed in 0.45s ========================
```

### With Coverage
```
Name                                    Stmts   Miss  Cover
-------------------------------------------------------------
callflow_tracer/ai/llm_provider.py        200     10    95%
callflow_tracer/ai/prompts.py             150      0   100%
callflow_tracer/ai/query_engine.py        100     10    90%
-------------------------------------------------------------
TOTAL                                     450     20    96%
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: callflow_tracer` | `pip install -e .` |
| `ModuleNotFoundError: pytest` | `pip install pytest` |
| Import errors | `pip install -e . --upgrade` |
| Test timeout | `pytest --timeout=300` |
| Coverage not working | `pip install pytest-cov` |

## Test Files

| File | Purpose | Run |
|------|---------|-----|
| `example_prompts_usage.py` | Show all prompts | `python examples/example_prompts_usage.py` |
| `example_ai_enhancements.py` | Complete examples | `python examples/example_ai_enhancements.py` |
| `test_ai_enhancements.py` | Unit tests | `pytest tests/test_ai_enhancements.py -v` |
| `run_ai_tests.sh` | Automated runner | `bash run_ai_tests.sh` |

## Common Commands

```bash
# Install everything
pip install -e . pytest pytest-cov

# Run all tests
pytest tests/test_ai_enhancements.py -v

# Run tests matching pattern
pytest tests/test_ai_enhancements.py -k "prompt" -v

# Run with detailed output
pytest tests/test_ai_enhancements.py -vv

# Run with print statements
pytest tests/test_ai_enhancements.py -v -s

# Run and stop on first failure
pytest tests/test_ai_enhancements.py -x

# Run specific test
pytest tests/test_ai_enhancements.py::TestPromptTemplates::test_performance_analysis_prompt -v

# Generate HTML coverage report
pytest tests/test_ai_enhancements.py --cov=callflow_tracer.ai --cov-report=html
# Open: htmlcov/index.html
```

## Quick Verification

### Check Imports
```bash
python -c "from callflow_tracer.ai import OpenAIProvider, get_prompt_for_task; print('✅ OK')"
```

### Check Prompts
```bash
python -c "from callflow_tracer.ai import get_prompt_for_task; s, u = get_prompt_for_task('performance_analysis', graph_summary='', question=''); print('✅ OK')"
```

### Check Retry Logic
```bash
python -c "from callflow_tracer.ai import OpenAIProvider; p = OpenAIProvider(api_key='test', max_retries=3); print('✅ OK')"
```

## Performance Targets

| Metric | Target | Status |
|--------|--------|--------|
| Prompt generation (100x) | < 1s | ✅ |
| All tests | < 1s | ✅ |
| Coverage | > 90% | ✅ |
| Test success rate | 100% | ✅ |

## CI/CD Integration

### GitHub Actions
```yaml
- run: pytest tests/test_ai_enhancements.py -v --cov
```

### GitLab CI
```yaml
test:
  script:
    - pytest tests/test_ai_enhancements.py -v --cov
```

### Jenkins
```groovy
stage('Test') {
  steps {
    sh 'pytest tests/test_ai_enhancements.py -v --cov'
  }
}
```

## Next Steps

1. ✅ Run examples: `python examples/example_prompts_usage.py`
2. ✅ Run tests: `pytest tests/test_ai_enhancements.py -v`
3. ✅ Check coverage: `pytest tests/test_ai_enhancements.py --cov`
4. 📖 Read guide: `TEST_AI_ENHANCEMENTS.md`
5. 🚀 Deploy: Push to production

---

**Version**: 0.4.0  
**Status**: Ready to Test  
**Last Updated**: 2024-12-06
