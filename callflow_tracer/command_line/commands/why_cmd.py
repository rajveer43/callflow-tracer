"""
`callflow why` command — Call Chain Explainer.

Answers: "Why / how is this function being called?"

Given a function name (full or partial), it builds a reverse call graph from
a trace and uses BFS to discover every unique call chain that leads to that
function — printed as indented trees with call counts, shortest chain first.

Usage:
    # Trace inline and answer immediately
    callflow-tracer why charge_customer --trace tests/test_payment.py

    # Re-use a previously saved JSON trace
    callflow-tracer why payment.processor.charge_customer --from trace.json

    # Limit output
    callflow-tracer why apply_fee --trace app.py --max-chains 5

DSA used (see _call_graph_analyzer.py):
    Reverse adjacency list    : dict[str, list[str]]  — O(E) build
    BFS with frozenset states : O(V + E) traversal, O(1) cycle check per hop
    set[str]                  : O(1) visited / dedup
"""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from .._utils import execute_script, load_graph_from_json
from .._call_graph_analyzer import (
    build_reverse_graph,
    find_call_chains,
    format_chain_as_tree,
    group_chains_by_root,
    resolve_target_names,
)
from ..interfaces.command import BaseCommand, CommandContext, CommandResult


class WhyCommand(BaseCommand):
    """Show every call chain that leads to a given function."""

    @property
    def name(self) -> str:
        return "why"

    @property
    def aliases(self) -> list[str]:
        return []

    @property
    def help(self) -> str:
        return "Show all call chains leading to a function (BFS, shortest first)"

    # ── Argument registration ──────────────────────────────────────────────

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "function_name",
            help="Function to investigate (full or partial name, e.g. 'charge_customer')",
        )
        # Mutually exclusive trace sources
        source_group = parser.add_mutually_exclusive_group(required=True)
        source_group.add_argument(
            "--trace", "-t",
            metavar="SCRIPT",
            help="Python script to trace live (runs the script first)",
        )
        source_group.add_argument(
            "--from", "-f",
            dest="from_file",
            metavar="FILE",
            help="Load a previously saved JSON trace file",
        )
        parser.add_argument(
            "--max-chains",
            type=int,
            default=20,
            metavar="N",
            help="Maximum number of chains to show (default: 20)",
        )
        parser.add_argument(
            "--max-depth",
            type=int,
            default=12,
            metavar="D",
            help="Maximum chain depth to explore (default: 12)",
        )
        parser.add_argument(
            "trace_args",
            nargs="*",
            help="Extra arguments forwarded to --trace script",
        )

    # ── Execution ──────────────────────────────────────────────────────────

    def execute(self, ctx: CommandContext) -> CommandResult:
        args = ctx.args

        # --- 1. Obtain the call graph -------------------------------------
        graph, load_err = _load_graph(args)
        if load_err:
            return CommandResult.failure(load_err)

        if not graph.nodes:
            return CommandResult.failure("Trace produced no call nodes.")

        # --- 2. Resolve target function name ------------------------------
        candidates = resolve_target_names(graph, args.function_name)
        if not candidates:
            known_sample = ", ".join(list(graph.nodes)[:5])
            return CommandResult.failure(
                f"Function '{args.function_name}' not found in the trace.\n"
                f"  Sample recorded functions: {known_sample} ..."
            )

        target = _pick_best_candidate(candidates, args.function_name)

        # --- 3. Build reverse graph + BFS ---------------------------------
        reverse_graph = build_reverse_graph(graph)
        chains = find_call_chains(
            reverse_graph,
            target=target,
            max_chains=args.max_chains,
            max_depth=args.max_depth,
        )

        if not chains:
            print(f"\n  '{target}' has no recorded callers — it may be an entry point.\n")
            return CommandResult.success(data={"target": target, "chains": 0})

        # --- 4. Render output ---------------------------------------------
        _print_why_report(target, chains, graph)

        return CommandResult.success(data={
            "target": target,
            "chains": len(chains),
            "unique_roots": len({c.root for c in chains}),
        })


# ── Private helpers ────────────────────────────────────────────────────────────

def _load_graph(args):
    """
    Return (CallGraph, error_string).
    Loads from a live trace or a JSON file depending on args.
    """
    from ...core.tracer import trace_scope

    if getattr(args, "from_file", None):
        fpath = args.from_file
        if not Path(fpath).exists():
            return None, f"Trace file not found: {fpath}"
        try:
            return load_graph_from_json(fpath), None
        except Exception as exc:
            return None, f"Failed to load trace file: {exc}"

    script = args.trace
    if not Path(script).exists():
        return None, f"Script not found: {script}"

    try:
        with trace_scope(None) as graph:
            execute_script(script, getattr(args, "trace_args", []) or [])
    except SystemExit:
        pass
    except Exception as exc:
        return None, f"Script raised an exception: {exc}"

    return graph, None


def _pick_best_candidate(candidates: list[str], partial: str) -> str:
    """
    From a list of matching full_names, return the best match:
      1. Exact match wins.
      2. Shortest name (fewest dots) as tie-breaker — avoids deeply nested duplicates.
    """
    for name in candidates:
        if name == partial:
            return name
    return min(candidates, key=lambda n: (len(n.split(".")), n))


def _print_why_report(target: str, chains, graph) -> None:
    """Print the full call-chain report to stdout."""
    sep = "═" * 60
    thin = "─" * 60

    print(f"\n{sep}")
    print(f"  callflow why  →  {target}")
    print(f"  {len(chains)} call chain(s) found")
    print(f"{sep}\n")

    groups = group_chains_by_root(chains)
    chain_idx = 1

    for root, root_chains in groups.items():
        for chain in root_chains:
            tree = format_chain_as_tree(chain, graph, chain_idx)
            print(tree)
            print()
            chain_idx += 1

    print(thin)
    unique_roots = len(groups)
    deepest = max(c.depth for c in chains)
    print(
        f"  {len(chains)} chain(s) from {unique_roots} unique entry point(s) | "
        f"deepest: {deepest} hop(s)"
    )
    print(f"{thin}\n")
