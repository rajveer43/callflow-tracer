"""CLI subcommands: otel, export."""

import argparse
import os
import sys
import traceback
from pathlib import Path

from ._utils import load_graph_from_json
from ..observability.opentelemetry_exporter import (
    export_callgraph_to_otel,
    export_callgraph_with_metrics,
    OpenTelemetryNotAvailable,
)
from ..observability.otel_config import OTelConfig, create_example_config
from ..visualization.exporter import export_html, export_json, export_html_3d


# ── Parser registration ────────────────────────────────────────────────────────

def add_otel_parser(subparsers) -> None:
    p = subparsers.add_parser(
        "otel", help="Advanced OpenTelemetry export with exemplars and sampling"
    )
    p.add_argument("input", nargs="?", help="Input trace file (JSON)")
    p.add_argument("--config", help="OTel config file (.yaml or .json)")
    p.add_argument("--service-name", help="Service name (overrides config)")
    p.add_argument("--environment", default="production",
                   help="Environment (production/staging/dev)")
    p.add_argument("--sampling-rate", type=float, default=1.0,
                   help="Sampling rate (0.0-1.0)")
    p.add_argument("--include-metrics", action="store_true",
                   help="Link custom metrics as exemplars")
    p.add_argument("--metrics-file", help="Path to metrics JSON file for exemplars")
    p.add_argument("--init-config", action="store_true",
                   help="Create example config file")


def add_export_parser(subparsers) -> None:
    p = subparsers.add_parser(
        "export",
        help="Export trace data to different formats (HTML/JSON/3D/OpenTelemetry)",
    )
    p.add_argument("input", help="Input trace file (JSON)")
    p.add_argument("-o", "--output", required=False,
                   help="Output file path (not used for otel)")
    p.add_argument("--format", choices=["html", "json", "3d", "otel"], required=True,
                   help="Output format")
    p.add_argument("--title", help="Title for the visualization")
    p.add_argument("--service-name",
                   help="Service name for OpenTelemetry export")


# ── Handlers ──────────────────────────────────────────────────────────────────

def handle_otel(args) -> int:
    if args.init_config:
        try:
            create_example_config(".callflow_otel.yaml")
            print("Example OTel config created: .callflow_otel.yaml")
            return 0
        except Exception as e:
            print(f"Error creating config: {e}", file=sys.stderr)
            return 1

    if not args.input:
        print("Error: input file is required unless --init-config is set", file=sys.stderr)
        return 1

    print("Exporting to OpenTelemetry (advanced mode)")
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
            import json
            try:
                with open(args.metrics_file, "r") as f:
                    metrics_data = json.load(f)
                result = export_callgraph_with_metrics(
                    graph, metrics_data,
                    service_name=config.get("service_name"),
                    resource_attributes=config.get("resource_attributes"),
                )
            except FileNotFoundError:
                print(f"Warning: Metrics file not found: {args.metrics_file}",
                      file=sys.stderr)
                result = export_callgraph_to_otel(
                    graph,
                    service_name=config.get("service_name"),
                    resource_attributes=config.get("resource_attributes"),
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

        print(f"\n=== OTel Export Summary ===")
        print(f"Status: {result.get('status')}")
        print(f"Spans exported: {result.get('span_count')}")
        print(f"Exemplars linked: {result.get('exemplar_count')}")
        print(f"Service: {result.get('service_name')}")
        print(f"Environment: {result.get('environment')}")
        print(f"Sampling rate: {result.get('sampling_rate')}")
        print(f"\nConfig used: {config.config_path or 'defaults + env vars'}")
        return 0

    except OpenTelemetryNotAvailable as e:
        print(str(e), file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error exporting to OTel: {e}", file=sys.stderr)
        traceback.print_exc()
        return 1


def handle_export(args) -> int:
    print(f"Exporting {args.input} to {args.format} format")
    try:
        graph = load_graph_from_json(args.input)
        title = args.title or f"Exported: {Path(args.input).name}"

        if args.format == "html":
            if not args.output:
                print("Error: --output is required for HTML export", file=sys.stderr)
                return 1
            export_html(graph, args.output, title=title)
            print(f"Exported to: {args.output}")

        elif args.format == "3d":
            if not args.output:
                print("Error: --output is required for 3D export", file=sys.stderr)
                return 1
            export_html_3d(graph, args.output, title=title)
            print(f"Exported to: {args.output}")

        elif args.format == "json":
            if not args.output:
                print("Error: --output is required for JSON export", file=sys.stderr)
                return 1
            export_json(graph, args.output)
            print(f"Exported to: {args.output}")

        elif args.format == "otel":
            service_name = args.service_name or os.getenv(
                "CALLFLOW_OTEL_SERVICE_NAME", "callflow-tracer"
            )
            print(f"Exporting call graph to OpenTelemetry (service_name={service_name})")
            try:
                export_callgraph_to_otel(graph, service_name=service_name)
            except OpenTelemetryNotAvailable as e:
                print(str(e), file=sys.stderr)
                return 1
            print("OpenTelemetry export completed.")

        return 0

    except Exception as e:
        print(f"Error exporting: {e}", file=sys.stderr)
        traceback.print_exc()
        return 1
