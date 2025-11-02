"""
Cost analysis module for CallFlow Tracer.

Calculate infrastructure costs based on execution patterns.
Useful for cloud cost optimization and resource allocation.

Example:
    from callflow_tracer.ai import analyze_costs
    
    costs = analyze_costs(
        graph,
        pricing={
            'compute': 0.0001,  # per ms
            'database': 0.001,  # per query
            'api_call': 0.01    # per call
        }
    )
    
    print(f"Estimated cost: ${costs['total']}")
    print(f"Most expensive: {costs['top_functions']}")
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class FunctionCost:
    """Cost breakdown for a function."""
    function_name: str
    module: str
    execution_count: int
    total_time_ms: float
    compute_cost: float
    estimated_calls: int
    call_cost: float
    total_cost: float
    cost_per_call: float


@dataclass
class CostAnalysis:
    """Complete cost analysis."""
    timestamp: str
    total_cost: float
    compute_cost: float
    database_cost: float
    api_cost: float
    other_cost: float
    function_costs: List[FunctionCost]
    top_functions: List[FunctionCost]
    cost_breakdown: Dict[str, float]
    optimization_opportunities: List[Dict[str, Any]]


class CostAnalyzer:
    """Analyze infrastructure costs from execution traces."""
    
    def __init__(self, pricing: Optional[Dict[str, float]] = None):
        """
        Initialize cost analyzer.
        
        Args:
            pricing: Pricing configuration with keys like 'compute', 'database', 'api_call'
        """
        self.pricing = pricing or self._get_default_pricing()
    
    def _get_default_pricing(self) -> Dict[str, float]:
        """Get default pricing (AWS-like)."""
        return {
            'compute': 0.0001,      # $0.0001 per ms
            'database': 0.001,      # $0.001 per query
            'api_call': 0.01,       # $0.01 per call
            'memory': 0.00001,      # $0.00001 per MB per ms
            'storage': 0.000023,    # $0.000023 per GB per hour
        }
    
    def analyze(self, graph: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze costs from execution trace.
        
        Args:
            graph: Execution trace graph
            
        Returns:
            Cost analysis results
        """
        nodes = self._extract_nodes(graph)
        total_time = self._get_total_time(graph)
        
        function_costs = []
        total_compute_cost = 0.0
        total_database_cost = 0.0
        total_api_cost = 0.0
        
        for node_key, node in nodes.items():
            func_name = node.get('name', 'unknown')
            module = node.get('module', 'unknown')
            total_time_ms = node.get('total_time', 0) * 1000
            call_count = node.get('call_count', 1)
            
            # Compute cost
            compute_cost = total_time_ms * self.pricing['compute']
            total_compute_cost += compute_cost
            
            # Estimate database calls (heuristic: if name contains 'query' or 'db')
            if 'query' in func_name.lower() or 'db' in func_name.lower():
                estimated_db_calls = call_count
                db_cost = estimated_db_calls * self.pricing['database']
                total_database_cost += db_cost
            else:
                db_cost = 0
            
            # Estimate API calls (heuristic: if name contains 'api' or 'request')
            if 'api' in func_name.lower() or 'request' in func_name.lower():
                estimated_api_calls = call_count
                api_cost = estimated_api_calls * self.pricing['api_call']
                total_api_cost += api_cost
            else:
                api_cost = 0
            
            total_cost = compute_cost + db_cost + api_cost
            cost_per_call = total_cost / call_count if call_count > 0 else 0
            
            function_cost = FunctionCost(
                function_name=func_name,
                module=module,
                execution_count=call_count,
                total_time_ms=total_time_ms,
                compute_cost=compute_cost,
                estimated_calls=call_count,
                call_cost=db_cost + api_cost,
                total_cost=total_cost,
                cost_per_call=cost_per_call
            )
            
            function_costs.append(function_cost)
        
        # Sort by total cost
        function_costs.sort(key=lambda x: x.total_cost, reverse=True)
        top_functions = function_costs[:10]
        
        total_cost = total_compute_cost + total_database_cost + total_api_cost
        
        # Find optimization opportunities
        opportunities = self._find_optimization_opportunities(function_costs)
        
        cost_breakdown = {
            'compute': total_compute_cost,
            'database': total_database_cost,
            'api': total_api_cost,
            'total': total_cost
        }
        
        analysis = CostAnalysis(
            timestamp=datetime.now().isoformat(),
            total_cost=total_cost,
            compute_cost=total_compute_cost,
            database_cost=total_database_cost,
            api_cost=total_api_cost,
            other_cost=0.0,
            function_costs=function_costs,
            top_functions=top_functions,
            cost_breakdown=cost_breakdown,
            optimization_opportunities=opportunities
        )
        
        return {
            'timestamp': analysis.timestamp,
            'total_cost': analysis.total_cost,
            'compute_cost': analysis.compute_cost,
            'database_cost': analysis.database_cost,
            'api_cost': analysis.api_cost,
            'function_costs': [asdict(f) for f in analysis.function_costs],
            'top_functions': [asdict(f) for f in analysis.top_functions],
            'cost_breakdown': analysis.cost_breakdown,
            'optimization_opportunities': analysis.optimization_opportunities
        }
    
    def _find_optimization_opportunities(self, function_costs: List[FunctionCost]) -> List[Dict[str, Any]]:
        """Find cost optimization opportunities."""
        opportunities = []
        
        # Find expensive functions
        for func_cost in function_costs[:5]:
            if func_cost.total_cost > 0.01:
                opportunities.append({
                    'function': func_cost.function_name,
                    'type': 'expensive_function',
                    'current_cost': func_cost.total_cost,
                    'recommendation': f"Optimize {func_cost.function_name} - currently costs ${func_cost.total_cost:.4f}",
                    'potential_savings': func_cost.total_cost * 0.3  # 30% savings potential
                })
        
        # Find frequently called functions
        for func_cost in function_costs:
            if func_cost.execution_count > 100:
                opportunities.append({
                    'function': func_cost.function_name,
                    'type': 'high_frequency_calls',
                    'current_cost': func_cost.total_cost,
                    'recommendation': f"Cache results of {func_cost.function_name} (called {func_cost.execution_count} times)",
                    'potential_savings': func_cost.total_cost * 0.5  # 50% savings with caching
                })
                break
        
        # Find database-heavy operations
        db_functions = [f for f in function_costs if 'query' in f.function_name.lower()]
        if db_functions:
            top_db = db_functions[0]
            opportunities.append({
                'function': top_db.function_name,
                'type': 'database_optimization',
                'current_cost': top_db.total_cost,
                'recommendation': f"Batch database queries in {top_db.function_name}",
                'potential_savings': top_db.total_cost * 0.4
            })
        
        return opportunities
    
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
    
    def _get_total_time(self, graph: Dict[str, Any]) -> float:
        """Get total time from graph."""
        if isinstance(graph, dict):
            if 'total_time' in graph:
                return graph['total_time']
            elif 'data' in graph and 'total_time' in graph['data']:
                return graph['data']['total_time']
        return 0.0


def analyze_costs(graph: Dict[str, Any],
                 pricing: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    """
    Analyze infrastructure costs from trace.
    
    Args:
        graph: Execution trace graph
        pricing: Optional pricing configuration
        
    Returns:
        Cost analysis results
    """
    analyzer = CostAnalyzer(pricing)
    return analyzer.analyze(graph)
