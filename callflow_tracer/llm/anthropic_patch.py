"""Auto-instrumentation for the Anthropic Python SDK."""

from __future__ import annotations

import time
from typing import Any

from .base_patch import LLMInstrumentor, _get_llm_caller_name


class AnthropicInstrumentor(LLMInstrumentor):
    """Patches anthropic.Anthropic.messages.create (sync + async)."""

    provider_name = "anthropic"

    def _patch_methods(self) -> None:
        try:
            import anthropic
        except ImportError:
            return

        self._patch_sync(anthropic)
        self._patch_async(anthropic)

    # ------------------------------------------------------------------
    # Sync
    # ------------------------------------------------------------------

    def _patch_sync(self, anthropic: Any) -> None:
        messages_cls = anthropic.resources.messages.Messages
        self._store_original(messages_cls, "create")
        original_create = self.original_methods[(messages_cls, "create")]
        instrumentor = self

        def patched_create(self_sdk, *args: Any, **kwargs: Any) -> Any:
            caller = _get_llm_caller_name()
            start = time.perf_counter()
            error = None
            try:
                response = original_create(self_sdk, *args, **kwargs)
                return response
            except Exception as exc:
                error = exc
                raise
            finally:
                duration = time.perf_counter() - start
                model = kwargs.get("model", "unknown")
                input_tokens = 0
                output_tokens = 0
                if error is None:
                    try:
                        input_tokens = response.usage.input_tokens or 0
                        output_tokens = response.usage.output_tokens or 0
                        model = response.model or model
                    except Exception:
                        pass
                instrumentor._record_llm_call(
                    caller_name=caller,
                    model=model,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    duration=duration,
                    error=error,
                )

        messages_cls.create = patched_create

    # ------------------------------------------------------------------
    # Async
    # ------------------------------------------------------------------

    def _patch_async(self, anthropic: Any) -> None:
        try:
            async_messages_cls = anthropic.resources.messages.AsyncMessages
        except AttributeError:
            return

        self._store_original(async_messages_cls, "create")
        original_create = self.original_methods[(async_messages_cls, "create")]
        instrumentor = self

        async def patched_async_create(self_sdk, *args: Any, **kwargs: Any) -> Any:
            caller = _get_llm_caller_name()
            start = time.perf_counter()
            error = None
            try:
                response = await original_create(self_sdk, *args, **kwargs)
                return response
            except Exception as exc:
                error = exc
                raise
            finally:
                duration = time.perf_counter() - start
                model = kwargs.get("model", "unknown")
                input_tokens = 0
                output_tokens = 0
                if error is None:
                    try:
                        input_tokens = response.usage.input_tokens or 0
                        output_tokens = response.usage.output_tokens or 0
                        model = response.model or model
                    except Exception:
                        pass
                instrumentor._record_llm_call(
                    caller_name=caller,
                    model=model,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    duration=duration,
                    error=error,
                )

        async_messages_cls.create = patched_async_create
