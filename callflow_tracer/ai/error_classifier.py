"""
ai/error_classifier.py — Classify LLM provider exceptions into ProviderErrorKind.

Maps raw exceptions (HTTP codes, timeout errors, etc.) to a stable enum so
ProviderChain can decide cooldown policy without parsing error strings everywhere.
"""

from __future__ import annotations

from enum import Enum


class ProviderErrorKind(str, Enum):
    RATE_LIMIT = "rate_limit"   # 429 → exponential backoff, 1s→2s→4s→…→60s
    AUTH       = "auth"         # 401 → skip provider for session
    AUTH_PERM  = "auth_perm"    # 403 → skip provider permanently
    BILLING    = "billing"      # 402 → skip provider, try cheaper model
    OVERLOADED = "overloaded"   # 503 → short backoff 2s→4s
    TIMEOUT    = "timeout"      # connect/read timeout → retry same provider
    UNKNOWN    = "unknown"      # other → bubble up after N attempts


def classify(exc: Exception) -> ProviderErrorKind:
    """
    Classify a raw exception into a ProviderErrorKind.

    Inspects both the exception message and the exception type name so it works
    across provider SDKs (openai, anthropic, requests, httpx, etc.).
    """
    msg = str(exc).lower()
    exc_type = type(exc).__name__.lower()

    # Rate limit — 429
    if any(tok in msg for tok in ("429", "rate limit", "rate_limit", "too many requests", "ratelimit")):
        return ProviderErrorKind.RATE_LIMIT

    # Billing / payment — 402
    if any(tok in msg for tok in ("402", "payment required", "billing", "insufficient_quota", "quota exceeded")):
        return ProviderErrorKind.BILLING

    # Permanent auth failure — 403
    if any(tok in msg for tok in ("403", "forbidden", "permission denied", "access denied")):
        return ProviderErrorKind.AUTH_PERM

    # Session auth failure — 401
    if any(tok in msg for tok in ("401", "unauthorized", "invalid api key", "authentication", "invalid_api_key")):
        return ProviderErrorKind.AUTH

    # Overloaded / service unavailable — 503
    if any(tok in msg for tok in ("503", "overloaded", "service unavailable", "capacity", "server_error")):
        return ProviderErrorKind.OVERLOADED

    # Timeout — type name or message
    if "timeout" in exc_type or any(tok in msg for tok in ("timeout", "timed out", "read timeout", "connect timeout")):
        return ProviderErrorKind.TIMEOUT

    return ProviderErrorKind.UNKNOWN
