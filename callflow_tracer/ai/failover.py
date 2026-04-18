"""
ai/failover.py — ProviderChain: chain-of-responsibility LLM failover.

Wraps a list[LLMProvider] and implements LLMProvider so it is a drop-in
replacement. Tries each provider slot in order; applies per-slot cooldowns
on failure; raises ProviderChainExhaustedError only when ALL slots fail.

Design patterns:
  Chain of Responsibility — ProviderChain.generate() iterates slots in order
  Strategy               — ExponentialBackoff vs PermanentSkip via ProviderErrorKind
  Null Object            — NullProvider returned when all slots exhausted

DSA:
  collections.deque[ProviderSlot] — O(1) iteration; round-trip friendly
  time.monotonic() floats         — O(1) cooldown comparison, no datetime overhead
  min(base * 2**n, cap)           — capped exponential backoff
"""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from typing import Optional

from .error_classifier import ProviderErrorKind, classify
from .llm_provider import LLMProvider

# Backoff parameters
_RATE_LIMIT_BASE  = 1.0
_OVERLOAD_BASE    = 2.0
_BACKOFF_CAP      = 60.0
_SESSION_SKIP     = 86_400.0  # 24 h — effectively "skip for session"


class ProviderChainExhaustedError(RuntimeError):
    """Raised when all ProviderSlots are unavailable or have failed."""


@dataclass
class ProviderSlot:
    """Wraps one LLMProvider with its failure state."""

    provider: LLMProvider
    cooldown_until: float = 0.0   # monotonic timestamp
    fail_count: int = 0
    permanent_skip: bool = False

    def is_available(self) -> bool:
        return not self.permanent_skip and time.monotonic() >= self.cooldown_until

    def apply_backoff(self, kind: ProviderErrorKind) -> None:
        """Update cooldown state based on the classified error kind."""
        now = time.monotonic()
        self.fail_count += 1

        if kind == ProviderErrorKind.RATE_LIMIT:
            delay = min(_RATE_LIMIT_BASE * (2 ** (self.fail_count - 1)), _BACKOFF_CAP)
            self.cooldown_until = now + delay

        elif kind == ProviderErrorKind.OVERLOADED:
            delay = min(_OVERLOAD_BASE * (2 ** (self.fail_count - 1)), _BACKOFF_CAP)
            self.cooldown_until = now + delay

        elif kind in (ProviderErrorKind.AUTH, ProviderErrorKind.BILLING):
            # Skip for the rest of this session
            self.cooldown_until = now + _SESSION_SKIP

        elif kind == ProviderErrorKind.AUTH_PERM:
            self.permanent_skip = True

        # TIMEOUT / UNKNOWN: no cooldown — retry same provider on next attempt


class ProviderChain(LLMProvider):
    """
    Wraps list[LLMProvider] — implements LLMProvider interface so it is a
    drop-in replacement anywhere an LLMProvider is accepted.

    On each generate() call:
      1. Iterates available (non-cooled) slots in order.
      2. First successful response is returned immediately.
      3. On failure, classifies the exception and applies the matching
         cooldown policy to that slot.
      4. When all slots fail or are cooled, raises ProviderChainExhaustedError.
    """

    def __init__(self, providers: list[LLMProvider], max_attempts: int = 3) -> None:
        self._slots: deque[ProviderSlot] = deque(
            ProviderSlot(provider=p) for p in providers
        )
        self._max_attempts = max_attempts

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """Try each available slot in order. First success wins."""
        last_exc: Exception | None = None
        attempts = 0

        for slot in list(self._slots):
            if not slot.is_available():
                continue
            if attempts >= self._max_attempts:
                break
            attempts += 1
            try:
                return slot.provider.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            except Exception as exc:
                last_exc = exc
                kind = classify(exc)
                slot.apply_backoff(kind)

        if last_exc is not None:
            raise ProviderChainExhaustedError(
                f"All LLM providers failed. Last error: {last_exc}"
            ) from last_exc
        raise ProviderChainExhaustedError(
            "No LLM providers are currently available (all cooled down or exhausted)."
        )

    def is_available(self) -> bool:
        return any(s.is_available() for s in self._slots)


class NullProvider(LLMProvider):
    """
    Null Object — used when all providers are exhausted.
    Returns a bounded error string instead of raising.
    """

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        return (
            "[ERROR: All LLM providers are unavailable. "
            "Check your API keys and rate limits.]"
        )

    def is_available(self) -> bool:
        return False
