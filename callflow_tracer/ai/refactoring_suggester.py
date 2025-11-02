"""
Code refactoring suggestions module for CallFlow Tracer.

AI-powered refactoring recommendations with code examples.
Analyzes execution patterns to suggest structural improvements.

Example:
    from callflow_tracer.ai import suggest_refactoring
    
    suggestions = suggest_refactoring(
        graph,
        include_code_examples=True,
        provider=OpenAIProvider()
    )
    
    for suggestion in suggestions:
        print(f"Function: {suggestion['function']}")
        print(f"Issue: {suggestion['issue']}")
        print(f"Recommendation: {suggestion['recommendation']}")
        print(f"Code example:\\n{suggestion['code_example']}")
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from .llm_provider import LLMProvider


@dataclass
class RefactoringSuggestion:
    """A refactoring suggestion."""
    function_name: str
    module: str
    issue_type: str  # 'long_function', 'high_complexity', 'tight_coupling', etc
    issue: str
    recommendation: str
    code_example: str
    impact: str  # 'high', 'medium', 'low'
    effort: str  # 'low', 'medium', 'high'
    priority: int  # 1-5, higher is more important


class RefactoringSuggester:
    """Suggest code refactoring improvements."""
    
    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        """
        Initialize refactoring suggester.
        
        Args:
            llm_provider: Optional LLM provider for enhanced suggestions
        """
        self.llm_provider = llm_provider
    
    def suggest_refactoring(self, graph: Dict[str, Any],
                           include_code_examples: bool = True) -> List[Dict[str, Any]]:
        """
        Suggest refactoring improvements.
        
        Args:
            graph: Execution trace graph
            include_code_examples: Include code examples in suggestions
            
        Returns:
            List of refactoring suggestions
        """
        suggestions = []
        nodes = self._extract_nodes(graph)
        
        # Analyze each function
        for node_key, node in nodes.items():
            node_suggestions = self._analyze_node(node, include_code_examples)
            suggestions.extend(node_suggestions)
        
        # Analyze overall structure
        structure_suggestions = self._analyze_structure(nodes, include_code_examples)
        suggestions.extend(structure_suggestions)
        
        # Sort by priority and impact
        suggestions.sort(
            key=lambda x: (x['priority'], x['impact'] != 'low'),
            reverse=True
        )
        
        return [asdict(s) if isinstance(s, RefactoringSuggestion) else s 
                for s in suggestions]
    
    def _analyze_node(self, node: Dict[str, Any],
                     include_code_examples: bool) -> List[RefactoringSuggestion]:
        """Analyze a single node for refactoring opportunities."""
        suggestions = []
        
        func_name = node.get('name', 'unknown')
        module = node.get('module', 'unknown')
        total_time = node.get('total_time', 0)
        call_count = node.get('call_count', 1)
        
        # Check for long-running functions
        if total_time > 1.0:
            suggestion = RefactoringSuggestion(
                function_name=func_name,
                module=module,
                issue_type='long_function',
                issue=f"Function takes {total_time:.2f}s to execute",
                recommendation="Break into smaller functions or optimize hot paths",
                code_example=self._get_long_function_example() if include_code_examples else "",
                impact='high',
                effort='medium',
                priority=5
            )
            suggestions.append(suggestion)
        
        # Check for frequently called functions
        if call_count > 100:
            suggestion = RefactoringSuggestion(
                function_name=func_name,
                module=module,
                issue_type='high_call_frequency',
                issue=f"Function called {call_count} times",
                recommendation="Consider caching results or batching operations",
                code_example=self._get_caching_example() if include_code_examples else "",
                impact='high',
                effort='low',
                priority=4
            )
            suggestions.append(suggestion)
        
        # Check for potential N+1 patterns
        if call_count > 10 and total_time > 0.1:
            avg_time = total_time / call_count
            if avg_time > 0.01:  # Each call takes >10ms
                suggestion = RefactoringSuggestion(
                    function_name=func_name,
                    module=module,
                    issue_type='potential_n_plus_one',
                    issue=f"Function called {call_count} times with {avg_time*1000:.1f}ms per call",
                    recommendation="Check for N+1 query patterns, consider batching",
                    code_example=self._get_n_plus_one_example() if include_code_examples else "",
                    impact='high',
                    effort='medium',
                    priority=5
                )
                suggestions.append(suggestion)
        
        return suggestions
    
    def _analyze_structure(self, nodes: Dict[str, Dict[str, Any]],
                          include_code_examples: bool) -> List[RefactoringSuggestion]:
        """Analyze overall code structure."""
        suggestions = []
        
        # Find tightly coupled functions
        tight_couplings = self._find_tight_couplings(nodes)
        for coupling in tight_couplings:
            suggestion = RefactoringSuggestion(
                function_name=coupling['functions'][0],
                module='multiple',
                issue_type='tight_coupling',
                issue=f"Functions {coupling['functions']} are tightly coupled",
                recommendation="Extract common logic into separate module",
                code_example=self._get_decoupling_example() if include_code_examples else "",
                impact='medium',
                effort='high',
                priority=3
            )
            suggestions.append(suggestion)
        
        # Find unused functions
        unused = self._find_unused_functions(nodes)
        for func in unused:
            suggestion = RefactoringSuggestion(
                function_name=func['name'],
                module=func['module'],
                issue_type='unused_function',
                issue="Function is never called",
                recommendation="Remove dead code or add to public API",
                code_example="",
                impact='low',
                effort='low',
                priority=1
            )
            suggestions.append(suggestion)
        
        return suggestions
    
    def _find_tight_couplings(self, nodes: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find tightly coupled functions."""
        couplings = []
        
        # Group by module
        modules = {}
        for node_key, node in nodes.items():
            module = node.get('module', 'unknown')
            if module not in modules:
                modules[module] = []
            modules[module].append(node.get('name', 'unknown'))
        
        # Find modules with many functions calling each other
        for module, functions in modules.items():
            if len(functions) > 5:
                couplings.append({
                    'module': module,
                    'functions': functions[:3],
                    'count': len(functions)
                })
        
        return couplings
    
    def _find_unused_functions(self, nodes: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find unused functions."""
        unused = []
        
        for node_key, node in nodes.items():
            call_count = node.get('call_count', 0)
            if call_count == 0:
                unused.append({
                    'name': node.get('name', 'unknown'),
                    'module': node.get('module', 'unknown')
                })
        
        return unused
    
    def _get_long_function_example(self) -> str:
        """Get example for long function refactoring."""
        return """# Before - Long function
def process_user_data(user_id):
    # 500 lines of code...
    user = fetch_user(user_id)
    orders = fetch_orders(user_id)
    analytics = compute_analytics(orders)
    # ... more processing
    return result

# After - Refactored
def process_user_data(user_id):
    user = fetch_user(user_id)
    orders = fetch_orders(user_id)
    return compute_user_summary(user, orders)

def compute_user_summary(user, orders):
    analytics = compute_analytics(orders)
    return {
        'user': user,
        'orders': orders,
        'analytics': analytics
    }"""
    
    def _get_caching_example(self) -> str:
        """Get example for caching."""
        return """# Before - No caching
def get_user_profile(user_id):
    return database.query(f"SELECT * FROM users WHERE id={user_id}")

# After - With caching
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_user_profile(user_id):
    return database.query(f"SELECT * FROM users WHERE id={user_id}")"""
    
    def _get_n_plus_one_example(self) -> str:
        """Get example for N+1 pattern."""
        return """# Before - N+1 queries
def get_user_orders(user_id):
    orders = []
    for order_id in get_order_ids(user_id):
        orders.append(get_order(order_id))  # N+1!
    return orders

# After - Batch query
def get_user_orders(user_id):
    order_ids = get_order_ids(user_id)
    return get_orders_batch(order_ids)  # Single query!"""
    
    def _get_decoupling_example(self) -> str:
        """Get example for decoupling."""
        return """# Before - Tightly coupled
class UserService:
    def process(self):
        self.validate()
        self.transform()
        self.persist()

# After - Decoupled
class UserValidator:
    def validate(self, user):
        # Validation logic
        pass

class UserTransformer:
    def transform(self, user):
        # Transform logic
        pass

class UserRepository:
    def persist(self, user):
        # Persistence logic
        pass"""
    
    def _extract_nodes(self, graph: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Extract nodes from graph."""
        nodes = {}
        
        if isinstance(graph, dict):
            if 'nodes' in graph:
                for node in graph['nodes']:
                    key = f"{node.get('module', 'unknown')}:{node.get('name', 'unknown')}"
                    nodes[key] = node
            elif 'data' in graph and 'nodes' in graph['data']:
                for node in graph['data']['nodes']:
                    key = f"{node.get('module', 'unknown')}:{node.get('name', 'unknown')}"
                    nodes[key] = node
        
        return nodes


def suggest_refactoring(graph: Dict[str, Any],
                       include_code_examples: bool = True,
                       provider: Optional[LLMProvider] = None) -> List[Dict[str, Any]]:
    """
    Suggest code refactoring improvements.
    
    Args:
        graph: Execution trace graph
        include_code_examples: Include code examples
        provider: Optional LLM provider
        
    Returns:
        List of refactoring suggestions
    """
    suggester = RefactoringSuggester(provider)
    return suggester.suggest_refactoring(graph, include_code_examples)
