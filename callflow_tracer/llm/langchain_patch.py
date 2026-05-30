"""Auto-instrumentation for LangChain via its callback system.

Registers a CallflowCallbackHandler that intercepts every LLM start/end
event and records it as an LLMSpan + CallGraph edge — exactly like the
Anthropic and OpenAI patches, but using LangChain's native callback API
instead of monkey-patching underlying SDK methods.
"""

from __future__ import annotations

import threading
import time
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from .base_patch import LLMInstrumentor, _get_llm_caller_name
from .cost_table import calculate_cost
from .span import LLMSpan, get_llm_registry
from callflow_tracer.core.tracer import get_current_graph


class CallflowLangChainCallback:
    """LangChain BaseCallbackHandler that records LLM spans.

    Lazy-inherits from BaseCallbackHandler so the class can be *defined*
    even when langchain is not installed; it only becomes usable when
    langchain is present at runtime.
    """

    _base_cls_cache: Optional[type] = None

    @classmethod
    def _get_base(cls) -> type:
        if cls._base_cls_cache is None:
            from langchain.callbacks.base import BaseCallbackHandler  # type: ignore
            cls._base_cls_cache = BaseCallbackHandler
        return cls._base_cls_cache

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

    def __new__(cls, *args: Any, **kwargs: Any) -> "CallflowLangChainCallback":
        base = cls._get_base()
        # Dynamically mix in BaseCallbackHandler the first time we instantiate
        if base not in cls.__bases__:
            cls.__bases__ = (base,) + cls.__bases__
        instance = object.__new__(cls)
        return instance

    def __init__(self) -> None:
        base = self._get_base()
        base.__init__(self)
        self._start_times: Dict[UUID, float] = {}
        self._callers: Dict[UUID, str] = {}
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # LLM events
    # ------------------------------------------------------------------

    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        *,
        run_id: UUID,
        **kwargs: Any,
    ) -> None:
        caller = _get_llm_caller_name()
        with self._lock:
            self._start_times[run_id] = time.perf_counter()
            self._callers[run_id] = caller

    def on_llm_end(
        self,
        response: Any,
        *,
        run_id: UUID,
        **kwargs: Any,
    ) -> None:
        with self._lock:
            start = self._start_times.pop(run_id, None)
            caller = self._callers.pop(run_id, "<unknown>")
        if start is None:
            return

        duration = time.perf_counter() - start
        model = "unknown"
        input_tokens = 0
        output_tokens = 0

        try:
            # LLMResult → generations[0][0].generation_info or llm_output
            llm_output = getattr(response, "llm_output", {}) or {}
            model = llm_output.get("model_name", model)
            token_usage = llm_output.get("token_usage", {})
            input_tokens = token_usage.get("prompt_tokens", 0)
            output_tokens = token_usage.get("completion_tokens", 0)
        except Exception:
            pass

        node_full_name = f"llm.langchain.{model}"
        graph = get_current_graph()
        if graph is not None:
            graph.record_call(
                caller=caller,
                callee=node_full_name,
                duration=duration,
                args=[],
                kwargs={},
                skip_reason=None,
            )

        cost = calculate_cost(model, input_tokens, output_tokens)
        span = LLMSpan(
            node_full_name=node_full_name,
            provider="langchain",
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
        )
        get_llm_registry().record(span)

    def on_llm_error(
        self,
        error: Union[Exception, KeyboardInterrupt],
        *,
        run_id: UUID,
        **kwargs: Any,
    ) -> None:
        with self._lock:
            self._start_times.pop(run_id, None)
            self._callers.pop(run_id, None)


class LangChainInstrumentor(LLMInstrumentor):
    """Injects CallflowLangChainCallback into LangChain's global callback manager."""

    provider_name = "langchain"

    def __init__(self) -> None:
        super().__init__()
        self._callback: Optional[CallflowLangChainCallback] = None

    def _patch_methods(self) -> None:
        try:
            from langchain.callbacks import get_callback_manager  # type: ignore
        except ImportError:
            try:
                # LangChain ≥0.1 uses a different import path
                from langchain_core.callbacks import get_callback_manager  # type: ignore
            except ImportError:
                return

        self._callback = CallflowLangChainCallback()
        try:
            get_callback_manager().add_handler(self._callback)
        except Exception:
            pass

    def _unpatch_methods(self) -> None:
        if self._callback is None:
            return
        try:
            from langchain.callbacks import get_callback_manager  # type: ignore
        except ImportError:
            try:
                from langchain_core.callbacks import get_callback_manager  # type: ignore
            except ImportError:
                return
        try:
            get_callback_manager().remove_handler(self._callback)
        except Exception:
            pass
        self._callback = None
        super()._unpatch_methods()
