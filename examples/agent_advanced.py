"""
examples/agent_advanced.py — Advanced usage of the callflow-tracer swarm agent.

Demonstrates:
  - SwarmBuilder for fine-grained control
  - Skills system: assigning specific skills to the swarm
  - Swarm hooks: subscribing to agent events programmatically
  - ProviderChain / failover: multiple LLM providers with automatic retry
  - Persistent bindings: per-cwd settings that survive between runs
  - Custom workspace skill loaded from a temp directory

Prerequisites:
  Set at least one LLM provider key in your environment:
    export ANTHROPIC_API_KEY=sk-ant-...
    export OPENAI_API_KEY=sk-...
    export GEMINI_API_KEY=AI...

Run:
  python examples/agent_advanced.py [1|2|3|4|5]
"""

from __future__ import annotations

import os
import time


# ── Example 1: SwarmBuilder — fine-grained control ────────────────────────────

def example_swarm_builder():
    """
    SwarmBuilder gives you control over parallelism, timeout, and workers.
    Useful when integrating the swarm into a larger application.
    """
    from callflow_tracer.ai.llm_provider import get_default_provider
    from callflow_tracer.agent.orchestration import SwarmBuilder

    llm = get_default_provider()

    swarm = (
        SwarmBuilder(llm)
        .with_mode("parallel")     # "sequential" for step-by-step debugging
        .with_timeout(60)          # per-agent timeout in seconds
        .with_max_workers(3)       # max threads in the pool
        .verbose()                 # print live progress
        .build()
    )

    answer = swarm.ask(
        question="Which functions in the agent system have the most complex logic?",
        cwd=os.path.dirname(os.path.dirname(__file__)),
        scope="callflow_tracer/agent/",
    )
    print(answer)


# ── Example 2: Swarm hooks — react to events programmatically ─────────────────

def example_hooks():
    """
    Subscribe to swarm lifecycle events without modifying agent code.
    HookKind values: agent_start, tool_called, tool_result, finding_ready,
                     swarm_start, swarm_complete
    """
    from callflow_tracer.ai.llm_provider import get_default_provider
    from callflow_tracer.agent.orchestration import SwarmBuilder

    llm = get_default_provider()
    swarm = SwarmBuilder(llm).with_timeout(60).build()

    # Collect events into a log
    event_log: list[dict] = []

    def on_tool_called(kind, payload):
        event_log.append({
            "event": "tool_called",
            "agent": payload["agent"],
            "tool": payload["tool"],
            "ts": time.monotonic(),
        })
        print(f"  [{payload['agent']}] called tool: {payload['tool']}")

    def on_finding(kind, payload):
        event_log.append({
            "event": "finding_ready",
            "agent": payload["agent"],
            "summary": payload["summary"][:80],
        })
        print(f"  [{payload['agent']}] finding ready: {payload['summary'][:60]}")

    answer = swarm.ask(
        question="What does the ProviderChain do and how does backoff work?",
        cwd=os.path.dirname(os.path.dirname(__file__)),
        scope="callflow_tracer/ai/",
        hooks={
            "tool_called":    on_tool_called,
            "finding_ready":  on_finding,
        },
    )

    print(f"\nCollected {len(event_log)} events during this run.")
    print(answer)


# ── Example 3: ProviderChain — automatic failover across LLM providers ────────

def example_provider_chain():
    """
    ProviderChain wraps multiple LLM providers. If the primary provider
    returns a 429 or 503, the chain automatically retries the next one
    with exponential backoff — no code changes needed in agents.
    """
    from callflow_tracer.ai.llm_provider import (
        AnthropicProvider, OpenAIProvider, GeminiProvider,
    )
    from callflow_tracer.ai.failover import ProviderChain
    from callflow_tracer.agent.orchestration import SwarmBuilder

    # Build a chain with all three providers.
    # Whichever has a valid key will respond; the others are skipped on auth error.
    chain = ProviderChain(
        providers=[
            AnthropicProvider(),
            OpenAIProvider(),
            GeminiProvider(),
        ],
        max_attempts=3,
    )

    if not chain.is_available():
        print("No LLM providers configured — set ANTHROPIC_API_KEY / OPENAI_API_KEY / GEMINI_API_KEY")
        return

    swarm = SwarmBuilder(chain).with_timeout(90).verbose().build()
    answer = swarm.ask(
        question="How does the error classifier decide between RATE_LIMIT and OVERLOADED?",
        cwd=os.path.dirname(os.path.dirname(__file__)),
        scope="callflow_tracer/ai/",
    )
    print(answer)


# ── Example 4: Persistent bindings — remember settings per project ────────────

def example_bindings():
    """
    BindingStore saves trace/scope/provider per working directory.
    On the second run the swarm picks them up automatically — no flags needed.
    """
    from callflow_tracer.agent.core.bindings import BindingStore, CwdBinding

    cwd = os.path.dirname(os.path.dirname(__file__))
    store = BindingStore()

    # Save binding for this project directory
    store.save(cwd, CwdBinding(
        scope="callflow_tracer/agent/",
        provider="anthropic",       # prefer anthropic for this project
    ))
    print(f"Saved binding for: {cwd}")

    # On the next run, ask_cmd.py automatically loads and applies this binding
    loaded = store.load(cwd)
    print(f"  scope    = {loaded.scope}")
    print(f"  provider = {loaded.provider}")
    print(f"  trace    = {loaded.trace}")

    # Merge with CLI flags — CLI wins over stored binding
    effective = store.merge(loaded, {"scope": "callflow_tracer/ai/", "provider": None})
    print(f"\nAfter merging with CLI flags:")
    print(f"  scope    = {effective.scope}")    # CLI override
    print(f"  provider = {effective.provider}")  # from binding (CLI was None)


# ── Example 5: Workspace skill — extend agent capabilities ────────────────────

def example_workspace_skill():
    """
    Drop a .py file in ~/.callflow/skills/ and it's automatically loaded
    into every swarm run. This example creates a temporary skill to show the flow.

    A real workspace skill lives at:
        ~/.callflow/skills/my_skill.py
    and exports:
        SKILLS = [Skill(name="...", tools=(...), prompt_fragment="...")]
    """
    import tempfile
    import textwrap
    from pathlib import Path
    from callflow_tracer.ai.llm_provider import get_default_provider
    from callflow_tracer.agent.orchestration import SwarmBuilder

    skill_code = textwrap.dedent("""
        from callflow_tracer.agent.skills import Skill
        from callflow_tracer.agent.tools import GrepCodebaseTool, ReadFileTool

        SKILLS = [
            Skill(
                name="DocstringAudit",
                tools=(GrepCodebaseTool(), ReadFileTool()),
                description="Audit docstring coverage across the codebase",
                prompt_fragment=(
                    "You are auditing docstring coverage. Use grep_codebase to find "
                    "functions and classes that are missing docstrings (no triple-quote "
                    "immediately after the def/class line). Report file, line, and name."
                ),
            )
        ]
    """)

    with tempfile.TemporaryDirectory() as skill_dir:
        Path(skill_dir, "docstring_audit.py").write_text(skill_code, encoding="utf-8")

        llm = get_default_provider()
        swarm = (
            SwarmBuilder(llm)
            .with_skill_dir(skill_dir)   # load skills from this dir
            .with_timeout(60)
            .verbose()
            .build()
        )

        # RouterAgent now knows about DocstringAudit and may assign it
        answer = swarm.ask(
            question="Which modules have the worst docstring coverage?",
            cwd=os.path.dirname(os.path.dirname(__file__)),
            scope="callflow_tracer/agent/",
        )
        print(answer)


# ── Run ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    examples = {
        "1": ("SwarmBuilder fine-grained control",     example_swarm_builder),
        "2": ("Swarm hooks / event subscribers",       example_hooks),
        "3": ("ProviderChain automatic failover",      example_provider_chain),
        "4": ("Persistent bindings per project",       example_bindings),
        "5": ("Workspace skill (custom capability)",   example_workspace_skill),
    }

    if len(sys.argv) > 1 and sys.argv[1] in examples:
        name, fn = examples[sys.argv[1]]
        print(f"\nRunning: {name}\n{'─' * 58}")
        fn()
    else:
        print("Usage: python examples/agent_advanced.py <number>")
        print()
        for k, (name, _) in examples.items():
            print(f"  {k}  {name}")
        print()
        print("Running example 4 (bindings — no LLM needed) by default...\n")
        example_bindings()
