"""Auto-instrumentation for LlamaIndex LLMs.

Monkey-patches BaseLLM.complete / acomplete / chat / achat so every call
is captured as an LLMSpan regardless of which underlying model is used
(OpenAI, Anthropic, local, etc.).
"""

from __future__ import annotations

import time
from typing import Any

from .base_patch import LLMInstrumentor, _get_llm_caller_name


class LlamaIndexInstrumentor(LLMInstrumentor):
    """Patches llama_index.core.llms.BaseLLM sync + async entrypoints."""

    provider_name = "llamaindex"

    def _patch_methods(self) -> None:
        try:
            from llama_index.core.llms import LLM as BaseLLM  # type: ignore
        except ImportError:
            try:
                from llama_index.llms.base import BaseLLM  # type: ignore[no-redef]
            except ImportError:
                return

        for method_name in ("complete", "chat"):
            self._wrap_sync(BaseLLM, method_name)
        for method_name in ("acomplete", "achat"):
            self._wrap_async(BaseLLM, method_name)

    # ------------------------------------------------------------------
    # Sync wrapper factory
    # ------------------------------------------------------------------

    def _wrap_sync(self, cls: type, method_name: str) -> None:
        if not hasattr(cls, method_name):
            return
        self._store_original(cls, method_name)
        original = self.original_methods[(cls, method_name)]
        instrumentor = self

        def patched(self_llm: Any, *args: Any, **kwargs: Any) -> Any:
            caller = _get_llm_caller_name()
            start = time.perf_counter()
            error = None
            response = None
            try:
                response = original(self_llm, *args, **kwargs)
                return response
            except Exception as exc:
                error = exc
                raise
            finally:
                duration = time.perf_counter() - start
                model = getattr(self_llm, "model", None) or "unknown"
                input_tokens = output_tokens = 0
                if error is None and response is not None:
                    try:
                        usage = getattr(response, "raw", {}) or {}
                        input_tokens = usage.get("usage", {}).get("prompt_tokens", 0)
                        output_tokens = usage.get("usage", {}).get("completion_tokens", 0)
                    except Exception:
                        pass
                instrumentor._record_llm_call(
                    caller_name=caller,
                    model=str(model),
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    duration=duration,
                    error=error,
                )

        setattr(cls, method_name, patched)

    # ------------------------------------------------------------------
    # Async wrapper factory
    # ------------------------------------------------------------------

    def _wrap_async(self, cls: type, method_name: str) -> None:
        if not hasattr(cls, method_name):
            return
        self._store_original(cls, method_name)
        original = self.original_methods[(cls, method_name)]
        instrumentor = self

        async def patched_async(self_llm: Any, *args: Any, **kwargs: Any) -> Any:
            caller = _get_llm_caller_name()
            start = time.perf_counter()
            error = None
            response = None
            try:
                response = await original(self_llm, *args, **kwargs)
                return response
            except Exception as exc:
                error = exc
                raise
            finally:
                duration = time.perf_counter() - start
                model = getattr(self_llm, "model", None) or "unknown"
                input_tokens = output_tokens = 0
                if error is None and response is not None:
                    try:
                        usage = getattr(response, "raw", {}) or {}
                        input_tokens = usage.get("usage", {}).get("prompt_tokens", 0)
                        output_tokens = usage.get("usage", {}).get("completion_tokens", 0)
                    except Exception:
                        pass
                instrumentor._record_llm_call(
                    caller_name=caller,
                    model=str(model),
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    duration=duration,
                    error=error,
                )

        setattr(cls, method_name, patched_async)
