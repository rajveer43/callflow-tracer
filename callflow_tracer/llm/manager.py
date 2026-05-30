"""LLMInstrumentationManager and llm_instrumentation() context manager."""

from __future__ import annotations

import threading
from contextlib import contextmanager
from typing import Dict, List, Optional

from .anthropic_patch import AnthropicInstrumentor
from .base_patch import LLMInstrumentor
from .langchain_patch import LangChainInstrumentor
from .llamaindex_patch import LlamaIndexInstrumentor
from .openai_patch import OpenAIInstrumentor
from .span import get_llm_registry


class LLMInstrumentationManager:
    """Manages enabling / disabling LLM SDK patches."""

    def __init__(self) -> None:
        self.instrumentors: Dict[str, LLMInstrumentor] = {
            "anthropic": AnthropicInstrumentor(),
            "openai": OpenAIInstrumentor(),
            "langchain": LangChainInstrumentor(),
            "llamaindex": LlamaIndexInstrumentor(),
        }

    def enable_all(self) -> None:
        for inst in self.instrumentors.values():
            inst.enable()

    def disable_all(self) -> None:
        for inst in self.instrumentors.values():
            inst.disable()

    def enable_anthropic(self) -> None:
        self.instrumentors["anthropic"].enable()

    def disable_anthropic(self) -> None:
        self.instrumentors["anthropic"].disable()

    def enable_openai(self) -> None:
        self.instrumentors["openai"].enable()

    def disable_openai(self) -> None:
        self.instrumentors["openai"].disable()

    def enabled_providers(self) -> List[str]:
        return [name for name, inst in self.instrumentors.items() if inst.instrumentation_enabled]


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_manager: Optional[LLMInstrumentationManager] = None
_manager_lock = threading.Lock()


def get_llm_instrumentation_manager() -> LLMInstrumentationManager:
    global _manager
    if _manager is None:
        with _manager_lock:
            if _manager is None:
                _manager = LLMInstrumentationManager()
    return _manager


# ---------------------------------------------------------------------------
# Context manager
# ---------------------------------------------------------------------------

@contextmanager
def llm_instrumentation(
    providers: Optional[List[str]] = None,
    clear_registry: bool = False,
):
    """Enable LLM auto-instrumentation for the duration of the block.

    Args:
        providers: List of provider names to enable, e.g. ["anthropic"].
                   Defaults to all supported providers.
        clear_registry: If True, clear the LLMSpanRegistry before the block
                        so only spans from this block are recorded.

    Example::

        with llm_instrumentation(), trace_scope("out.json") as graph:
            response = client.messages.create(...)
            process(response)
    """
    manager = get_llm_instrumentation_manager()

    if clear_registry:
        get_llm_registry().clear()

    previously_enabled = manager.enabled_providers()

    targets = providers if providers is not None else list(manager.instrumentors.keys())
    for name in targets:
        if name in manager.instrumentors:
            manager.instrumentors[name].enable()

    try:
        yield manager
    finally:
        # Disable only those we newly enabled (don't disable pre-existing)
        for name in targets:
            if name not in previously_enabled and name in manager.instrumentors:
                manager.instrumentors[name].disable()
