"""
orchestration/executor.py — Execution Strategy Pattern.

Two concrete strategies for running a list of specialist agents:
  ParallelExecutor   — ThreadPoolExecutor + as_completed (fast, default)
  SequentialExecutor — one agent at a time (safe, debug-friendly)

Both take identical signatures so Swarm can swap them transparently.

DSA:
  ThreadPoolExecutor : bounded thread pool, max_workers configurable
  as_completed()     : collect results as they arrive (not in-order)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from concurrent.futures import TimeoutError as FutureTimeout
from typing import TYPE_CHECKING

from ..core.context import SwarmContext
from ..core.types import NullFinding

if TYPE_CHECKING:
    from ..agents.base import BaseAgent


class ExecutorStrategy(ABC):
    """Strategy ABC for running a list of agents against a shared context."""

    @abstractmethod
    def run(
        self,
        agents: list["BaseAgent"],
        ctx: SwarmContext,
        timeout: int,
        verbose: bool,
    ) -> None:
        """Execute all agents and write findings into ctx. Never raises."""


class ParallelExecutor(ExecutorStrategy):
    """
    Submit all agents to a thread pool; collect as they complete.
    Failed agents return NullFinding — never propagate exceptions.
    """

    def __init__(self, max_workers: int = 4) -> None:
        self._max_workers = max_workers

    def run(
        self,
        agents: list["BaseAgent"],
        ctx: SwarmContext,
        timeout: int,
        verbose: bool,
    ) -> None:
        with ThreadPoolExecutor(max_workers=self._max_workers) as pool:
            future_to_name = {
                pool.submit(agent.run, ctx): agent.name
                for agent in agents
            }

            for future in as_completed(future_to_name, timeout=timeout * len(agents)):
                name = future_to_name[future]
                try:
                    finding = future.result(timeout=timeout)
                    if verbose:
                        print(f"    {name} ✓  {finding.summary[:80]}")
                except FutureTimeout:
                    ctx.set_finding(NullFinding(name, error="timed out"))
                    if verbose:
                        print(f"    {name} ✗  timed out")
                except Exception as exc:
                    ctx.set_finding(NullFinding(name, error=str(exc)))
                    if verbose:
                        print(f"    {name} ✗  {exc}")


class SequentialExecutor(ExecutorStrategy):
    """Run agents one at a time. Safer for debugging; slower than parallel."""

    def run(
        self,
        agents: list["BaseAgent"],
        ctx: SwarmContext,
        timeout: int,
        verbose: bool,
    ) -> None:
        for agent in agents:
            if verbose:
                print(f"    {agent.name} running...")
            finding = agent.run(ctx)
            if verbose:
                print(f"    {agent.name} ✓  {finding.summary[:80]}")
