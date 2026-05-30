"""callflow_tracer.llm — unified LLM + Python flame graph instrumentation.

Auto-patches Anthropic and OpenAI SDKs so every LLM call appears as a
first-class span inside the callflow-tracer flame graph, colored in gold,
with token counts and cost shown in the tooltip.

Quick start::

    from callflow_tracer import trace_scope, llm_instrumentation
    import anthropic

    client = anthropic.Anthropic()

    with llm_instrumentation(), trace_scope("trace.json") as graph:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=256,
            messages=[{"role": "user", "content": "Hello!"}],
        )
        process(response)
"""

from .cost_table import PRICING, calculate_cost
from .manager import (
    LLMInstrumentationManager,
    get_llm_instrumentation_manager,
    llm_instrumentation,
)
from .span import LLMSpan, LLMSpanRegistry, get_llm_registry

__all__ = [
    # Public API
    "llm_instrumentation",
    "get_llm_instrumentation_manager",
    "LLMInstrumentationManager",
    # Span model
    "LLMSpan",
    "LLMSpanRegistry",
    "get_llm_registry",
    # Pricing
    "PRICING",
    "calculate_cost",
]
