"""LLMSpan dataclass and thread-safe LLMSpanRegistry singleton."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class LLMSpan:
    node_full_name: str   # e.g. "llm.anthropic.claude-sonnet-4-6"
    provider: str         # "anthropic" | "openai"
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "node_full_name": self.node_full_name,
            "provider": self.provider,
            "model": self.model,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.input_tokens + self.output_tokens,
            "cost_usd": self.cost_usd,
            "timestamp": self.timestamp,
        }


class LLMSpanRegistry:
    """Singleton registry mapping node_full_name → aggregated LLMSpan.

    Multiple calls to the same model accumulate token counts and cost
    so the flame graph tooltip shows lifetime totals, matching how
    CallNode aggregates call_count / total_time.
    """

    _instance: Optional["LLMSpanRegistry"] = None
    _init_lock: threading.Lock = threading.Lock()

    def __new__(cls) -> "LLMSpanRegistry":
        with cls._init_lock:
            if cls._instance is None:
                inst = super().__new__(cls)
                inst._spans: Dict[str, LLMSpan] = {}
                inst._lock = threading.Lock()
                cls._instance = inst
        return cls._instance

    def record(self, span: LLMSpan) -> None:
        with self._lock:
            existing = self._spans.get(span.node_full_name)
            if existing is None:
                self._spans[span.node_full_name] = span
            else:
                # Aggregate — keep earliest timestamp
                existing.input_tokens += span.input_tokens
                existing.output_tokens += span.output_tokens
                existing.cost_usd += span.cost_usd

    def get(self, node_full_name: str) -> Optional[LLMSpan]:
        with self._lock:
            return self._spans.get(node_full_name)

    def get_all(self) -> Dict[str, LLMSpan]:
        with self._lock:
            return dict(self._spans)

    def clear(self) -> None:
        with self._lock:
            self._spans.clear()


_registry: Optional[LLMSpanRegistry] = None
_registry_lock = threading.Lock()


def get_llm_registry() -> LLMSpanRegistry:
    global _registry
    if _registry is None:
        with _registry_lock:
            if _registry is None:
                _registry = LLMSpanRegistry()
    return _registry
