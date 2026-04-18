"""
examples/agent_basic_ask.py — Basic usage of the callflow-tracer swarm agent.

Demonstrates:
  - Single-question ask via the top-level convenience function
  - Verbose mode to watch agents and tools fire in real time
  - Scoping to a subdirectory
  - Saving the answer to a Markdown report

Prerequisites:
  Set at least one LLM provider key in your environment:
    export ANTHROPIC_API_KEY=sk-ant-...
    export OPENAI_API_KEY=sk-...
    export GEMINI_API_KEY=AI...

Run:
  python examples/agent_basic_ask.py
"""

from __future__ import annotations

import os


# ── Example 1: One-liner ask ───────────────────────────────────────────────────

def example_one_liner():
    """
    The simplest possible usage — one import, one call, one answer.
    RouterAgent auto-selects which specialist agents to deploy.
    """
    from callflow_tracer.agent import ask

    answer = ask("What are the most frequently called functions in this codebase?")
    print(answer)


# ── Example 2: Verbose mode — watch the swarm work ────────────────────────────

def example_verbose():
    """
    Verbose mode prints each agent as it starts, each tool call it makes,
    and a summary table at the end (elapsed time, findings, tool calls).
    """
    from callflow_tracer.agent import ask

    answer = ask(
        "Why does the tracer use a context manager instead of a decorator?",
        verbose=True,    # prints agent progress to stdout
        mode="parallel", # default — specialists run concurrently
    )
    print("\n" + "=" * 60)
    print("ANSWER")
    print("=" * 60)
    print(answer)


# ── Example 3: Scope to a subdirectory ────────────────────────────────────────

def example_scoped():
    """
    Restrict all agent searches and traces to a subdirectory.
    Useful when you only care about one package in a monorepo.
    """
    from callflow_tracer.agent import ask

    codebase_root = os.path.dirname(os.path.dirname(__file__))

    answer = ask(
        "What tools does the GrepAgent use and how do they work?",
        scope="callflow_tracer/agent/",  # only look inside this path
        verbose=True,
    )
    print(answer)


# ── Example 4: Save answer to a Markdown file ─────────────────────────────────

def example_save_report():
    """
    The ask() function returns a plain string — write it wherever you need.
    """
    from callflow_tracer.agent import ask
    from pathlib import Path

    answer = ask(
        "List the specialist agents and describe what each one is responsible for.",
        scope="callflow_tracer/agent/",
    )

    report_path = Path(__file__).parent / "agent_report.md"
    report_path.write_text(
        f"# Agent Architecture Report\n\n{answer}\n",
        encoding="utf-8",
    )
    print(f"Report saved to: {report_path}")
    print(answer)


# ── Run ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    examples = {
        "1": ("One-liner ask",         example_one_liner),
        "2": ("Verbose mode",          example_verbose),
        "3": ("Scoped to subdirectory",example_scoped),
        "4": ("Save to Markdown",      example_save_report),
    }

    if len(sys.argv) > 1 and sys.argv[1] in examples:
        name, fn = examples[sys.argv[1]]
        print(f"\nRunning: {name}\n{'─' * 50}")
        fn()
    else:
        print("Usage: python examples/agent_basic_ask.py <number>")
        print()
        for k, (name, _) in examples.items():
            print(f"  {k}  {name}")
        print()
        print("Running example 2 (verbose) by default...\n")
        example_verbose()
