"""
CallFlow Tracer - production facade.

The implementation now lives in domain packages under:
- `callflow_tracer.core`
- `callflow_tracer.visualization`
- `callflow_tracer.performance`
- `callflow_tracer.analysis`
- `callflow_tracer.observability`
- `callflow_tracer.funnel`
- `callflow_tracer.benchmark`
- `callflow_tracer.integrations`
"""

__version__ = "0.6.0"
__author__ = "Rajveer Rathod"
__email__ = "rathodrajveer1311@gmail.com"

# callflow-tracer-origin:rajveer43
# Original repository: https://github.com/rajveer43/callflow-tracer
# Licensed under MIT — see LICENSE for details.

from .core import *  # noqa: F401,F403
from .visualization import *  # noqa: F401,F403
from .performance import *  # noqa: F401,F403
from .analysis import *  # noqa: F401,F403
from .observability import *  # noqa: F401,F403
from .benchmark import *  # noqa: F401,F403
from .integrations import *  # noqa: F401,F403
from .funnel import *  # noqa: F401,F403


def trace_and_export(output_file: str, include_args: bool = False):
    """Convenience wrapper that mirrors the legacy top-level helper."""
    return trace_scope(output_file, include_args)


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

    Deploys a swarm of specialized agents (ContextAgent, WhyAgent, CostAgent,
    GrepAgent) in parallel, then synthesizes their findings into one answer.

    Args:
        question  : what you want to know
        api_key   : LLM API key (or set ANTHROPIC_API_KEY / OPENAI_API_KEY)
        provider  : "anthropic" | "openai" | "gemini" | "ollama"
        scope     : optional subdirectory to restrict search
        trace     : optional explicit Python script to trace
        mode      : "parallel" (fast) | "sequential" (debug)
        verbose   : print swarm progress
        timeout   : per-agent timeout seconds

    Example::

        from callflow_tracer import ask
        print(ask("why is my checkout slow?", api_key="sk-ant-...", provider="anthropic"))
    """
    from .agent import ask as _ask
    return _ask(
        question,
        api_key=api_key,
        provider=provider,
        scope=scope,
        trace=trace,
        mode=mode,
        verbose=verbose,
        timeout=timeout,
    )
