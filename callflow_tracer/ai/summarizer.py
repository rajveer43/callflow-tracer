"""
Trace summarization using LLMs.

Generates human-readable summaries of execution traces with insights,
bottlenecks, and actionable recommendations.
"""

from typing import Optional, Dict, Any, List
from ..tracer import CallGraph, CallNode
from .llm_provider import LLMProvider, get_default_provider


class TraceSummarizer:
    """Generate AI-powered summaries of execution traces."""
    
    def __init__(self, provider: Optional[LLMProvider] = None):
        """
        Initialize the trace summarizer.
        
        Args:
            provider: LLM provider to use. If None, auto-detect from environment.
        """
        self.provider = provider or get_default_provider()
    
    def summarize(self, graph: CallGraph, include_recommendations: bool = True,
                  include_bottlenecks: bool = True, max_bottlenecks: int = 5) -> Dict[str, Any]:
        """
        Generate a comprehensive summary of the trace.
        
        Args:
            graph: CallGraph to summarize
            include_recommendations: Include optimization recommendations
            include_bottlenecks: Include bottleneck analysis
            max_bottlenecks: Maximum number of bottlenecks to analyze
        
        Returns:
            Dictionary containing summary, bottlenecks, and recommendations
        """
        # Extract trace statistics
        stats = self._extract_stats(graph)
        
        # Identify bottlenecks
        bottlenecks = []
        if include_bottlenecks:
            bottlenecks = self._identify_bottlenecks(graph, max_bottlenecks)
        
        # Generate AI summary
        summary_text = self._generate_summary(stats, bottlenecks, include_recommendations)
        
        return {
            "summary": summary_text,
            "statistics": stats,
            "bottlenecks": bottlenecks,
            "total_execution_time": stats["total_time"],
            "total_functions": stats["total_functions"],
            "total_calls": stats["total_calls"]
        }
    
    def _extract_stats(self, graph: CallGraph) -> Dict[str, Any]:
        """Extract key statistics from the call graph."""
        total_time = sum(node.total_time for node in graph.nodes.values())
        total_calls = sum(node.call_count for node in graph.nodes.values())
        total_functions = len(graph.nodes)
        
        # Find slowest function
        slowest = max(graph.nodes.values(), key=lambda n: n.total_time, default=None)
        
        # Find most called function
        most_called = max(graph.nodes.values(), key=lambda n: n.call_count, default=None)
        
        # Calculate depth (max call stack depth)
        depth = self._calculate_depth(graph)
        
        return {
            "total_time": round(total_time, 3),
            "total_calls": total_calls,
            "total_functions": total_functions,
            "slowest_function": {
                "name": slowest.full_name if slowest else None,
                "time": round(slowest.total_time, 3) if slowest else 0,
                "percentage": round((slowest.total_time / total_time * 100) if slowest and total_time > 0 else 0, 1)
            },
            "most_called_function": {
                "name": most_called.full_name if most_called else None,
                "calls": most_called.call_count if most_called else 0
            },
            "max_depth": depth
        }
    
    def _calculate_depth(self, graph: CallGraph) -> int:
        """Calculate maximum call stack depth."""
        # Build adjacency list
        adj = {}
        for (caller, callee) in graph.edges.keys():
            if caller not in adj:
                adj[caller] = []
            adj[caller].append(callee)
        
        # Find roots (nodes with no incoming edges)
        all_callees = set(callee for _, callee in graph.edges.keys())
        roots = [node for node in graph.nodes.keys() if node not in all_callees]
        
        if not roots:
            # If no clear roots, use all nodes
            roots = list(graph.nodes.keys())
        
        # DFS to find max depth
        def dfs(node, visited):
            if node not in adj or node in visited:
                return 1
            visited.add(node)
            max_child_depth = max((dfs(child, visited.copy()) for child in adj[node]), default=0)
            return 1 + max_child_depth
        
        return max(dfs(root, set()) for root in roots) if roots else 0
    
    def _identify_bottlenecks(self, graph: CallGraph, max_count: int) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks in the trace."""
        # Sort nodes by total time
        sorted_nodes = sorted(
            graph.nodes.values(),
            key=lambda n: n.total_time,
            reverse=True
        )
        
        total_time = sum(node.total_time for node in graph.nodes.values())
        
        bottlenecks = []
        for node in sorted_nodes[:max_count]:
            percentage = (node.total_time / total_time * 100) if total_time > 0 else 0
            avg_time = node.total_time / node.call_count if node.call_count > 0 else 0
            
            bottlenecks.append({
                "function": node.full_name,
                "total_time": round(node.total_time, 3),
                "avg_time": round(avg_time, 6),
                "call_count": node.call_count,
                "percentage": round(percentage, 1),
                "module": node.module
            })
        
        return bottlenecks
    
    def _generate_summary(self, stats: Dict[str, Any], bottlenecks: List[Dict[str, Any]],
                         include_recommendations: bool) -> str:
        """Generate natural language summary using LLM."""
        
        # Build prompt
        prompt = self._build_summary_prompt(stats, bottlenecks, include_recommendations)
        
        system_prompt = """You are an expert performance analyst for Python applications.
Your job is to analyze execution traces and provide clear, actionable insights.
Be concise but informative. Focus on the most important findings.
Use bullet points for clarity. Avoid jargon when possible."""
        
        try:
            summary = self.provider.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=1000
            )
            return summary.strip()
        except Exception as e:
            # Fallback to basic summary if LLM fails
            return self._generate_fallback_summary(stats, bottlenecks)
    
    def _build_summary_prompt(self, stats: Dict[str, Any], bottlenecks: List[Dict[str, Any]],
                             include_recommendations: bool) -> str:
        """Build the prompt for LLM summarization."""
        
        prompt = f"""Analyze this Python execution trace and provide a clear summary:

EXECUTION STATISTICS:
- Total execution time: {stats['total_time']}s
- Total functions traced: {stats['total_functions']}
- Total function calls: {stats['total_calls']}
- Maximum call depth: {stats['max_depth']}

SLOWEST FUNCTION:
- {stats['slowest_function']['name']} took {stats['slowest_function']['time']}s ({stats['slowest_function']['percentage']}% of total time)

MOST CALLED FUNCTION:
- {stats['most_called_function']['name']} was called {stats['most_called_function']['calls']} times
"""
        
        if bottlenecks:
            prompt += "\nTOP BOTTLENECKS:\n"
            for i, bottleneck in enumerate(bottlenecks, 1):
                prompt += f"{i}. {bottleneck['function']}: {bottleneck['total_time']}s ({bottleneck['percentage']}%) - called {bottleneck['call_count']}x, avg {bottleneck['avg_time']}s\n"
        
        if include_recommendations:
            prompt += "\nProvide:\n1. A brief summary of the execution\n2. Key bottlenecks and their impact\n3. Specific optimization recommendations\n"
        else:
            prompt += "\nProvide a brief summary of the execution and key bottlenecks.\n"
        
        return prompt
    
    def _generate_fallback_summary(self, stats: Dict[str, Any], bottlenecks: List[Dict[str, Any]]) -> str:
        """Generate a basic summary without LLM (fallback)."""
        lines = [
            f"Execution Summary:",
            f"",
            f"Total execution time: {stats['total_time']}s across {stats['total_functions']} functions",
            f"Total function calls: {stats['total_calls']}",
            f"",
            f"Main bottleneck: {stats['slowest_function']['name']} ({stats['slowest_function']['percentage']}% of total time)",
        ]
        
        if bottlenecks:
            lines.append("")
            lines.append("Top bottlenecks:")
            for i, bottleneck in enumerate(bottlenecks[:3], 1):
                lines.append(f"  {i}. {bottleneck['function']}: {bottleneck['total_time']}s ({bottleneck['percentage']}%)")
        
        return "\n".join(lines)


def summarize_trace(graph: CallGraph, provider: Optional[LLMProvider] = None,
                   include_recommendations: bool = True) -> Dict[str, Any]:
    """
    Convenience function to summarize a trace.
    
    Args:
        graph: CallGraph to summarize
        provider: Optional LLM provider (auto-detected if None)
        include_recommendations: Include optimization recommendations
    
    Returns:
        Dictionary with summary, statistics, and bottlenecks
    
    Example:
        >>> from callflow_tracer import trace_scope
        >>> from callflow_tracer.ai import summarize_trace
        >>> 
        >>> with trace_scope() as graph:
        >>>     my_application()
        >>> 
        >>> summary = summarize_trace(graph)
        >>> print(summary['summary'])
    """
    summarizer = TraceSummarizer(provider)
    return summarizer.summarize(graph, include_recommendations=include_recommendations)
