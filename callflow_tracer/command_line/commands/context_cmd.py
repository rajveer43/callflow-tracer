"""
`callflow context` command — Trace-to-LLM Context Extractor.

Runs a Python script under the tracer, ranks the functions that actually
executed by relevance to an optional query, extracts their source code, and
writes a trimmed Markdown file ready to paste into any LLM.

Usage:
    callflow-tracer context script.py
    callflow-tracer context tests/test_payment.py --query "why is charge doubled"
    callflow-tracer context app.py --top 8 --output ctx.md --no-filter

Patterns used (see _context_extractor.py):
    Strategy → WeightedRankingStrategy (scoring logic)
    Builder  → ContextBuilder (Markdown assembly)
"""

from __future__ import annotations

import sys
from argparse import ArgumentParser
from pathlib import Path

from .._utils import execute_script
from .._context_extractor import (
    ContextBuilder,
    WeightedRankingStrategy,
    extract_source,
    is_user_code,
    rank_nodes,
)
from ..interfaces.command import BaseCommand, CommandContext, CommandResult


class ContextCommand(BaseCommand):
    """Trace a script and extract minimal LLM context from what actually ran."""

    @property
    def name(self) -> str:
        return "context"

    @property
    def aliases(self) -> list[str]:
        return ["ctx"]

    @property
    def help(self) -> str:
        return "Extract minimal LLM-ready context from a traced execution"

    # ── Argument registration ──────────────────────────────────────────────

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "script",
            help="Python script or test file to trace",
        )
        parser.add_argument(
            "script_args",
            nargs="*",
            help="Arguments forwarded to the script",
        )
        parser.add_argument(
            "--query", "-q",
            default="",
            metavar="TEXT",
            help="Natural-language description of what you're debugging",
        )
        parser.add_argument(
            "--top", "-n",
            type=int,
            default=6,
            metavar="N",
            help="Number of top functions to include (default: 6)",
        )
        parser.add_argument(
            "--output", "-o",
            default="context.md",
            metavar="FILE",
            help="Output file path (default: context.md)",
        )
        parser.add_argument(
            "--no-filter",
            action="store_true",
            help="Include stdlib and vendor nodes (not recommended)",
        )
        parser.add_argument(
            "--include-args",
            action="store_true",
            help="Capture function arguments during tracing",
        )
        parser.add_argument(
            "--sampling-rate",
            type=float,
            default=1.0,
            metavar="RATE",
            help="Fraction of calls to sample (0.0–1.0, default: 1.0)",
        )

    # ── Execution ──────────────────────────────────────────────────────────

    def execute(self, ctx: CommandContext) -> CommandResult:
        from ...core.tracer import trace_scope

        args = ctx.args

        # Validate inputs
        if not Path(args.script).exists():
            return CommandResult.failure(f"Script not found: {args.script}")

        top_n = max(1, min(args.top, 30))   # clamp: 1–30

        # --- 1. Trace the script ------------------------------------------
        try:
            with trace_scope(
                None,
                include_args=args.include_args,
                sampling_rate=args.sampling_rate,
            ) as graph:
                execute_script(args.script, args.script_args)
        except SystemExit:
            pass   # script called sys.exit() — graph is still valid
        except Exception as exc:
            return CommandResult.failure(f"Script raised an exception: {exc}")

        if not graph.nodes:
            return CommandResult.failure(
                "No function calls were recorded. "
                "Make sure the script actually executes code."
            )

        # --- 2. Rank nodes via Strategy -----------------------------------
        strategy = WeightedRankingStrategy()
        ranked = rank_nodes(graph, query=args.query, top_n=top_n, strategy=strategy)

        if not ranked:
            return CommandResult.failure(
                "No user-code nodes found after filtering. "
                "Try --no-filter to include all nodes."
            )

        # --- 3. Build Markdown via Builder --------------------------------
        total_calls = sum(n.call_count for n in graph.nodes.values())
        unique_modules = {n.module for n in graph.nodes.values() if n.module}

        builder = ContextBuilder()
        builder.set_header(
            query=args.query,
            script=args.script,
            total_calls=total_calls,
            total_files=len(unique_modules),
            top_n=len(ranked),
        )

        for rank_idx, ranked_node in enumerate(ranked, start=1):
            source = extract_source(ranked_node.full_name)
            builder.add_function(
                node=ranked_node.node,
                source=source,
                score=ranked_node.score,
                depth=ranked_node.depth,
                rank=rank_idx,
            )

        builder.set_footer()
        markdown = builder.build()

        # --- 4. Write output file -----------------------------------------
        output_path = Path(args.output)
        try:
            output_path.write_text(markdown, encoding="utf-8")
        except OSError as exc:
            return CommandResult.failure(f"Could not write output file: {exc}")

        # --- 5. Print summary to stdout -----------------------------------
        _print_context_summary(
            output_path=output_path,
            ranked_count=len(ranked),
            total_calls=total_calls,
            token_estimate=builder.estimated_tokens,
        )

        return CommandResult.success(data={
            "output": str(output_path),
            "functions_shown": len(ranked),
            "total_calls": total_calls,
            "estimated_tokens": builder.estimated_tokens,
        })


# ── Private helpers ────────────────────────────────────────────────────────────

def _print_context_summary(
    output_path: Path,
    ranked_count: int,
    total_calls: int,
    token_estimate: int,
) -> None:
    """Print a concise one-block summary to stdout."""
    sep = "─" * 56
    print(f"\n{sep}")
    print(f"  callflow context — done")
    print(sep)
    print(f"  Output       : {output_path}")
    print(f"  Functions    : {ranked_count}")
    print(f"  Total calls  : {total_calls:,}")
    print(f"  Est. tokens  : ~{token_estimate:,}  (ready to paste into any LLM)")
    print(f"{sep}\n")
