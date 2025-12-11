"""
Test suite for AI enhancements in CallFlow Tracer v0.4.0

Tests cover:
1. LLM Provider functionality
2. Retry logic and error handling
3. Prompt template generation
4. Integration with AI modules
"""

import pytest
import logging
from unittest.mock import Mock, patch, MagicMock
from callflow_tracer.ai import (
    OpenAIProvider,
    AnthropicProvider,
    GeminiProvider,
    OllamaProvider,
    PromptTemplates,
    get_prompt_for_task,
)


# ============================================================================
# TESTS FOR LLM PROVIDERS
# ============================================================================

class TestOpenAIProvider:
    """Test OpenAI provider with retry logic."""
    
    def test_provider_initialization(self):
        """Test OpenAI provider initialization."""
        provider = OpenAIProvider(
            api_key="test-key",
            model="gpt-4o",
            max_retries=5,
            retry_delay=2.0
        )
        
        assert provider.api_key == "test-key"
        assert provider.model == "gpt-4o"
        assert provider.max_retries == 5
        assert provider.retry_delay == 2.0
    
    def test_provider_model_configurations(self):
        """Test that model configurations are available."""
        provider = OpenAIProvider()
        
        assert "gpt-4-turbo" in provider.MODELS
        assert "gpt-4o" in provider.MODELS
        assert "gpt-4o-mini" in provider.MODELS
        assert "gpt-3.5-turbo" in provider.MODELS
        
        # Check context windows
        assert provider.MODELS["gpt-4-turbo"]["context_window"] == 128000
        assert provider.MODELS["gpt-4o"]["context_window"] == 128000
    
    def test_is_available_without_key(self):
        """Test is_available returns False without API key."""
        provider = OpenAIProvider(api_key=None)
        assert provider.is_available() is False
    
    def test_is_available_with_key(self):
        """Test is_available returns True with API key."""
        provider = OpenAIProvider(api_key="test-key")
        assert provider.is_available() is True
    
    @patch('openai.OpenAI')
    def test_generate_with_retry_success(self, mock_openai):
        """Test successful generation with retry logic."""
        # Mock the OpenAI client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Test response"))]
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch.object(OpenAIProvider, '_get_client', return_value=mock_client):
            provider = OpenAIProvider(api_key="test-key")
            result = provider.generate("Test prompt", "Test system prompt")
            
            assert result == "Test response"
            mock_client.chat.completions.create.assert_called_once()


class TestAnthropicProvider:
    """Test Anthropic provider with retry logic."""
    
    def test_provider_initialization(self):
        """Test Anthropic provider initialization."""
        provider = AnthropicProvider(
            api_key="test-key",
            model="claude-3-opus-20240229",
            max_retries=3,
            retry_delay=1.0
        )
        
        assert provider.api_key == "test-key"
        assert provider.model == "claude-3-opus-20240229"
        assert provider.max_retries == 3
        assert provider.retry_delay == 1.0
    
    def test_provider_model_configurations(self):
        """Test that Claude model configurations are available."""
        provider = AnthropicProvider()
        
        assert "claude-3-opus-20240229" in provider.MODELS
        assert "claude-3-sonnet-20240229" in provider.MODELS
        assert "claude-3-haiku-20240307" in provider.MODELS
        assert "claude-3-5-sonnet-20241022" in provider.MODELS
        
        # Check context windows
        assert provider.MODELS["claude-3-opus-20240229"]["context_window"] == 200000
    
    def test_is_available_with_key(self):
        """Test is_available with API key."""
        provider = AnthropicProvider(api_key="test-key")
        assert provider.is_available() is True


class TestGeminiProvider:
    """Test Google Gemini provider with retry logic."""
    
    def test_provider_initialization(self):
        """Test Gemini provider initialization."""
        provider = GeminiProvider(
            api_key="test-key",
            model="gemini-1.5-pro",
            max_retries=4,
            retry_delay=1.5
        )
        
        assert provider.api_key == "test-key"
        assert provider.model == "gemini-1.5-pro"
        assert provider.max_retries == 4
        assert provider.retry_delay == 1.5
    
    def test_provider_model_configurations(self):
        """Test that Gemini model configurations are available."""
        provider = GeminiProvider()
        
        assert "gemini-1.5-pro" in provider.MODELS
        assert "gemini-1.5-flash" in provider.MODELS
        assert "gemini-pro" in provider.MODELS
        
        # Check context windows
        assert provider.MODELS["gemini-1.5-pro"]["context_window"] == 1000000


class TestOllamaProvider:
    """Test Ollama local provider."""
    
    def test_provider_initialization(self):
        """Test Ollama provider initialization."""
        provider = OllamaProvider(
            model="llama3.1",
            base_url="http://localhost:11434",
            max_retries=3,
            retry_delay=1.0
        )
        
        assert provider.model == "llama3.1"
        assert provider.base_url == "http://localhost:11434"
        assert provider.max_retries == 3
        assert provider.retry_delay == 1.0


# ============================================================================
# TESTS FOR RETRY LOGIC
# ============================================================================

class TestRetryLogic:
    """Test retry logic with exponential backoff."""
    
    def test_retry_with_backoff_success_first_attempt(self):
        """Test successful execution on first attempt."""
        provider = OpenAIProvider(api_key="test-key", max_retries=3)
        
        mock_func = Mock(return_value="success")
        result = provider._retry_with_backoff(mock_func)
        
        assert result == "success"
        assert mock_func.call_count == 1
    
    def test_retry_with_backoff_success_after_retries(self):
        """Test successful execution after retries."""
        provider = OpenAIProvider(api_key="test-key", max_retries=3)
        
        # Fail twice, then succeed
        mock_func = Mock(side_effect=[
            Exception("Attempt 1 failed"),
            Exception("Attempt 2 failed"),
            "success"
        ])
        
        with patch('time.sleep'):  # Mock sleep to speed up test
            result = provider._retry_with_backoff(mock_func)
        
        assert result == "success"
        assert mock_func.call_count == 3
    
    def test_retry_with_backoff_all_failures(self):
        """Test failure after all retries exhausted."""
        provider = OpenAIProvider(api_key="test-key", max_retries=3)
        
        mock_func = Mock(side_effect=Exception("Always fails"))
        
        with patch('time.sleep'):
            with pytest.raises(RuntimeError) as exc_info:
                provider._retry_with_backoff(mock_func)
        
        assert "Failed after 3 attempts" in str(exc_info.value)
        assert mock_func.call_count == 3


# ============================================================================
# TESTS FOR PROMPT TEMPLATES
# ============================================================================

class TestPromptTemplates:
    """Test prompt template generation."""
    
    def test_performance_analysis_prompt(self):
        """Test performance analysis prompt generation."""
        system, user = PromptTemplates.query_performance_analysis(
            graph_summary="Test summary",
            question="What are bottlenecks?"
        )
        
        assert isinstance(system, str)
        assert isinstance(user, str)
        assert len(system) > 0
        assert len(user) > 0
        assert "performance analyst" in system.lower()
        assert "bottleneck" in user.lower()
    
    def test_root_cause_analysis_prompt(self):
        """Test root cause analysis prompt generation."""
        system, user = PromptTemplates.root_cause_analysis(
            root_causes="Test causes",
            impact="Test impact",
            issue_type="performance"
        )
        
        assert isinstance(system, str)
        assert isinstance(user, str)
        assert "debugger" in system.lower()
        assert "root cause" in user.lower()
    
    def test_code_fix_prompt(self):
        """Test code fix generation prompt."""
        system, user = PromptTemplates.generate_code_fix(
            issue_type="n_plus_one",
            function_name="test_func",
            context="Test context",
            before_code="def test(): pass"
        )
        
        assert isinstance(system, str)
        assert isinstance(user, str)
        assert "optimizer" in system.lower()
        assert "n_plus_one" in user.lower()
    
    def test_anomaly_analysis_prompt(self):
        """Test anomaly analysis prompt generation."""
        system, user = PromptTemplates.analyze_anomalies(
            anomalies="Test anomalies",
            baseline="Test baseline"
        )
        
        assert isinstance(system, str)
        assert isinstance(user, str)
        assert "statistical" in system.lower()
        assert "anomaly" in user.lower()
    
    def test_security_analysis_prompt(self):
        """Test security analysis prompt generation."""
        system, user = PromptTemplates.analyze_security_issues(
            issues="Test issues",
            code_context="Test code"
        )
        
        assert isinstance(system, str)
        assert isinstance(user, str)
        assert "security" in system.lower()
        assert "owasp" in system.lower()
    
    def test_refactoring_prompt(self):
        """Test refactoring suggestions prompt."""
        system, user = PromptTemplates.suggest_refactoring(
            function_code="def test(): pass",
            metrics={'complexity': 10}
        )
        
        assert isinstance(system, str)
        assert isinstance(user, str)
        assert "architect" in system.lower()
        assert "refactor" in user.lower()
    
    def test_test_generation_prompt(self):
        """Test test generation prompt."""
        system, user = PromptTemplates.generate_tests(
            function_code="def test(): pass",
            function_name="test_func"
        )
        
        assert isinstance(system, str)
        assert isinstance(user, str)
        assert "qa" in system.lower() or "test" in system.lower()
        assert "pytest" in user.lower()
    
    def test_documentation_prompt(self):
        """Test documentation generation prompt."""
        system, user = PromptTemplates.generate_documentation(
            function_code="def test(): pass",
            function_name="test_func"
        )
        
        assert isinstance(system, str)
        assert isinstance(user, str)
        assert "documentation" in system.lower()
        assert "docstring" in user.lower()


# ============================================================================
# TESTS FOR GET_PROMPT_FOR_TASK FUNCTION
# ============================================================================

class TestGetPromptForTask:
    """Test get_prompt_for_task convenience function."""
    
    def test_get_prompt_performance_analysis(self):
        """Test getting performance analysis prompt."""
        system, user = get_prompt_for_task(
            'performance_analysis',
            graph_summary="Test",
            question="Test?"
        )
        
        assert isinstance(system, str)
        assert isinstance(user, str)
    
    def test_get_prompt_root_cause_analysis(self):
        """Test getting root cause analysis prompt."""
        system, user = get_prompt_for_task(
            'root_cause_analysis',
            root_causes="Test",
            impact="Test",
            issue_type="performance"
        )
        
        assert isinstance(system, str)
        assert isinstance(user, str)
    
    def test_get_prompt_code_fix(self):
        """Test getting code fix prompt."""
        system, user = get_prompt_for_task(
            'code_fix',
            issue_type='n_plus_one',
            function_name='test',
            context='Test'
        )
        
        assert isinstance(system, str)
        assert isinstance(user, str)
    
    def test_get_prompt_invalid_task(self):
        """Test error handling for invalid task type."""
        with pytest.raises(ValueError) as exc_info:
            get_prompt_for_task('invalid_task')
        
        assert "Unknown task type" in str(exc_info.value)
    
    def test_all_task_types_available(self):
        """Test that all task types are available."""
        task_types = [
            'performance_analysis',
            'root_cause_analysis',
            'code_fix',
            'anomaly_analysis',
            'security_analysis',
            'refactoring',
            'test_generation',
            'documentation',
        ]
        
        for task_type in task_types:
            # Should not raise an error
            try:
                if task_type == 'performance_analysis':
                    get_prompt_for_task(task_type, graph_summary="", question="")
                elif task_type == 'root_cause_analysis':
                    get_prompt_for_task(task_type, root_causes="", impact="", issue_type="")
                elif task_type == 'code_fix':
                    get_prompt_for_task(task_type, issue_type="", function_name="", context="")
                elif task_type == 'anomaly_analysis':
                    get_prompt_for_task(task_type, anomalies="")
                elif task_type == 'security_analysis':
                    get_prompt_for_task(task_type, issues="")
                elif task_type == 'refactoring':
                    get_prompt_for_task(task_type, function_code="", metrics={})
                elif task_type == 'test_generation':
                    get_prompt_for_task(task_type, function_code="", function_name="")
                elif task_type == 'documentation':
                    get_prompt_for_task(task_type, function_code="", function_name="")
            except TypeError:
                # Expected for missing required parameters
                pass


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for AI enhancements."""
    
    def test_prompt_consistency(self):
        """Test that prompts are consistent across calls."""
        graph_summary = "Test summary"
        question = "Test question"
        
        system1, user1 = get_prompt_for_task(
            'performance_analysis',
            graph_summary=graph_summary,
            question=question
        )
        
        system2, user2 = get_prompt_for_task(
            'performance_analysis',
            graph_summary=graph_summary,
            question=question
        )
        
        assert system1 == system2
        assert user1 == user2
    
    def test_prompt_includes_input_data(self):
        """Test that prompts include the provided input data."""
        graph_summary = "UNIQUE_SUMMARY_12345"
        question = "UNIQUE_QUESTION_67890"
        
        system, user = get_prompt_for_task(
            'performance_analysis',
            graph_summary=graph_summary,
            question=question
        )
        
        assert graph_summary in user
        assert question in user
    
    def test_different_tasks_have_different_prompts(self):
        """Test that different tasks generate different prompts."""
        system1, user1 = get_prompt_for_task(
            'performance_analysis',
            graph_summary="Test",
            question="Test?"
        )
        
        system2, user2 = get_prompt_for_task(
            'root_cause_analysis',
            root_causes="Test",
            impact="Test",
            issue_type="performance"
        )
        
        # Prompts should be different
        assert system1 != system2 or user1 != user2


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Test performance of prompt generation."""
    
    def test_prompt_generation_speed(self):
        """Test that prompt generation is fast."""
        import time
        
        start = time.time()
        for _ in range(100):
            get_prompt_for_task(
                'performance_analysis',
                graph_summary="Test",
                question="Test?"
            )
        elapsed = time.time() - start
        
        # Should complete 100 prompts in less than 1 second
        assert elapsed < 1.0, f"Prompt generation too slow: {elapsed}s for 100 prompts"


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
