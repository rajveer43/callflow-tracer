"""
LLM provider abstraction for CallFlow Tracer AI features.

Supports multiple LLM providers: OpenAI, Anthropic, Google Gemini, Ollama (local).
"""

import os
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import json


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None, 
                 temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """Generate text from the LLM."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is configured and available."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
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
        """Generate text using OpenAI API."""
        if not self.is_available():
            raise ValueError("OpenAI API key not configured. Set OPENAI_API_KEY environment variable.")
        
        client = self._get_client()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if OpenAI is configured."""
        return bool(self.api_key)


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022"):
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
        """Generate text using Anthropic API."""
        if not self.is_available():
            raise ValueError("Anthropic API key not configured. Set ANTHROPIC_API_KEY environment variable.")
        
        client = self._get_client()
        
        try:
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
        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if Anthropic is configured."""
        return bool(self.api_key)


class GeminiProvider(LLMProvider):
    """Google Gemini provider."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash"):
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
        """Generate text using Google Gemini API."""
        if not self.is_available():
            raise ValueError("Gemini API key not configured. Set GEMINI_API_KEY or GOOGLE_API_KEY environment variable.")
        
        genai = self._get_client()
        
        # Combine system prompt with user prompt if provided
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        try:
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
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if Gemini is configured."""
        return bool(self.api_key)


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider."""
    
    def __init__(self, model: str = "llama3.1", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None,
                 temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """Generate text using Ollama."""
        try:
            import requests
        except ImportError:
            raise ImportError(
                "Requests package not installed. Install with: pip install requests"
            )
        
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        try:
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
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ollama API error: {str(e)}")
    
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
