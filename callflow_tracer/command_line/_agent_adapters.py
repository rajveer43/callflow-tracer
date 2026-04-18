"""
LLM / agent SDK detection via the Adapter Pattern.

Problem: Every LLM SDK uses different function names.
  anthropic  →  messages.create / messages.stream
  openai     →  chat.completions.create / completions.create
  langchain  →  LLMChain.__call__ / AgentExecutor.invoke / BaseTool._run
  litellm    →  completion / acompletion
  raw tool   →  anything matching "tool" + "_run" / "execute" / "invoke"

Solution: Each SDK gets one Adapter that (a) decides if a full_name belongs to
it, and (b) normalises a CallNode into a uniform AgentEvent.  A LLMAdapterRegistry
holds all adapters and returns the first match — O(A) where A = |adapters| (tiny).

DSA used:
  - frozenset  : O(1) exact-token membership for known SDK identifiers
  - list       : ordered adapter search (first-match wins)
  - dataclass  : immutable AgentEvent value object

Patterns:
  Adapter  → LLMCallAdapter hierarchy  (normalize divergent SDKs into one format)
  Registry → LLMAdapterRegistry        (ordered first-match dispatch)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.tracer import CallNode

# ── Normalised output value object ────────────────────────────────────────────

@dataclass(frozen=True)
class AgentEvent:
    """
    Unified representation of one LLM or tool invocation extracted from a trace.

    Fields:
        kind             : "llm" | "tool" | "embed" | "chain"
        name             : canonical function/tool name
        provider         : SDK identifier string
        call_count       : how many times this node was called
        total_time_ms    : total wall-clock ms across all calls
        avg_time_ms      : per-call average
        input_tokens_est : rough input token estimate (timing-based heuristic)
        output_tokens_est: rough output token estimate
        cost_usd_est     : rough USD cost estimate (based on cheap model rates)
    """

    kind: str
    name: str
    provider: str
    call_count: int
    total_time_ms: float
    avg_time_ms: float
    input_tokens_est: int
    output_tokens_est: int
    cost_usd_est: float


# ── Token and cost estimation helpers ─────────────────────────────────────────

# Heuristic throughput (tokens/second) by provider — conservative estimates
# so we don't over-promise accuracy.
_TOKENS_PER_SECOND: dict[str, float] = {
    "anthropic": 80.0,
    "openai":    100.0,
    "langchain": 90.0,
    "litellm":   90.0,
    "unknown":   80.0,
}

# Very rough cost per 1K tokens (output) in USD — use cheapest model as floor
_COST_PER_1K_OUTPUT: dict[str, float] = {
    "anthropic": 0.003,
    "openai":    0.002,
    "langchain": 0.002,
    "litellm":   0.002,
    "unknown":   0.003,
}


def _estimate_tokens(avg_time_ms: float, provider: str) -> tuple[int, int]:
    """
    Heuristic: total_tokens ≈ avg_time_ms / 1000 × tokens_per_second.
    Split 40/60 input/output as a rough average.
    """
    tps = _TOKENS_PER_SECOND.get(provider, 80.0)
    total = int((avg_time_ms / 1000.0) * tps)
    input_tokens  = int(total * 0.4)
    output_tokens = int(total * 0.6)
    return input_tokens, output_tokens


def _estimate_cost(output_tokens: int, call_count: int, provider: str) -> float:
    """USD cost estimate for all calls combined."""
    rate = _COST_PER_1K_OUTPUT.get(provider, 0.003)
    return round((output_tokens * call_count / 1000.0) * rate, 6)


# ── Abstract Adapter ───────────────────────────────────────────────────────────

class LLMCallAdapter(ABC):
    """
    Abstract adapter interface.
    Concrete adapters normalise one SDK's call graph nodes into AgentEvent.
    """

    @abstractmethod
    def can_adapt(self, full_name: str) -> bool:
        """
        Return True if *full_name* belongs to this SDK.
        Must be O(1) or O(P) where P = small constant number of patterns.
        """

    @abstractmethod
    def provider(self) -> str:
        """Return a short, stable provider identifier string."""

    @abstractmethod
    def detect_kind(self, full_name: str) -> str:
        """Classify the call as 'llm', 'tool', 'embed', or 'chain'."""

    def adapt(self, node: "CallNode") -> AgentEvent:
        """
        Normalise a CallNode → AgentEvent.
        Default implementation is shared; subclasses override provider/kind hooks.
        """
        total_ms = node.total_time * 1000.0
        avg_ms   = (node.total_time / max(node.call_count, 1)) * 1000.0
        prov     = self.provider()
        kind     = self.detect_kind(node.full_name)
        in_tok, out_tok = _estimate_tokens(avg_ms, prov)
        cost     = _estimate_cost(out_tok, node.call_count, prov)

        return AgentEvent(
            kind=kind,
            name=node.full_name,
            provider=prov,
            call_count=node.call_count,
            total_time_ms=round(total_ms, 2),
            avg_time_ms=round(avg_ms, 2),
            input_tokens_est=in_tok,
            output_tokens_est=out_tok,
            cost_usd_est=cost,
        )


# ── Concrete Adapters ──────────────────────────────────────────────────────────

class AnthropicAdapter(LLMCallAdapter):
    """Detects Anthropic SDK calls (anthropic-sdk-python)."""

    _INDICATORS: frozenset[str] = frozenset({
        "anthropic", "messages", "claude", "_legacy_api",
    })
    _TOOL_SIGNALS: frozenset[str] = frozenset({"tool_use", "tool_result"})

    def can_adapt(self, full_name: str) -> bool:
        lower = full_name.lower()
        return any(ind in lower for ind in self._INDICATORS)

    def provider(self) -> str:
        return "anthropic"

    def detect_kind(self, full_name: str) -> str:
        lower = full_name.lower()
        if any(sig in lower for sig in self._TOOL_SIGNALS):
            return "tool"
        if "embed" in lower:
            return "embed"
        return "llm"


class OpenAIAdapter(LLMCallAdapter):
    """Detects OpenAI SDK calls (openai-python)."""

    _INDICATORS: frozenset[str] = frozenset({
        "openai", "chat", "completions", "gpt",
    })
    _TOOL_SIGNALS: frozenset[str] = frozenset({"function_call", "tool_call", "tools"})

    def can_adapt(self, full_name: str) -> bool:
        lower = full_name.lower()
        return any(ind in lower for ind in self._INDICATORS)

    def provider(self) -> str:
        return "openai"

    def detect_kind(self, full_name: str) -> str:
        lower = full_name.lower()
        if any(sig in lower for sig in self._TOOL_SIGNALS):
            return "tool"
        if "embed" in lower:
            return "embed"
        return "llm"


class LangChainAdapter(LLMCallAdapter):
    """Detects LangChain / LangGraph calls."""

    _INDICATORS: frozenset[str] = frozenset({
        "langchain", "langgraph", "llmchain", "agentexecutor",
        "basechain", "runnablesequence",
    })
    _TOOL_SIGNALS: frozenset[str] = frozenset({"_run", "invoke", "basetool", "tool"})
    _LLM_SIGNALS:  frozenset[str] = frozenset({"llm", "chat_model", "generate", "predict"})

    def can_adapt(self, full_name: str) -> bool:
        lower = full_name.lower()
        return any(ind in lower for ind in self._INDICATORS)

    def provider(self) -> str:
        return "langchain"

    def detect_kind(self, full_name: str) -> str:
        lower = full_name.lower()
        if any(sig in lower for sig in self._LLM_SIGNALS):
            return "llm"
        if any(sig in lower for sig in self._TOOL_SIGNALS):
            return "tool"
        return "chain"


class LiteLLMAdapter(LLMCallAdapter):
    """Detects litellm proxy calls."""

    _INDICATORS: frozenset[str] = frozenset({"litellm", "acompletion"})

    def can_adapt(self, full_name: str) -> bool:
        lower = full_name.lower()
        return any(ind in lower for ind in self._INDICATORS)

    def provider(self) -> str:
        return "litellm"

    def detect_kind(self, full_name: str) -> str:
        return "llm" if "embed" not in full_name.lower() else "embed"


class GenericToolAdapter(LLMCallAdapter):
    """
    Fallback adapter for any function that looks like a tool call but didn't
    match a specific SDK.  Matches conservative heuristics only.
    """

    _TOOL_NAME_TOKENS: frozenset[str] = frozenset({
        "_execute", "_run", "tool_call", "run_tool", "dispatch_tool",
    })

    def can_adapt(self, full_name: str) -> bool:
        lower = full_name.lower()
        return any(tok in lower for tok in self._TOOL_NAME_TOKENS)

    def provider(self) -> str:
        return "unknown"

    def detect_kind(self, full_name: str) -> str:
        return "tool"


# ── Adapter Registry ───────────────────────────────────────────────────────────

class LLMAdapterRegistry:
    """
    Ordered list of adapters. detect() returns the first adapter whose
    can_adapt() returns True — O(A) where A = len(adapters) (currently 5).

    Concrete adapters are checked before the generic fallback, so specific
    SDK matches win over the generic tool heuristic.
    """

    def __init__(self) -> None:
        self._adapters: list[LLMCallAdapter] = [
            AnthropicAdapter(),
            OpenAIAdapter(),
            LangChainAdapter(),
            LiteLLMAdapter(),
            GenericToolAdapter(),   # fallback — must be last
        ]

    def detect(self, full_name: str) -> LLMCallAdapter | None:
        """Return the first matching adapter, or None if nothing matched."""
        for adapter in self._adapters:
            if adapter.can_adapt(full_name):
                return adapter
        return None

    def is_agent_call(self, full_name: str) -> bool:
        """Quick predicate — True if any adapter matches."""
        return self.detect(full_name) is not None


# ── Timeline builder ───────────────────────────────────────────────────────────

@dataclass
class AgentTimeline:
    """
    Ordered sequence of AgentEvents extracted from a CallGraph.
    Ordered by total_time_ms descending (costliest calls first).
    """

    events: list[AgentEvent] = field(default_factory=list)

    @property
    def total_time_ms(self) -> float:
        return sum(e.total_time_ms for e in self.events)

    @property
    def total_cost_usd(self) -> float:
        return round(sum(e.cost_usd_est for e in self.events), 6)

    @property
    def total_input_tokens(self) -> int:
        return sum(e.input_tokens_est * e.call_count for e in self.events)

    @property
    def total_output_tokens(self) -> int:
        return sum(e.output_tokens_est * e.call_count for e in self.events)

    @property
    def llm_events(self) -> list[AgentEvent]:
        return [e for e in self.events if e.kind == "llm"]

    @property
    def tool_events(self) -> list[AgentEvent]:
        return [e for e in self.events if e.kind == "tool"]


def build_agent_timeline(graph: "CallGraph") -> AgentTimeline:
    """
    Walk all graph nodes, detect LLM/tool calls via the adapter registry,
    and return an AgentTimeline sorted by total_time_ms descending.

    O(V × A) where A = number of adapters (tiny constant).
    """
    registry = LLMAdapterRegistry()
    events: list[AgentEvent] = []

    for full_name, node in graph.nodes.items():
        adapter = registry.detect(full_name)
        if adapter is not None:
            events.append(adapter.adapt(node))

    # Sort by total time descending — costliest calls surface first
    events.sort(key=lambda e: e.total_time_ms, reverse=True)
    return AgentTimeline(events=events)
