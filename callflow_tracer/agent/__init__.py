"""
`callflow_tracer.agent` — modular swarm agent system.

Public API:
  - `Swarm` / `SwarmBuilder` from `agent.orchestration`
  - `ask()` convenience entry point
"""

from __future__ import annotations

import os

from .orchestration import Swarm, SwarmBuilder

__all__ = ["Swarm", "SwarmBuilder", "ask"]


def ask(
    question: str,
    *,
    api_key: str | None = None,
    provider: str | None = None,
    scope: str | None = None,
    trace: str | None = None,
    mode: str = "parallel",
    verbose: bool = False,
    timeout: int = 120,
) -> str:
    """
    Ask a natural-language question about your codebase.

    The swarm deploys specialized agents in parallel, traces your code,
    and returns a structured answer.

    Args:
        question  : what you want to know
        api_key   : LLM provider API key (or set env var: ANTHROPIC_API_KEY /
                    OPENAI_API_KEY / GEMINI_API_KEY)
        provider  : "anthropic" | "openai" | "gemini" | "ollama"
                    (auto-detected from env if not specified)
        scope     : optional subdirectory to restrict search (e.g. "./payment/")
        trace     : optional explicit Python script to trace
        mode      : "parallel" (fast, default) | "sequential" (debug)
        verbose   : print swarm progress to stdout
        timeout   : per-agent timeout in seconds (default: 120)

    Returns:
        Structured answer string — ready to print or log.

    Raises:
        ValueError: if no LLM provider can be configured.
    """
    from ..ai.llm_provider import get_default_provider

    llm = get_default_provider(provider_name=provider)

    # Allow caller-supplied key to override env var
    if api_key and hasattr(llm, "api_key"):
        llm.api_key = api_key

    builder = SwarmBuilder(llm).with_mode(mode).with_timeout(timeout)
    if verbose:
        builder = builder.verbose()
    swarm = builder.build()

    return swarm.ask(
        question=question,
        cwd=os.getcwd(),
        scope=scope,
        trace_script=trace,
    )
