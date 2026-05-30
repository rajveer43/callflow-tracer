"""Abstract base for LLM SDK auto-instrumentation."""

from __future__ import annotations

import sys
import time
from typing import Optional

from callflow_tracer.core.auto_instrumentation import AutoInstrumentor
from callflow_tracer.core.tracer import get_current_graph

from .cost_table import calculate_cost
from .span import LLMSpan, get_llm_registry


def _get_llm_caller_name() -> str:
    """Walk the stack to find the first frame outside callflow_tracer and LLM SDK internals."""
    _skip = {"callflow_tracer", "anthropic", "openai", "httpx", "httpcore"}
    try:
        frame = sys._getframe(1)
        while frame is not None:
            module_name = frame.f_globals.get("__name__", "")
            if not any(module_name.startswith(s) for s in _skip):
                func_name = frame.f_code.co_name
                if module_name and module_name != "__main__":
                    return f"{module_name}.{func_name}"
                return func_name or "<unknown>"
            frame = frame.f_back
    except Exception:
        pass
    return "<unknown>"


class LLMInstrumentor(AutoInstrumentor):
    """Base class for LLM SDK patchers.

    Subclasses implement `_patch_methods()` targeting a specific SDK.
    After every LLM call they call `_record_llm_call()` which writes
    both a CallGraph edge and an LLMSpan into the registry.
    """

    provider_name: str = ""  # set by subclass, e.g. "anthropic"

    def _record_llm_call(
        self,
        caller_name: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        duration: float,
        error: Optional[Exception] = None,
    ) -> None:
        node_full_name = f"llm.{self.provider_name}.{model}"

        graph = get_current_graph()
        if graph is not None:
            graph.record_call(
                caller=caller_name,
                callee=node_full_name,
                duration=duration,
                args=[],
                kwargs={},
                skip_reason=None,
            )

        cost = calculate_cost(model, input_tokens, output_tokens)
        span = LLMSpan(
            node_full_name=node_full_name,
            provider=self.provider_name,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
        )
        get_llm_registry().record(span)
