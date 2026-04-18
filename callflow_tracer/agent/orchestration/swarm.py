"""
orchestration/swarm.py — top-level swarm orchestrator.
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import TYPE_CHECKING, Callable

from ..agents.base import BaseAgent
from ..core.context import SwarmContext
from ..core.hooks import HookBus, HookKind, NullHookBus
from ..core.memory import JsonlMemoryStore, RunMemory
from ..skills import build_skill_registry
from ..skills.base import SkillRegistry
from .executor import ParallelExecutor, SequentialExecutor
from .registry import build_agent_registry

if TYPE_CHECKING:
    from ...ai.llm_provider import LLMProvider


class Swarm:
    """
    Orchestrates one question lifecycle:
      1) RouterAgent
      2) Specialists (parallel or sequential)
      3) SynthesizerAgent
      4) Memory append + compaction
    """

    def __init__(
        self,
        provider: "LLMProvider",
        mode: str = "parallel",
        timeout: int = 120,
        max_workers: int = 4,
        verbose: bool = False,
        plugin_dir: Path | None = None,
        skill_dir: Path | None = None,
    ) -> None:
        self._skill_registry: SkillRegistry = build_skill_registry(skill_dir=skill_dir)
        self._registry = build_agent_registry(
            provider,
            plugin_dir=plugin_dir,
            skill_registry=self._skill_registry,
        )
        self._mode = mode
        self._timeout = timeout
        self._max_workers = max_workers
        self._verbose = verbose

    def ask(
        self,
        question: str,
        cwd: str | None = None,
        scope: str | None = None,
        trace_script: str | None = None,
        hooks: dict[str, Callable] | None = None,
    ) -> str:
        """Run the full swarm pipeline and return the final answer."""
        resolved_cwd = cwd or os.getcwd()

        # Wire HookBus — verbose mode auto-subscribes printer hooks
        bus: HookBus = HookBus()
        if self._verbose:
            bus.subscribe(HookKind.TOOL_CALLED, _verbose_tool_printer)
            bus.subscribe(HookKind.FINDING_READY, _verbose_finding_printer)
        # Library caller hooks (via dict[HookKind-string, callable])
        if hooks:
            for kind_str, fn in hooks.items():
                try:
                    bus.subscribe(HookKind(kind_str), fn)
                except ValueError:
                    pass  # ignore unknown hook kind strings

        ctx = SwarmContext(
            question=question,
            cwd=resolved_cwd,
            scope=scope,
            trace_script=trace_script,
            hook_bus=bus,
        )

        bus.fire(HookKind.SWARM_START, {"question": question, "cwd": resolved_cwd})
        start = time.monotonic()
        self._run_router(ctx)
        self._run_specialists(ctx)
        self._run_synthesizer(ctx)
        elapsed = round((time.monotonic() - start) * 1000)

        answer = ctx.final_answer or "No answer could be synthesized."
        bus.fire(HookKind.SWARM_COMPLETE, {"elapsed_ms": elapsed, "answer": answer[:200]})

        if self._verbose:
            _print_swarm_summary(ctx, elapsed)

        # Persist memory and compact if needed
        try:
            store = JsonlMemoryStore(resolved_cwd)
            store.append(RunMemory(
                question=question,
                answer=answer,
                findings={
                    name: f.summary for name, f in ctx.findings.items() if not f.is_null
                },
                cwd=resolved_cwd,
                scope=scope,
                trace_script=trace_script,
                elapsed_ms=elapsed,
            ))
            store.compact()
        except Exception:
            pass  # memory failures must never surface to the caller

        return answer

    # ── Pipeline stages ────────────────────────────────────────────────────

    def _run_router(self, ctx: SwarmContext) -> None:
        self._log("RouterAgent dispatching...")
        router = self._registry["RouterAgent"]
        router.run(ctx)
        if ctx.dispatch_plan:
            self._log(f"  → {ctx.dispatch_plan.agent_names()} ({ctx.dispatch_plan.mode} mode)")
        else:
            self._log("  → Router produced no plan; defaulting to all specialists")

    def _run_specialists(self, ctx: SwarmContext) -> None:
        if not ctx.dispatch_plan:
            agent_names = ["ContextAgent", "GrepAgent"]
            tasks_by_name = {}
        else:
            agent_names = [n for n in ctx.dispatch_plan.agent_names() if n in self._registry]
            tasks_by_name = {t.agent_name: t for t in ctx.dispatch_plan.tasks}

        if not agent_names:
            return

        # Inject skills + extra tools into each agent before handing to executor.
        # This runs in the main thread — agents are not yet running in parallel.
        for name in agent_names:
            task = tasks_by_name.get(name)
            if task is not None:
                self._registry[name].configure_from_task(task, self._skill_registry)

        agents: list[BaseAgent] = [self._registry[n] for n in agent_names]
        if self._mode == "parallel":
            executor = ParallelExecutor(max_workers=self._max_workers)
        else:
            executor = SequentialExecutor()
        executor.run(agents=agents, ctx=ctx, timeout=self._timeout, verbose=self._verbose)

    def _run_synthesizer(self, ctx: SwarmContext) -> None:
        active = ctx.active_findings()
        self._log(f"SynthesizerAgent merging {len(active)} finding(s)...")
        self._registry["SynthesizerAgent"].run(ctx)

    def _log(self, message: str) -> None:
        if self._verbose:
            print(f"  {message}")


# ── Hook callbacks for verbose mode ───────────────────────────────────────────

def _verbose_tool_printer(kind: HookKind, payload: dict) -> None:
    agent = payload.get("agent", "?")
    tool  = payload.get("tool", "?")
    print(f"    [{agent}] → {tool}")


def _verbose_finding_printer(kind: HookKind, payload: dict) -> None:
    agent   = payload.get("agent", "?")
    summary = payload.get("summary", "")[:80]
    print(f"    [{agent}] finding: {summary}")


def _print_swarm_summary(ctx: SwarmContext, elapsed_ms: int) -> None:
    active = ctx.active_findings()
    failed = [name for name, finding in ctx.findings.items() if finding.is_null]
    tool_calls = sum(len(f.tool_calls_made) for f in active)
    thin = "─" * 58
    print(f"\n{thin}")
    print(f"  Swarm complete in {elapsed_ms}ms")
    print(f"  Active findings : {len(active)}")
    print(f"  Failed agents   : {failed or 'none'}")
    print(f"  Tool calls made : {tool_calls}")
    print(f"  Audit messages  : {len(ctx.messages)}")
    print(f"{thin}\n")
