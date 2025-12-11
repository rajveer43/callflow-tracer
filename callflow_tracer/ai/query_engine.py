"""
Natural language query interface for exploring traces.

Allows users to ask questions about their traces in plain English.
"""

from typing import Optional, Dict, Any, List, Union
from ..tracer import CallGraph, CallNode
from .llm_provider import LLMProvider, get_default_provider
import re


class QueryEngine:
    """Natural language query interface for call graphs."""
    
    def __init__(self, provider: Optional[LLMProvider] = None):
        """
        Initialize the query engine.
        
        Args:
            provider: LLM provider to use. If None, auto-detect from environment.
        """
        self.provider = provider or get_default_provider()
        
        # Common query patterns (for optimization)
        self.patterns = {
            r"slow|slowest|bottleneck": self._query_slow_functions,
            r"fast|fastest|quick": self._query_fast_functions,
            r"most called|frequently|often": self._query_most_called,
            r"least called|rarely|seldom": self._query_least_called,
            r"database|db|sql": self._query_database_functions,
            r"i/o|io|file|network": self._query_io_functions,
            r"recursive": self._query_recursive_functions,
            r"module|package": self._query_by_module,
            r"call.*count|how many times": self._query_call_count,
            r"total.*time|execution.*time": self._query_total_time,
        }
    
    def query(self, graph: CallGraph, question: str, use_llm: bool = True) -> Dict[str, Any]:
        """
        Query the call graph using natural language.
        
        Args:
            graph: CallGraph to query
            question: Natural language question
            use_llm: Whether to use LLM for complex queries (fallback to pattern matching if False)
        
        Returns:
            Dictionary with answer, data, and query type
        
        Example:
            >>> result = query_engine.query(graph, "Which functions are slowest?")
            >>> print(result['answer'])
            >>> print(result['data'])
        """
        question_lower = question.lower()
        
        # Try pattern matching first (faster)
        for pattern, handler in self.patterns.items():
            if re.search(pattern, question_lower):
                try:
                    data = handler(graph, question)
                    answer = self._format_answer(question, data, handler.__name__)
                    return {
                        "question": question,
                        "answer": answer,
                        "data": data,
                        "query_type": handler.__name__.replace("_query_", "")
                    }
                except Exception as e:
                    # If pattern matching fails, fall through to LLM
                    pass
        
        # Use LLM for complex queries
        if use_llm:
            return self._query_with_llm(graph, question)
        else:
            return {
                "question": question,
                "answer": "Unable to answer this question. Try asking about slow functions, call counts, or specific modules.",
                "data": None,
                "query_type": "unknown"
            }
    
    def _query_slow_functions(self, graph: CallGraph, question: str) -> List[Dict[str, Any]]:
        """Find slow/bottleneck functions."""
        # Extract number if specified (e.g., "top 5 slowest")
        match = re.search(r'(\d+)', question)
        limit = int(match.group(1)) if match else 5
        
        sorted_nodes = sorted(
            graph.nodes.values(),
            key=lambda n: n.total_time,
            reverse=True
        )[:limit]
        
        total_time = sum(node.total_time for node in graph.nodes.values())
        
        return [
            {
                "function": node.full_name,
                "total_time": round(node.total_time, 3),
                "avg_time": round(node.total_time / node.call_count, 6),
                "call_count": node.call_count,
                "percentage": round((node.total_time / total_time * 100) if total_time > 0 else 0, 1)
            }
            for node in sorted_nodes
        ]
    
    def _query_fast_functions(self, graph: CallGraph, question: str) -> List[Dict[str, Any]]:
        """Find fastest functions."""
        match = re.search(r'(\d+)', question)
        limit = int(match.group(1)) if match else 5
        
        sorted_nodes = sorted(
            graph.nodes.values(),
            key=lambda n: n.total_time
        )[:limit]
        
        return [
            {
                "function": node.full_name,
                "total_time": round(node.total_time, 6),
                "avg_time": round(node.total_time / node.call_count, 6),
                "call_count": node.call_count
            }
            for node in sorted_nodes
        ]
    
    def _query_most_called(self, graph: CallGraph, question: str) -> List[Dict[str, Any]]:
        """Find most frequently called functions."""
        match = re.search(r'(\d+)', question)
        limit = int(match.group(1)) if match else 5
        
        sorted_nodes = sorted(
            graph.nodes.values(),
            key=lambda n: n.call_count,
            reverse=True
        )[:limit]
        
        return [
            {
                "function": node.full_name,
                "call_count": node.call_count,
                "total_time": round(node.total_time, 3),
                "avg_time": round(node.total_time / node.call_count, 6)
            }
            for node in sorted_nodes
        ]
    
    def _query_least_called(self, graph: CallGraph, question: str) -> List[Dict[str, Any]]:
        """Find least frequently called functions."""
        match = re.search(r'(\d+)', question)
        limit = int(match.group(1)) if match else 5
        
        sorted_nodes = sorted(
            graph.nodes.values(),
            key=lambda n: n.call_count
        )[:limit]
        
        return [
            {
                "function": node.full_name,
                "call_count": node.call_count,
                "total_time": round(node.total_time, 3)
            }
            for node in sorted_nodes
        ]
    
    def _query_database_functions(self, graph: CallGraph, question: str) -> List[Dict[str, Any]]:
        """Find database-related functions."""
        db_keywords = ['db', 'database', 'sql', 'query', 'execute', 'cursor', 'session']
        
        db_nodes = [
            node for node in graph.nodes.values()
            if any(keyword in node.full_name.lower() for keyword in db_keywords)
        ]
        
        # Sort by total time
        db_nodes.sort(key=lambda n: n.total_time, reverse=True)
        
        return [
            {
                "function": node.full_name,
                "total_time": round(node.total_time, 3),
                "call_count": node.call_count,
                "avg_time": round(node.total_time / node.call_count, 6)
            }
            for node in db_nodes
        ]
    
    def _query_io_functions(self, graph: CallGraph, question: str) -> List[Dict[str, Any]]:
        """Find I/O related functions."""
        io_keywords = ['read', 'write', 'open', 'file', 'request', 'fetch', 'get', 'post', 'http']
        
        io_nodes = [
            node for node in graph.nodes.values()
            if any(keyword in node.full_name.lower() for keyword in io_keywords)
        ]
        
        io_nodes.sort(key=lambda n: n.total_time, reverse=True)
        
        return [
            {
                "function": node.full_name,
                "total_time": round(node.total_time, 3),
                "call_count": node.call_count
            }
            for node in io_nodes
        ]
    
    def _query_recursive_functions(self, graph: CallGraph, question: str) -> List[Dict[str, Any]]:
        """Find recursive functions."""
        recursive = []
        
        for (caller, callee) in graph.edges.keys():
            if caller == callee:
                node = graph.nodes[caller]
                recursive.append({
                    "function": node.full_name,
                    "call_count": node.call_count,
                    "total_time": round(node.total_time, 3)
                })
        
        return recursive
    
    def _query_by_module(self, graph: CallGraph, question: str) -> List[Dict[str, Any]]:
        """Find functions in a specific module."""
        # Extract module name from question
        words = question.split()
        module_name = None
        
        for i, word in enumerate(words):
            if word.lower() in ['module', 'package', 'in']:
                if i + 1 < len(words):
                    module_name = words[i + 1].strip('?.,')
                    break
        
        if not module_name:
            # Try to find any word that looks like a module
            for word in words:
                if '.' in word or word[0].islower():
                    module_name = word.strip('?.,')
                    break
        
        if not module_name:
            return []
        
        matching_nodes = [
            node for node in graph.nodes.values()
            if module_name.lower() in node.module.lower() or module_name.lower() in node.full_name.lower()
        ]
        
        matching_nodes.sort(key=lambda n: n.total_time, reverse=True)
        
        return [
            {
                "function": node.full_name,
                "module": node.module,
                "total_time": round(node.total_time, 3),
                "call_count": node.call_count
            }
            for node in matching_nodes
        ]
    
    def _query_call_count(self, graph: CallGraph, question: str) -> Dict[str, Any]:
        """Get total call count statistics."""
        total_calls = sum(node.call_count for node in graph.nodes.values())
        
        return {
            "total_calls": total_calls,
            "unique_functions": len(graph.nodes),
            "avg_calls_per_function": round(total_calls / len(graph.nodes), 2) if graph.nodes else 0
        }
    
    def _query_total_time(self, graph: CallGraph, question: str) -> Dict[str, Any]:
        """Get total execution time statistics."""
        total_time = sum(node.total_time for node in graph.nodes.values())
        
        return {
            "total_time": round(total_time, 3),
            "total_functions": len(graph.nodes)
        }
    
    def _format_answer(self, question: str, data: Any, query_type: str) -> str:
        """Format the answer in natural language."""
        if not data:
            return "No results found for your query."
        
        if isinstance(data, list):
            if not data:
                return "No functions match your criteria."
            
            lines = []
            for i, item in enumerate(data, 1):
                if 'function' in item:
                    func = item['function']
                    time_info = f"{item['total_time']}s" if 'total_time' in item else ""
                    calls_info = f"({item['call_count']} calls)" if 'call_count' in item else ""
                    pct_info = f"[{item['percentage']}%]" if 'percentage' in item else ""
                    
                    lines.append(f"{i}. {func} - {time_info} {calls_info} {pct_info}".strip())
            
            return "\n".join(lines)
        
        elif isinstance(data, dict):
            lines = []
            for key, value in data.items():
                formatted_key = key.replace('_', ' ').title()
                lines.append(f"{formatted_key}: {value}")
            return "\n".join(lines)
        
        return str(data)
    
    def _query_with_llm(self, graph: CallGraph, question: str) -> Dict[str, Any]:
        """Use LLM to answer complex queries with enhanced prompts."""
        from .prompts import get_prompt_for_task
        
        # Prepare graph summary for LLM
        graph_summary = self._prepare_graph_summary(graph)
        
        # Get enhanced prompt template
        system_prompt, user_prompt = get_prompt_for_task(
            'performance_analysis',
            graph_summary=graph_summary,
            question=question
        )
        
        try:
            answer = self.provider.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.3,  # Lower temperature for more focused analysis
                max_tokens=1200
            )
            
            return {
                "question": question,
                "answer": answer.strip(),
                "data": None,
                "query_type": "llm_generated"
            }
        except Exception as e:
            return {
                "question": question,
                "answer": f"Error processing query: {str(e)}",
                "data": None,
                "query_type": "error"
            }
    
    def _prepare_graph_summary(self, graph: CallGraph, max_functions: int = 20) -> str:
        """Prepare a concise summary of the graph for LLM context."""
        total_time = sum(node.total_time for node in graph.nodes.values())
        total_calls = sum(node.call_count for node in graph.nodes.values())
        
        # Get top functions by time
        top_functions = sorted(
            graph.nodes.values(),
            key=lambda n: n.total_time,
            reverse=True
        )[:max_functions]
        
        lines = [
            f"Total execution time: {round(total_time, 3)}s",
            f"Total functions: {len(graph.nodes)}",
            f"Total calls: {total_calls}",
            "",
            "Top functions by execution time:"
        ]
        
        for i, node in enumerate(top_functions, 1):
            pct = (node.total_time / total_time * 100) if total_time > 0 else 0
            lines.append(
                f"{i}. {node.full_name}: {round(node.total_time, 3)}s ({round(pct, 1)}%) - {node.call_count} calls"
            )
        
        return "\n".join(lines)


def query_trace(graph: CallGraph, question: str, provider: Optional[LLMProvider] = None,
               use_llm: bool = True) -> Dict[str, Any]:
    """
    Convenience function to query a trace using natural language.
    
    Args:
        graph: CallGraph to query
        question: Natural language question
        provider: Optional LLM provider (auto-detected if None)
        use_llm: Whether to use LLM for complex queries
    
    Returns:
        Dictionary with answer and data
    
    Example:
        >>> from callflow_tracer import trace_scope
        >>> from callflow_tracer.ai import query_trace
        >>> 
        >>> with trace_scope() as graph:
        >>>     my_application()
        >>> 
        >>> result = query_trace(graph, "Which functions are slowest?")
        >>> print(result['answer'])
    """
    engine = QueryEngine(provider)
    return engine.query(graph, question, use_llm=use_llm)
