"""
LLM provider abstraction for CallFlow Tracer AI features.

Supports multiple LLM providers: OpenAI, Anthropic, Google Gemini, Ollama (local).
Enhanced with retry logic, rate limiting, and advanced model support.
"""

import os
import time
import random
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import json
import logging

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        """
        Initialize LLM provider with retry configuration.
        
        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries (seconds)
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None, 
                 temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """Generate text from the LLM."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is configured and available."""
        pass
    
    def _retry_with_backoff(self, func, *args, **kwargs):
        """
        Execute function with exponential backoff retry logic.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function result
            
        Raises:
            RuntimeError: If all retries fail
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_retries - 1:
                    # Exponential backoff with jitter
                    delay = self.retry_delay * (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(
                        f"Attempt {attempt + 1}/{self.max_retries} failed: {str(e)}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    time.sleep(delay)
        
        raise RuntimeError(f"Failed after {self.max_retries} attempts: {str(last_exception)}")


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider with support for GPT-4 Turbo and advanced models."""
    
    # Model configurations with context windows
    MODELS = {
        "gpt-4-turbo": {"context_window": 128000, "cost_per_1k_input": 0.01},
        "gpt-4o": {"context_window": 128000, "cost_per_1k_input": 0.005},
        "gpt-4o-mini": {"context_window": 128000, "cost_per_1k_input": 0.00015},
        "gpt-3.5-turbo": {"context_window": 4096, "cost_per_1k_input": 0.0005},
    }
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini", 
                 max_retries: int = 3, retry_delay: float = 1.0):
        super().__init__(max_retries=max_retries, retry_delay=retry_delay)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self._client = None
    
    def _get_client(self):
        """Lazy load OpenAI client."""
        if self._client is None:
            try:
                import openai
                self._client = openai.OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "OpenAI package not installed. Install with: pip install openai"
                )
        return self._client
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None,
                 temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """Generate text using OpenAI API with retry logic."""
        if not self.is_available():
            raise ValueError("OpenAI API key not configured. Set OPENAI_API_KEY environment variable.")
        
        def _generate():
            client = self._get_client()
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        
        return self._retry_with_backoff(_generate)
    
    def is_available(self) -> bool:
        """Check if OpenAI is configured."""
        return bool(self.api_key)


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider with support for Claude 3 Opus and advanced models."""
    
    # Model configurations with context windows
    MODELS = {
        "claude-3-opus-20240229": {"context_window": 200000, "cost_per_1k_input": 0.015},
        "claude-3-sonnet-20240229": {"context_window": 200000, "cost_per_1k_input": 0.003},
        "claude-3-haiku-20240307": {"context_window": 200000, "cost_per_1k_input": 0.00025},
        "claude-3-5-sonnet-20241022": {"context_window": 200000, "cost_per_1k_input": 0.003},
    }
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022",
                 max_retries: int = 3, retry_delay: float = 1.0):
        super().__init__(max_retries=max_retries, retry_delay=retry_delay)
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self._client = None
    
    def _get_client(self):
        """Lazy load Anthropic client."""
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "Anthropic package not installed. Install with: pip install anthropic"
                )
        return self._client
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None,
                 temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """Generate text using Anthropic API with retry logic."""
        if not self.is_available():
            raise ValueError("Anthropic API key not configured. Set ANTHROPIC_API_KEY environment variable.")
        
        def _generate():
            client = self._get_client()
            
            kwargs = {
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            if system_prompt:
                kwargs["system"] = system_prompt
            
            response = client.messages.create(**kwargs)
            return response.content[0].text
        
        return self._retry_with_backoff(_generate)
    
    def is_available(self) -> bool:
        """Check if Anthropic is configured."""
        return bool(self.api_key)


class GeminiProvider(LLMProvider):
    """Google Gemini provider with support for Gemini Pro and advanced models."""
    
    # Model configurations with context windows
    MODELS = {
        "gemini-1.5-pro": {"context_window": 1000000, "cost_per_1k_input": 0.0075},
        "gemini-1.5-flash": {"context_window": 1000000, "cost_per_1k_input": 0.00075},
        "gemini-pro": {"context_window": 32768, "cost_per_1k_input": 0.0005},
    }
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash",
                 max_retries: int = 3, retry_delay: float = 1.0):
        super().__init__(max_retries=max_retries, retry_delay=retry_delay)
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.model = model
        self._client = None
    
    def _get_client(self):
        """Lazy load Gemini client."""
        if self._client is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._client = genai
            except ImportError:
                raise ImportError(
                    "Google Generative AI package not installed. Install with: pip install google-generativeai"
                )
        return self._client
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None,
                 temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """Generate text using Google Gemini API with retry logic."""
        if not self.is_available():
            raise ValueError("Gemini API key not configured. Set GEMINI_API_KEY or GOOGLE_API_KEY environment variable.")
        
        def _generate():
            genai = self._get_client()
            
            # Combine system prompt with user prompt if provided
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Create model instance
            model = genai.GenerativeModel(self.model)
            
            # Configure generation parameters
            generation_config = genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
            
            response = model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            return response.text
        
        return self._retry_with_backoff(_generate)
    
    def is_available(self) -> bool:
        """Check if Gemini is configured."""
        return bool(self.api_key)


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider with retry logic."""
    
    def __init__(self, model: str = "llama3.1", base_url: str = "http://localhost:11434",
                 max_retries: int = 3, retry_delay: float = 1.0):
        super().__init__(max_retries=max_retries, retry_delay=retry_delay)
        self.model = model
        self.base_url = base_url
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None,
                 temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """Generate text using Ollama with retry logic."""
        try:
            import requests
        except ImportError:
            raise ImportError(
                "Requests package not installed. Install with: pip install requests"
            )
        
        def _generate():
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json()["response"]
        
        return self._retry_with_backoff(_generate)
    
    def is_available(self) -> bool:
        """Check if Ollama is running."""
        try:
            import requests
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False


def get_default_provider(provider_name: Optional[str] = None) -> LLMProvider:
    """
    Get the default LLM provider based on environment or explicit choice.
    
    Args:
        provider_name: Explicit provider name ('openai', 'anthropic', 'gemini', 'ollama')
                      If None, auto-detect from environment variables
    
    Returns:
        Configured LLMProvider instance
    
    Raises:
        ValueError: If no provider is available
    """
    if provider_name:
        provider_name = provider_name.lower()
        if provider_name == "openai":
            provider = OpenAIProvider()
        elif provider_name == "anthropic":
            provider = AnthropicProvider()
        elif provider_name in ["gemini", "google"]:
            provider = GeminiProvider()
        elif provider_name == "ollama":
            provider = OllamaProvider()
        else:
            raise ValueError(f"Unknown provider: {provider_name}")
        
        if not provider.is_available():
            raise ValueError(f"Provider {provider_name} is not available or not configured")
        return provider
    
    # Auto-detect
    providers = [
        OpenAIProvider(),
        AnthropicProvider(),
        GeminiProvider(),
        OllamaProvider()
    ]
    
    for provider in providers:
        if provider.is_available():
            return provider
    
    raise ValueError(
        "No LLM provider available. Please configure one of:\n"
        "- OpenAI: Set OPENAI_API_KEY environment variable\n"
        "- Anthropic: Set ANTHROPIC_API_KEY environment variable\n"
        "- Google Gemini: Set GEMINI_API_KEY or GOOGLE_API_KEY environment variable\n"
        "- Ollama: Install and run Ollama locally (https://ollama.ai)"
    )
