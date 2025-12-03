#!/usr/bin/env python3
"""
Command-line interface for callflow-tracer.

This module provides a comprehensive CLI for all callflow-tracer features.
"""

import sys
import os
import argparse
import json
from pathlib import Path
from typing import Dict
from . import __version__
from .tracer import trace_scope, CallGraph, CallNode, CallEdge
from .exporter import export_html, export_json, export_html_3d
from .opentelemetry_exporter import export_callgraph_to_otel, export_callgraph_with_metrics, OpenTelemetryNotAvailable
from .otel_config import OTelConfig, create_example_config
from .flamegraph import generate_flamegraph
from .comparison import compare_graphs, export_comparison_html
from .memory_leak_detector import MemoryLeakDetector, get_top_memory_consumers
from .profiling import get_memory_usage
from .code_quality import analyze_codebase, ComplexityAnalyzer, MaintainabilityAnalyzer, TechnicalDebtAnalyzer, QualityTrendAnalyzer
from .predictive_analysis import PerformancePredictor, CapacityPlanner, ScalabilityAnalyzer, ResourceForecaster, generate_predictive_report
from .code_churn import CodeChurnAnalyzer, ChurnCorrelationAnalyzer, generate_churn_report


class CallflowCLI:
    """Main CLI handler for callflow-tracer."""
    
    def __init__(self):
        self.parser = self._create_parser()
    
    def _create_parser(self):
        """Create the argument parser with all subcommands."""
        parser = argparse.ArgumentParser(
            prog='callflow-tracer',
            description='CallFlow Tracer - Visualize and analyze Python function call flows',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  callflow-tracer trace script.py -o output.html
  callflow-tracer flamegraph script.py -o flamegraph.html
  callflow-tracer memory-leak script.py --threshold 10
  callflow-tracer compare trace1.json trace2.json -o comparison.html
  callflow-tracer profile script.py -o profile.html

For more information: https://github.com/rajveer43/callflow-tracer
            """
        )
        
        parser.add_argument('--version', action='version', version=f'callflow-tracer {__version__}')
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Trace command
        self._add_trace_parser(subparsers)
        self._add_flamegraph_parser(subparsers)
        self._add_profile_parser(subparsers)
        self._add_memory_leak_parser(subparsers)
        self._add_compare_parser(subparsers)
        self._add_export_parser(subparsers)
        self._add_info_parser(subparsers)
        
        # New analysis commands
        self._add_quality_parser(subparsers)
        self._add_predict_parser(subparsers)
        self._add_churn_parser(subparsers)
        
        # OpenTelemetry commands
        self._add_otel_parser(subparsers)
        
        return parser
    
    def _add_trace_parser(self, subparsers):
        """Add trace subcommand parser."""
        trace_parser = subparsers.add_parser('trace', help='Trace function calls in a Python script')
        trace_parser.add_argument('script', help='Python script to trace')
        trace_parser.add_argument('script_args', nargs='*', help='Arguments to pass to the script')
        trace_parser.add_argument('-o', '--output', default='callflow_trace.html', help='Output file path')
        trace_parser.add_argument('--format', choices=['html', 'json', 'both'], default='html', help='Output format')
        trace_parser.add_argument('--3d', dest='three_d', action='store_true', help='Generate 3D visualization')
        trace_parser.add_argument('--title', help='Title for the visualization')
        trace_parser.add_argument('--include-args', action='store_true', help='Include function arguments')
        trace_parser.add_argument('--no-browser', action='store_true', help='Do not open browser')
    
    def _add_flamegraph_parser(self, subparsers):
        """Add flamegraph subcommand parser."""
        fg_parser = subparsers.add_parser('flamegraph', help='Generate flamegraph from traced script')
        fg_parser.add_argument('script', help='Python script to trace')
        fg_parser.add_argument('script_args', nargs='*', help='Arguments to pass to the script')
        fg_parser.add_argument('-o', '--output', default='flamegraph.html', help='Output HTML file path')
        fg_parser.add_argument('--title', help='Title for the flamegraph')
        fg_parser.add_argument('--min-time', type=float, default=0.0, help='Minimum time threshold (ms)')
        fg_parser.add_argument('--no-browser', action='store_true', help='Do not open browser')
    
    def _add_profile_parser(self, subparsers):
        """Add profile subcommand parser."""
        prof_parser = subparsers.add_parser('profile', help='Profile script performance')
        prof_parser.add_argument('script', help='Python script to profile')
        prof_parser.add_argument('script_args', nargs='*', help='Arguments to pass to the script')
        prof_parser.add_argument('-o', '--output', default='profile.html', help='Output file path')
        prof_parser.add_argument('--format', choices=['html', 'json', 'text'], default='html')
        prof_parser.add_argument('--memory', action='store_true', help='Include memory profiling')
        prof_parser.add_argument('--cpu', action='store_true', help='Include CPU profiling')
        prof_parser.add_argument('--no-browser', action='store_true', help='Do not open browser')
    
    def _add_memory_leak_parser(self, subparsers):
        """Add memory-leak subcommand parser."""
        mem_parser = subparsers.add_parser('memory-leak', help='Detect memory leaks in a script')
        mem_parser.add_argument('script', help='Python script to analyze')
        mem_parser.add_argument('script_args', nargs='*', help='Arguments to pass to the script')
        mem_parser.add_argument('-o', '--output', default='memory_leak_report.html', help='Output file')
        mem_parser.add_argument('--threshold', type=float, default=5.0, help='Memory growth threshold (MB)')
        mem_parser.add_argument('--interval', type=float, default=0.1, help='Sampling interval (seconds)')
        mem_parser.add_argument('--top', type=int, default=10, help='Top memory consumers to show')
        mem_parser.add_argument('--no-browser', action='store_true', help='Do not open browser')
    
    def _add_compare_parser(self, subparsers):
        """Add compare subcommand parser."""
        cmp_parser = subparsers.add_parser('compare', help='Compare two trace files')
        cmp_parser.add_argument('file1', help='First trace file (JSON)')
        cmp_parser.add_argument('file2', help='Second trace file (JSON)')
        cmp_parser.add_argument('-o', '--output', default='comparison.html', help='Output HTML file')
        cmp_parser.add_argument('--label1', default='Trace 1', help='Label for first trace')
        cmp_parser.add_argument('--label2', default='Trace 2', help='Label for second trace')
        cmp_parser.add_argument('--no-browser', action='store_true', help='Do not open browser')
    
    def _add_export_parser(self, subparsers):
        """Add export subcommand parser."""
        exp_parser = subparsers.add_parser('export', help='Export trace data to different formats (HTML/JSON/3D/OpenTelemetry)')
        exp_parser.add_argument('input', help='Input trace file (JSON)')
        exp_parser.add_argument('-o', '--output', required=False, help='Output file path (not used for otel)')
        exp_parser.add_argument('--format', choices=['html', 'json', '3d', 'otel'], required=True, help='Output format')
        exp_parser.add_argument('--title', help='Title for the visualization')
        exp_parser.add_argument('--service-name', help='Service name to use for OpenTelemetry export (overrides CALLFLOW_OTEL_SERVICE_NAME)')
    
    def _add_info_parser(self, subparsers):
        """Add info subcommand parser."""
        info_parser = subparsers.add_parser('info', help='Show information about a trace file')
        info_parser.add_argument('file', help='Trace file to analyze (JSON)')
        info_parser.add_argument('--detailed', action='store_true', help='Show detailed statistics')
    
    def run(self, args=None):
        """Run the CLI with the given arguments."""
        parsed_args = self.parser.parse_args(args)
        
        if not parsed_args.command:
            self.parser.print_help()
            return 1
        
        handler_name = f'_handle_{parsed_args.command.replace("-", "_")}'
        handler = getattr(self, handler_name, None)
        
        if handler:
            try:
                return handler(parsed_args)
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
                if '--debug' in sys.argv:
                    import traceback
                    traceback.print_exc()
                return 1
        else:
            print(f"Unknown command: {parsed_args.command}", file=sys.stderr)
            return 1
    
    def _execute_script(self, script_path, script_args):
        """Execute a Python script with given arguments."""
        original_argv = sys.argv
        sys.argv = [script_path] + script_args
        
        try:
            script_globals = {
                '__name__': '__main__',
                '__file__': script_path,
            }
            with open(script_path, 'r') as f:
                code = compile(f.read(), script_path, 'exec')
                exec(code, script_globals)
        finally:
            sys.argv = original_argv
    
    def _open_browser(self, filepath):
        """Open a file in the default web browser."""
        import webbrowser
        abs_path = os.path.abspath(filepath)
        webbrowser.open(f'file://{abs_path}')
    
    def _handle_trace(self, args):
        """Handle trace command."""
        print(f"Tracing script: {args.script}")
        
        try:
            title = args.title or f"Call Flow: {Path(args.script).name}"
            
            with trace_scope(None, include_args=args.include_args) as graph:
                self._execute_script(args.script, args.script_args)
            
            if args.format in ['html', 'both']:
                html_path = args.output if args.format == 'html' else args.output.replace('.json', '.html')
                if args.three_d:
                    export_html_3d(graph, html_path, title=title)
                    print(f"3D visualization saved to: {html_path}")
                else:
                    export_html(graph, html_path, title=title)
                    print(f"HTML visualization saved to: {html_path}")
                
                if not args.no_browser:
                    self._open_browser(html_path)
            
            if args.format in ['json', 'both']:
                json_path = args.output if args.format == 'json' else args.output.replace('.html', '.json')
                export_json(graph, json_path)
                print(f"JSON trace saved to: {json_path}")
            
            print(f"\nTrace Summary:")
            print(f"  Total nodes: {len(graph.nodes)}")
            print(f"  Total edges: {len(graph.edges)}")
            print(f"  Total calls: {sum(node.call_count for node in graph.nodes.values())}")
            
            return 0
            
        except FileNotFoundError:
            print(f"Error: Script not found: {args.script}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Error executing script: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1
    
    def _handle_flamegraph(self, args):
        """Handle flamegraph command."""
        print(f"Generating flamegraph for: {args.script}")
        
        try:
            with trace_scope(None) as graph:
                self._execute_script(args.script, args.script_args)
            
            title = args.title or f"Flamegraph: {Path(args.script).name}"
            flamegraph_html = generate_flamegraph(graph, title=title, min_time_ms=args.min_time)
            
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(flamegraph_html)
            
            print(f"Flamegraph saved to: {args.output}")
            
            if not args.no_browser:
                self._open_browser(args.output)
            
            return 0
            
        except Exception as e:
            print(f"Error generating flamegraph: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1
    
    def _handle_profile(self, args):
        """Handle profile command."""
        print(f"Profiling script: {args.script}")
        
        try:
            import cProfile
            import pstats
            from io import StringIO
            
            profiler = cProfile.Profile()
            
            with trace_scope(None) as graph:
                profiler.enable()
                self._execute_script(args.script, args.script_args)
                profiler.disable()
            
            stream = StringIO()
            stats = pstats.Stats(profiler, stream=stream)
            stats.sort_stats('cumulative')
            stats.print_stats(50)
            
            profile_text = stream.getvalue()
            memory_stats = get_memory_usage() if args.memory else None
            
            if args.format == 'html':
                profiling_stats = {
                    'cpu_profile': profile_text,
                    'memory_stats': memory_stats
                }
                
                export_html(graph, args.output, title=f"Profile: {Path(args.script).name}", 
                          profiling_stats=profiling_stats)
                print(f"Profile saved to: {args.output}")
                
                if not args.no_browser:
                    self._open_browser(args.output)
            
            elif args.format == 'json':
                profile_data = {
                    'graph': {
                        'nodes': [node.to_dict() for node in graph.nodes.values()],
                        'edges': [edge.to_dict() for edge in graph.edges.values()]
                    },
                    'cpu_profile': profile_text,
                    'memory_stats': memory_stats
                }
                
                with open(args.output, 'w') as f:
                    json.dump(profile_data, f, indent=2)
                
                print(f"Profile saved to: {args.output}")
            
            elif args.format == 'text':
                with open(args.output, 'w') as f:
                    f.write("=== CPU PROFILE ===\n\n")
                    f.write(profile_text)
                    
                    if memory_stats:
                        f.write("\n\n=== MEMORY STATS ===\n\n")
                        f.write(json.dumps(memory_stats, indent=2))
                
                print(f"Profile saved to: {args.output}")
            
            return 0
            
        except Exception as e:
            print(f"Error profiling script: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1
    
    def _handle_memory_leak(self, args):
        """Handle memory-leak command."""
        print(f"Detecting memory leaks in: {args.script}")
        
        try:
            detector = MemoryLeakDetector(threshold_mb=args.threshold, sample_interval=args.interval)
            detector.start()
            
            self._execute_script(args.script, args.script_args)
            
            report = detector.stop()
            top_consumers = get_top_memory_consumers(args.top)
            
            from .memory_leak_visualizer import generate_memory_leak_html
            html_content = generate_memory_leak_html(report, top_consumers, args.script)
            
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"\nMemory Leak Report:")
            print(f"  Peak memory: {report['peak_memory_mb']:.2f} MB")
            print(f"  Memory growth: {report['memory_growth_mb']:.2f} MB")
            print(f"  Potential leaks: {len(report.get('potential_leaks', []))}")
            print(f"\nReport saved to: {args.output}")
            
            if not args.no_browser:
                self._open_browser(args.output)
            
            return 0
            
        except Exception as e:
            print(f"Error detecting memory leaks: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1
    
    def _load_graph_from_json(self, filepath):
        """Load a CallGraph from a JSON file."""
        with open(filepath, 'r') as f:
            trace_data = json.load(f)
        
        graph = CallGraph()
        for node_data in trace_data.get('nodes', []):
            node = CallNode(node_data['name'], node_data.get('module', ''))
            node.call_count = node_data['call_count']
            node.total_time = node_data['total_time']
            graph.nodes[node.full_name] = node
        
        for edge_data in trace_data.get('edges', []):
            edge = CallEdge(edge_data['caller'], edge_data['callee'])
            edge.call_count = edge_data['call_count']
            edge.total_time = edge_data['total_time']
            graph.edges[(edge.caller, edge.callee)] = edge
        
        return graph
    
    def _handle_compare(self, args):
        """Handle compare command."""
        print(f"Comparing traces: {args.file1} vs {args.file2}")
        
        try:
            graph1 = self._load_graph_from_json(args.file1)
            graph2 = self._load_graph_from_json(args.file2)
            
            comparison = compare_graphs(graph1, graph2, args.label1, args.label2)
            export_comparison_html(graph1, graph2, args.output, label1=args.label1, label2=args.label2)
            
            print(f"\nComparison Summary:")
            print(f"  {args.label1}: {len(graph1.nodes)} nodes, {len(graph1.edges)} edges")
            print(f"  {args.label2}: {len(graph2.nodes)} nodes, {len(graph2.edges)} edges")
            print(f"  New nodes: {len(comparison.get('added_nodes', []))}")
            print(f"  Removed nodes: {len(comparison.get('removed_nodes', []))}")
            print(f"\nComparison saved to: {args.output}")
            
            if not args.no_browser:
                self._open_browser(args.output)
            
            return 0
            
        except Exception as e:
            print(f"Error comparing traces: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1
    
    def _handle_export(self, args):
        """Handle export command."""
        print(f"Exporting {args.input} to {args.format} format")
        
        try:
            graph = self._load_graph_from_json(args.input)
            title = args.title or f"Exported: {Path(args.input).name}"

            if args.format == 'html':
                if not args.output:
                    raise ValueError("Output file path is required for HTML export")
                export_html(graph, args.output, title=title)
                print(f"Exported to: {args.output}")
            elif args.format == '3d':
                if not args.output:
                    raise ValueError("Output file path is required for 3D export")
                export_html_3d(graph, args.output, title=title)
                print(f"Exported to: {args.output}")
            elif args.format == 'json':
                if not args.output:
                    raise ValueError("Output file path is required for JSON export")
                export_json(graph, args.output)
                print(f"Exported to: {args.output}")
            elif args.format == 'otel':
                # Determine service name: CLI arg, env var, or sensible default
                service_name = args.service_name or os.getenv('CALLFLOW_OTEL_SERVICE_NAME', 'callflow-tracer')

                print(f"Exporting call graph to OpenTelemetry (service_name={service_name})")
                try:
                    export_callgraph_to_otel(graph, service_name=service_name)
                except OpenTelemetryNotAvailable as e:
                    print(str(e), file=sys.stderr)
                    return 1

                print("OpenTelemetry export completed (spans sent via configured OTel SDK).")

            return 0
            
        except Exception as e:
            print(f"Error exporting: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1
    
    def _handle_info(self, args):
        """Handle info command."""
        print(f"Analyzing trace file: {args.file}")
        
        try:
            with open(args.file, 'r') as f:
                trace_data = json.load(f)
            
            nodes = trace_data.get('nodes', [])
            edges = trace_data.get('edges', [])
            
            total_calls = sum(node['call_count'] for node in nodes)
            total_time = sum(node['total_time'] for node in nodes)
            sorted_nodes = sorted(nodes, key=lambda x: x['total_time'], reverse=True)
            
            print(f"\n=== Trace Information ===")
            print(f"File: {args.file}")
            print(f"Total nodes: {len(nodes)}")
            print(f"Total edges: {len(edges)}")
            print(f"Total function calls: {total_calls}")
            print(f"Total execution time: {total_time:.6f}s")
            
            if args.detailed:
                print(f"\n=== Top 10 Functions by Time ===")
                for i, node in enumerate(sorted_nodes[:10], 1):
                    print(f"{i}. {node['full_name']}")
                    print(f"   Calls: {node['call_count']}, Time: {node['total_time']:.6f}s")
                
                modules = {}
                for node in nodes:
                    module = node.get('module', '__main__')
                    if module not in modules:
                        modules[module] = {'count': 0, 'time': 0.0}
                    modules[module]['count'] += 1
                    modules[module]['time'] += node['total_time']
                
                print(f"\n=== Module Statistics ===")
                for module, stats in sorted(modules.items(), key=lambda x: x[1]['time'], reverse=True):
                    print(f"{module}: {stats['count']} functions, {stats['time']:.6f}s")
            
            return 0
            
        except Exception as e:
            print(f"Error analyzing trace: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1
    
    def _add_quality_parser(self, subparsers):
        """Add quality analysis subcommand parser."""
        quality_parser = subparsers.add_parser('quality', help='Analyze code quality metrics')
        quality_parser.add_argument('directory', nargs='?', default='.', help='Directory to analyze')
        quality_parser.add_argument('-o', '--output', default='quality_report.html', help='Output file')
        quality_parser.add_argument('--format', choices=['html', 'json'], default='html')
        quality_parser.add_argument('--track-trends', action='store_true', help='Track quality trends over time')
        quality_parser.add_argument('--no-browser', action='store_true', help='Do not open browser')
    
    def _add_predict_parser(self, subparsers):
        """Add predictive analysis subcommand parser."""
        predict_parser = subparsers.add_parser('predict', help='Predict performance issues')
        predict_parser.add_argument('trace_history', help='JSON file with trace history')
        predict_parser.add_argument('-o', '--output', default='predictions.html', help='Output file')
        predict_parser.add_argument('--format', choices=['html', 'json'], default='html')
        predict_parser.add_argument('--no-browser', action='store_true', help='Do not open browser')
    
    def _add_churn_parser(self, subparsers):
        """Add code churn analysis subcommand parser."""
        churn_parser = subparsers.add_parser('churn', help='Analyze code churn')
        churn_parser.add_argument('directory', nargs='?', default='.', help='Repository directory')
        churn_parser.add_argument('-o', '--output', default='churn_report.html', help='Output file')
        churn_parser.add_argument('--days', type=int, default=90, help='Days of history to analyze')
        churn_parser.add_argument('--format', choices=['html', 'json'], default='html')
        churn_parser.add_argument('--no-browser', action='store_true', help='Do not open browser')
    
    def _handle_quality(self, args):
        """Handle quality analysis command."""
        print(f"Analyzing code quality in: {args.directory}")
        
        try:
            # Analyze codebase
            results = analyze_codebase(args.directory)
            
            # Track trends if requested
            if args.track_trends:
                trend_analyzer = QualityTrendAnalyzer()
                from .code_quality import ComplexityMetrics, MaintainabilityMetrics, TechnicalDebtIndicator
                
                complexity = [ComplexityMetrics(**m) for m in results['complexity_metrics']]
                maintainability = [MaintainabilityMetrics(**m) for m in results['maintainability_metrics']]
                debt = [TechnicalDebtIndicator(**d) for d in results['debt_indicators']]
                
                trend = trend_analyzer.add_snapshot(complexity, maintainability, debt)
                results['trend'] = trend.to_dict()
                results['trend_analysis'] = trend_analyzer.analyze_trends()
            
            # Output results
            if args.format == 'json':
                with open(args.output, 'w') as f:
                    json.dump(results, f, indent=2)
                print(f"Quality report saved to: {args.output}")
            else:
                # Generate HTML report
                html = self._generate_quality_html(results)
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(html)
                print(f"Quality report saved to: {args.output}")
                
                if not args.no_browser:
                    self._open_browser(args.output)
            
            # Print summary
            summary = results['summary']
            print(f"\n=== Quality Summary ===")
            print(f"Total functions: {summary['total_functions']}")
            print(f"Average complexity: {summary['average_complexity']:.2f}")
            print(f"Average maintainability: {summary['average_maintainability']:.2f}")
            print(f"Total debt score: {summary['total_debt_score']:.2f}")
            print(f"Critical issues: {summary['critical_issues']}")
            print(f"High issues: {summary['high_issues']}")
            
            return 0
            
        except Exception as e:
            print(f"Error analyzing quality: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1
    
    def _handle_predict(self, args):
        """Handle predictive analysis command."""
        print(f"Analyzing trace history: {args.trace_history}")
        
        try:
            # Load trace history
            with open(args.trace_history, 'r') as f:
                history_data = json.load(f)
            
            # Ensure it's a list
            if isinstance(history_data, dict):
                history = [history_data]
            else:
                history = history_data
            
            if len(history) < 2:
                print("Warning: Need at least 2 traces for prediction", file=sys.stderr)
                return 1
            
            # Generate predictions
            current_trace = history[-1]
            report = generate_predictive_report(history[:-1], current_trace)
            
            # Output results
            if args.format == 'json':
                with open(args.output, 'w') as f:
                    json.dump(report, f, indent=2)
                print(f"Predictions saved to: {args.output}")
            else:
                html = self._generate_predictions_html(report)
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(html)
                print(f"Predictions saved to: {args.output}")
                
                if not args.no_browser:
                    self._open_browser(args.output)
            
            # Print summary
            summary = report['summary']
            print(f"\n=== Prediction Summary ===")
            print(f"Total predictions: {summary['total_predictions']}")
            print(f"Critical risks: {summary['critical_risks']}")
            print(f"High risks: {summary['high_risks']}")
            print(f"Average confidence: {summary['average_confidence']:.2%}")
            
            if report['recommendations']:
                print(f"\n=== Recommendations ===")
                for rec in report['recommendations']:
                    print(f"  • {rec}")
            
            return 0
            
        except Exception as e:
            print(f"Error generating predictions: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1
    
    def _handle_churn(self, args):
        """Handle code churn analysis command."""
        print(f"Analyzing code churn in: {args.directory}")
        
        try:
            # Generate churn report
            report = generate_churn_report(args.directory, args.days)
            
            # Output results
            if args.format == 'json':
                with open(args.output, 'w') as f:
                    json.dump(report, f, indent=2)
                print(f"Churn report saved to: {args.output}")
            else:
                html = self._generate_churn_html(report)
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(html)
                print(f"Churn report saved to: {args.output}")
                
                if not args.no_browser:
                    self._open_browser(args.output)
            
            # Print summary
            summary = report['summary']
            print(f"\n=== Churn Summary ===")
            print(f"Total files analyzed: {summary['total_files']}")
            print(f"Total commits: {summary['total_commits']}")
            print(f"Total changes: {summary['total_changes']}")
            print(f"Average churn rate: {summary['average_churn_rate']:.2f} changes/day")
            print(f"High risk files: {summary['high_risk_files']}")
            
            if report['hotspots']:
                print(f"\n=== Top 5 Hotspots ===")
                for i, hotspot in enumerate(report['hotspots'][:5], 1):
                    print(f"{i}. {hotspot['file_path']}")
                    print(f"   Score: {hotspot['hotspot_score']:.1f}, Commits: {hotspot['total_commits']}")
            
            return 0
            
        except Exception as e:
            print(f"Error analyzing churn: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1
    
    def _generate_quality_html(self, results: Dict) -> str:
        """Generate HTML report for quality analysis."""
        # Simple HTML template
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Code Quality Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }}
        h1 {{ color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-value {{ font-size: 2em; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #4CAF50; color: white; }}
        .critical {{ color: #f44336; font-weight: bold; }}
        .high {{ color: #ff9800; font-weight: bold; }}
        .medium {{ color: #ffc107; }}
        .low {{ color: #4CAF50; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Code Quality Report</h1>
        
        <div class="summary">
            <div class="stat-card">
                <div class="stat-value">{results['summary']['total_functions']}</div>
                <div>Total Functions</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{results['summary']['average_complexity']:.1f}</div>
                <div>Avg Complexity</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{results['summary']['average_maintainability']:.1f}</div>
                <div>Avg Maintainability</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{results['summary']['critical_issues']}</div>
                <div>Critical Issues</div>
            </div>
        </div>
        
        <h2>Technical Debt Indicators</h2>
        <table>
            <tr>
                <th>Function</th>
                <th>Module</th>
                <th>Debt Score</th>
                <th>Severity</th>
                <th>Issues</th>
            </tr>
"""
        
        for debt in results['debt_indicators'][:20]:
            severity_class = debt['severity'].lower()
            html += f"""
            <tr>
                <td>{debt['function_name']}</td>
                <td>{debt['module']}</td>
                <td>{debt['debt_score']:.1f}</td>
                <td class="{severity_class}">{debt['severity']}</td>
                <td>{', '.join(debt['issues'][:2])}</td>
            </tr>
"""
        
        html += """
        </table>
    </div>
</body>
</html>
"""
        return html
    
    def _generate_predictions_html(self, report: Dict) -> str:
        """Generate HTML report for predictions."""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Performance Predictions</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }}
        h1 {{ color: #333; }}
        .prediction {{ border-left: 4px solid #2196F3; padding: 15px; margin: 10px 0; background: #f9f9f9; }}
        .critical {{ border-color: #f44336; }}
        .high {{ border-color: #ff9800; }}
        .medium {{ border-color: #ffc107; }}
        .low {{ border-color: #4CAF50; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Performance Predictions</h1>
        <p>Total Predictions: {report['summary']['total_predictions']}</p>
        <p>Critical Risks: {report['summary']['critical_risks']}</p>
"""
        
        for pred in report['performance_predictions'][:10]:
            risk_class = pred['risk_level'].lower()
            html += f"""
        <div class="prediction {risk_class}">
            <h3>{pred['function_name']}</h3>
            <p><strong>Risk Level:</strong> {pred['risk_level']}</p>
            <p><strong>Current Time:</strong> {pred['current_avg_time']:.6f}s</p>
            <p><strong>Predicted Time:</strong> {pred['predicted_time']:.6f}s</p>
            <p><strong>Confidence:</strong> {pred['confidence']:.1%}</p>
            <p><strong>Recommendations:</strong></p>
            <ul>
                {''.join(f'<li>{rec}</li>' for rec in pred['recommendations'])}
            </ul>
        </div>
"""
        
        html += """
    </div>
</body>
</html>
"""
        return html
    
    def _generate_churn_html(self, report: Dict) -> str:
        """Generate HTML report for code churn."""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Code Churn Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }}
        h1 {{ color: #333; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #FF5722; color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Code Churn Report</h1>
        <p>Analysis Period: {report['summary']['analysis_period_days']} days</p>
        <p>Total Files: {report['summary']['total_files']}</p>
        <p>Total Commits: {report['summary']['total_commits']}</p>
        
        <h2>Top Hotspots</h2>
        <table>
            <tr>
                <th>File</th>
                <th>Hotspot Score</th>
                <th>Commits</th>
                <th>Changes</th>
                <th>Churn Rate</th>
            </tr>
"""
        
        for hotspot in report['hotspots']:
            html += f"""
            <tr>
                <td>{hotspot['file_path']}</td>
                <td>{hotspot['hotspot_score']:.1f}</td>
                <td>{hotspot['total_commits']}</td>
                <td>{hotspot['lines_modified']}</td>
                <td>{hotspot['churn_rate']:.2f}/day</td>
            </tr>
"""
        
        html += """
        </table>
    </div>
</body>
</html>
"""
        return html
    
    def _add_otel_parser(self, subparsers):
        """Add OpenTelemetry export subcommand parser."""
        otel_parser = subparsers.add_parser('otel', help='Advanced OpenTelemetry export with exemplars and sampling')
        otel_parser.add_argument('input', help='Input trace file (JSON)')
        otel_parser.add_argument('--config', help='OTel config file (.yaml or .json)')
        otel_parser.add_argument('--service-name', help='Service name (overrides config)')
        otel_parser.add_argument('--environment', default='production', help='Environment (production/staging/dev)')
        otel_parser.add_argument('--sampling-rate', type=float, default=1.0, help='Sampling rate (0.0-1.0)')
        otel_parser.add_argument('--include-metrics', action='store_true', help='Link custom metrics as exemplars')
        otel_parser.add_argument('--metrics-file', help='Path to metrics JSON file for exemplars')
        otel_parser.add_argument('--init-config', action='store_true', help='Create example config file')
    
    def _handle_otel(self, args):
        """Handle advanced OTel export command."""
        if args.init_config:
            try:
                create_example_config(".callflow_otel.yaml")
                print("Example OTel config created: .callflow_otel.yaml")
                return 0
            except Exception as e:
                print(f"Error creating config: {e}", file=sys.stderr)
                return 1
        
        print(f"Exporting to OpenTelemetry (advanced mode)")
        
        try:
            # Load config
            config = OTelConfig(args.config)
            config.load_from_env()
            
            # Override with CLI args
            if args.service_name:
                config.config["service_name"] = args.service_name
            if args.environment:
                config.config["environment"] = args.environment
            if args.sampling_rate:
                config.config["sampling_rate"] = args.sampling_rate
            
            # Load trace
            graph = self._load_graph_from_json(args.input)
            
            # Export with metrics if requested
            if args.include_metrics and args.metrics_file:
                try:
                    with open(args.metrics_file, 'r') as f:
                        metrics_data = json.load(f)
                    result = export_callgraph_with_metrics(
                        graph,
                        metrics_data,
                        service_name=config.get("service_name"),
                        resource_attributes=config.get("resource_attributes")
                    )
                except FileNotFoundError:
                    print(f"Warning: Metrics file not found: {args.metrics_file}", file=sys.stderr)
                    result = export_callgraph_to_otel(
                        graph,
                        service_name=config.get("service_name"),
                        resource_attributes=config.get("resource_attributes"),
                        sampling_rate=config.get("sampling_rate"),
                        environment=config.get("environment")
                    )
            else:
                result = export_callgraph_to_otel(
                    graph,
                    service_name=config.get("service_name"),
                    resource_attributes=config.get("resource_attributes"),
                    sampling_rate=config.get("sampling_rate"),
                    environment=config.get("environment")
                )
            
            # Print summary
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
            import traceback
            traceback.print_exc()
            return 1


def main():
    """Main entry point for the CLI."""
    cli = CallflowCLI()
    sys.exit(cli.run())


if __name__ == '__main__':
    main()
