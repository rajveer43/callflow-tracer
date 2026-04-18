"""Concrete commands: otel, export."""

from __future__ import annotations

import os
import traceback as tb
from argparse import ArgumentParser
from pathlib import Path

from .._utils import load_graph_from_json
from ..interfaces.command import BaseCommand, CommandContext, CommandResult


class OtelCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "otel"

    @property
    def help(self) -> str:
        return "Advanced OpenTelemetry export with exemplars and sampling"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("input", nargs="?", help="Input trace file (JSON)")
        parser.add_argument("--config")
        parser.add_argument("--service-name")
        parser.add_argument("--environment", default="production")
        parser.add_argument("--sampling-rate", type=float, default=1.0)
        parser.add_argument("--include-metrics", action="store_true")
        parser.add_argument("--metrics-file")
        parser.add_argument("--init-config", action="store_true")

    def execute(self, ctx: CommandContext) -> CommandResult:
        import json
        from ...observability.opentelemetry_exporter import (
            export_callgraph_to_otel, export_callgraph_with_metrics,
            OpenTelemetryNotAvailable,
        )
        from ...observability.otel_config import OTelConfig, create_example_config

        args = ctx.args
        if args.init_config:
            try:
                create_example_config(".callflow_otel.yaml")
                print("Config created: .callflow_otel.yaml")
                return CommandResult.success()
            except Exception as e:
                return CommandResult.failure(str(e))

        if not args.input:
            return CommandResult.failure("input file required unless --init-config is set")

        try:
            config = OTelConfig(args.config)
            config.load_from_env()
            if args.service_name:
                config.config["service_name"] = args.service_name
            if args.environment:
                config.config["environment"] = args.environment
            if args.sampling_rate:
                config.config["sampling_rate"] = args.sampling_rate

            graph = load_graph_from_json(args.input)

            if args.include_metrics and args.metrics_file:
                try:
                    with open(args.metrics_file, "r") as f:
                        metrics_data = json.load(f)
                    result = export_callgraph_with_metrics(
                        graph, metrics_data,
                        service_name=config.get("service_name"),
                        resource_attributes=config.get("resource_attributes"),
                    )
                except FileNotFoundError:
                    print(f"Warning: metrics file not found: {args.metrics_file}")
                    result = export_callgraph_to_otel(
                        graph,
                        service_name=config.get("service_name"),
                        sampling_rate=config.get("sampling_rate"),
                        environment=config.get("environment"),
                    )
            else:
                result = export_callgraph_to_otel(
                    graph,
                    service_name=config.get("service_name"),
                    resource_attributes=config.get("resource_attributes"),
                    sampling_rate=config.get("sampling_rate"),
                    environment=config.get("environment"),
                )

            print(f"\n=== OTel Export ===")
            for k in ("status", "span_count", "exemplar_count", "service_name", "environment"):
                print(f"  {k}: {result.get(k)}")

            return CommandResult.success(data=result)

        except OpenTelemetryNotAvailable as e:
            return CommandResult.failure(str(e))
        except Exception as e:
            tb.print_exc()
            return CommandResult.failure(str(e))


class ExportCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "export"

    @property
    def help(self) -> str:
        return "Export trace data to HTML / JSON / 3D / OpenTelemetry"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("input", help="Input trace file (JSON)")
        parser.add_argument("-o", "--output")
        parser.add_argument("--format", choices=["html", "json", "3d", "otel"], required=True)
        parser.add_argument("--title")
        parser.add_argument("--service-name")

    def execute(self, ctx: CommandContext) -> CommandResult:
        from ...visualization.exporter import export_html, export_json, export_html_3d
        from ...observability.opentelemetry_exporter import (
            export_callgraph_to_otel, OpenTelemetryNotAvailable,
        )

        args = ctx.args
        try:
            graph = load_graph_from_json(args.input)
            title = args.title or f"Exported: {Path(args.input).name}"

            if args.format in ("html", "json", "3d") and not args.output:
                return CommandResult.failure(f"--output is required for {args.format} format")

            if args.format == "html":
                export_html(graph, args.output, title=title)
            elif args.format == "3d":
                export_html_3d(graph, args.output, title=title)
            elif args.format == "json":
                export_json(graph, args.output)
            elif args.format == "otel":
                svc = args.service_name or os.getenv("CALLFLOW_OTEL_SERVICE_NAME", "callflow-tracer")
                try:
                    export_callgraph_to_otel(graph, service_name=svc)
                    print("OpenTelemetry export completed.")
                    return CommandResult.success()
                except OpenTelemetryNotAvailable as e:
                    return CommandResult.failure(str(e))

            print(f"Exported to: {args.output}")
            return CommandResult.success()

        except Exception as e:
            tb.print_exc()
            return CommandResult.failure(str(e))
