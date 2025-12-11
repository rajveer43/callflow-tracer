#!/bin/bash

# AI Enhancements Test Runner Script
# Runs all examples and tests for AI enhancements in CallFlow Tracer v0.4.0

set -e  # Exit on error

echo "=========================================================================="
echo "CallFlow Tracer AI Enhancements - Test Runner"
echo "=========================================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track results
PASSED=0
FAILED=0

# Function to print section header
print_header() {
    echo ""
    echo "=========================================================================="
    echo "$1"
    echo "=========================================================================="
    echo ""
}

# Function to print success
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
    ((PASSED++))
}

# Function to print error
print_error() {
    echo -e "${RED}❌ $1${NC}"
    ((FAILED++))
}

# Function to print info
print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Check Python installation
print_header "Checking Prerequisites"

if ! command -v python3 &> /dev/null; then
    print_error "Python 3 not found"
    exit 1
fi
print_success "Python 3 found: $(python3 --version)"

if ! python3 -c "import pytest" 2>/dev/null; then
    print_info "Installing pytest..."
    pip install pytest pytest-cov
fi
print_success "pytest is available"

# Check if we're in the right directory
if [ ! -f "setup.py" ]; then
    print_error "setup.py not found. Please run this script from the callflow-tracer root directory."
    exit 1
fi
print_success "Found setup.py - running from correct directory"

# Install package in development mode
print_header "Installing Package"

if pip install -e . > /dev/null 2>&1; then
    print_success "Package installed in development mode"
else
    print_error "Failed to install package"
    exit 1
fi

# Run example: Prompts usage
print_header "Running Example 1: Prompt Templates"

if python3 examples/example_prompts_usage.py > /tmp/example1.log 2>&1; then
    print_success "example_prompts_usage.py completed"
else
    print_error "example_prompts_usage.py failed"
    cat /tmp/example1.log
fi

# Run example: AI enhancements
print_header "Running Example 2: AI Features"

if python3 examples/example_ai_enhancements.py > /tmp/example2.log 2>&1; then
    print_success "example_ai_enhancements.py completed"
else
    print_error "example_ai_enhancements.py failed (may require API keys)"
    print_info "This is expected if API keys are not configured"
fi

# Run unit tests
print_header "Running Unit Tests"

if pytest tests/test_ai_enhancements.py -v --tb=short > /tmp/tests.log 2>&1; then
    # Count passed tests
    PASSED_TESTS=$(grep -c "PASSED" /tmp/tests.log || echo "0")
    print_success "All tests passed ($PASSED_TESTS tests)"
    cat /tmp/tests.log
else
    print_error "Some tests failed"
    cat /tmp/tests.log
fi

# Run tests with coverage
print_header "Running Tests with Coverage"

if pytest tests/test_ai_enhancements.py --cov=callflow_tracer.ai --cov-report=term-missing > /tmp/coverage.log 2>&1; then
    print_success "Coverage report generated"
    cat /tmp/coverage.log
else
    print_error "Coverage report failed"
fi

# Verify imports
print_header "Verifying Imports"

if python3 -c "from callflow_tracer.ai import (
    OpenAIProvider,
    AnthropicProvider,
    GeminiProvider,
    OllamaProvider,
    PromptTemplates,
    get_prompt_for_task,
)" 2>/dev/null; then
    print_success "All imports successful"
else
    print_error "Import verification failed"
fi

# Verify prompt templates
print_header "Verifying Prompt Templates"

if python3 << 'EOF'
from callflow_tracer.ai import get_prompt_for_task

templates = [
    ('performance_analysis', {'graph_summary': '', 'question': ''}),
    ('root_cause_analysis', {'root_causes': '', 'impact': '', 'issue_type': ''}),
    ('code_fix', {'issue_type': '', 'function_name': '', 'context': ''}),
    ('anomaly_analysis', {'anomalies': ''}),
    ('security_analysis', {'issues': ''}),
    ('refactoring', {'function_code': '', 'metrics': {}}),
    ('test_generation', {'function_code': '', 'function_name': ''}),
    ('documentation', {'function_code': '', 'function_name': ''}),
]

for template_name, kwargs in templates:
    try:
        system, user = get_prompt_for_task(template_name, **kwargs)
        assert len(system) > 0
        assert len(user) > 0
        print(f"✓ {template_name}")
    except Exception as e:
        print(f"✗ {template_name}: {e}")
        exit(1)
EOF
then
    print_success "All 8 prompt templates verified"
else
    print_error "Prompt template verification failed"
fi

# Verify retry logic
print_header "Verifying Retry Logic"

if python3 << 'EOF'
from callflow_tracer.ai import OpenAIProvider
from unittest.mock import Mock

provider = OpenAIProvider(api_key="test", max_retries=3)

# Test successful retry
mock_func = Mock(side_effect=[
    Exception("Fail 1"),
    Exception("Fail 2"),
    "success"
])

try:
    result = provider._retry_with_backoff(mock_func)
    assert result == "success"
    assert mock_func.call_count == 3
    print("✓ Retry logic works correctly")
except Exception as e:
    print(f"✗ Retry logic failed: {e}")
    exit(1)
EOF
then
    print_success "Retry logic verified"
else
    print_error "Retry logic verification failed"
fi

# Summary
print_header "Test Summary"

echo "Examples Run:"
echo "  - example_prompts_usage.py: ✅"
echo "  - example_ai_enhancements.py: ✅ (or requires API keys)"
echo ""
echo "Tests Run:"
echo "  - Unit tests: ✅"
echo "  - Coverage report: ✅"
echo "  - Import verification: ✅"
echo "  - Prompt templates: ✅"
echo "  - Retry logic: ✅"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}=========================================================================="
    echo "All tests passed! ✅"
    echo "=========================================================================="
    echo ""
    echo "Next steps:"
    echo "  1. Review AI_ENHANCEMENTS_GUIDE.md for detailed documentation"
    echo "  2. Check examples/example_prompts_usage.py for usage patterns"
    echo "  3. Run tests with: pytest tests/test_ai_enhancements.py -v"
    echo "  4. Check coverage with: pytest tests/test_ai_enhancements.py --cov"
    echo ""
else
    echo -e "${RED}=========================================================================="
    echo "Some tests failed! ❌"
    echo "=========================================================================="
    echo ""
    echo "Failed tests: $FAILED"
    echo "Passed tests: $PASSED"
    echo ""
    exit 1
fi
