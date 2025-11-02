"""
Test generation module for CallFlow Tracer.

Automatically generates performance tests from execution traces.
Supports pytest and unittest frameworks with timing assertions.

Example:
    from callflow_tracer.ai import generate_performance_tests
    
    tests = generate_performance_tests(
        graph,
        test_framework='pytest',
        include_assertions=True
    )
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class GeneratedTest:
    """A generated test."""
    test_name: str
    test_code: str
    framework: str  # 'pytest', 'unittest'
    assertions: List[str]
    test_type: str  # 'performance', 'regression', 'load', 'integration'


class TestGenerator:
    """Generate performance tests from traces."""
    
    def __init__(self, test_framework: str = 'pytest'):
        """
        Initialize test generator.
        
        Args:
            test_framework: Test framework ('pytest' or 'unittest')
        """
        self.test_framework = test_framework
    
    def generate_tests(self, graph: Dict[str, Any],
                      include_assertions: bool = True,
                      include_load_tests: bool = False) -> List[Dict[str, Any]]:
        """
        Generate tests from execution trace.
        
        Args:
            graph: Execution trace graph
            include_assertions: Include timing assertions
            include_load_tests: Include load tests
            
        Returns:
            List of generated tests
        """
        tests = []
        
        # Extract test data from graph
        nodes = self._extract_nodes(graph)
        total_time = self._get_total_time(graph)
        
        # Generate performance regression test
        perf_test = self._generate_performance_test(
            nodes, total_time, include_assertions
        )
        tests.append(perf_test)
        
        # Generate integration test
        integration_test = self._generate_integration_test(nodes)
        tests.append(integration_test)
        
        # Generate load test if requested
        if include_load_tests:
            load_test = self._generate_load_test(nodes, total_time)
            tests.append(load_test)
        
        return [self._format_test(t) for t in tests]
    
    def _generate_performance_test(self, nodes: Dict[str, Dict[str, Any]],
                                   total_time: float,
                                   include_assertions: bool) -> GeneratedTest:
        """Generate performance regression test."""
        test_name = "test_performance_regression"
        
        # Build test code
        if self.test_framework == 'pytest':
            test_code = self._generate_pytest_performance_test(
                nodes, total_time, include_assertions
            )
        else:
            test_code = self._generate_unittest_performance_test(
                nodes, total_time, include_assertions
            )
        
        assertions = self._extract_assertions(nodes, total_time)
        
        return GeneratedTest(
            test_name=test_name,
            test_code=test_code,
            framework=self.test_framework,
            assertions=assertions,
            test_type='performance'
        )
    
    def _generate_pytest_performance_test(self, nodes: Dict[str, Dict[str, Any]],
                                         total_time: float,
                                         include_assertions: bool) -> str:
        """Generate pytest performance test."""
        code = f'''"""
Auto-generated performance regression test.
Generated: {datetime.now().isoformat()}
"""

import pytest
from callflow_tracer import trace_scope


def test_performance_regression():
    """Performance regression test - ensures no significant slowdown."""
    with trace_scope() as graph:
        # TODO: Call your function here
        pass
    
    # Assertions
    assert graph.total_time < {total_time * 1.1:.3f}, \\
        f"Performance regression: {{graph.total_time}} > {total_time * 1.1:.3f}s"
'''
        
        # Add function-level assertions
        if include_assertions:
            for node_key, node in list(nodes.items())[:5]:  # Top 5 functions
                func_name = node.get('name', 'unknown')
                func_time = node.get('total_time', 0)
                
                code += f'''
    
    # {func_name} should not exceed {func_time * 1.2:.3f}s
    node = graph.get_node('{func_name}')
    if node:
        assert node.total_time < {func_time * 1.2:.3f}, \\
            f"{{node.name}} regression: {{node.total_time}} > {func_time * 1.2:.3f}s"
'''
        
        return code
    
    def _generate_unittest_performance_test(self, nodes: Dict[str, Dict[str, Any]],
                                           total_time: float,
                                           include_assertions: bool) -> str:
        """Generate unittest performance test."""
        code = f'''"""
Auto-generated performance regression test.
Generated: {datetime.now().isoformat()}
"""

import unittest
from callflow_tracer import trace_scope


class TestPerformanceRegression(unittest.TestCase):
    """Performance regression tests."""
    
    def test_overall_performance(self):
        """Test overall performance hasn't regressed."""
        with trace_scope() as graph:
            # TODO: Call your function here
            pass
        
        self.assertLess(
            graph.total_time,
            {total_time * 1.1:.3f},
            f"Performance regression: {{graph.total_time}} > {total_time * 1.1:.3f}s"
        )
'''
        
        # Add function-level tests
        if include_assertions:
            for i, (node_key, node) in enumerate(list(nodes.items())[:5]):
                func_name = node.get('name', 'unknown')
                func_time = node.get('total_time', 0)
                test_method = f"test_{func_name.lower().replace(' ', '_')}"
                
                code += f'''
    
    def {test_method}(self):
        """Test {func_name} performance."""
        with trace_scope() as graph:
            # TODO: Call your function here
            pass
        
        node = graph.get_node('{func_name}')
        self.assertIsNotNone(node, "{func_name} not found in trace")
        self.assertLess(
            node.total_time,
            {func_time * 1.2:.3f},
            f"{{node.name}} regression: {{node.total_time}} > {func_time * 1.2:.3f}s"
        )
'''
        
        code += '''

if __name__ == '__main__':
    unittest.main()
'''
        
        return code
    
    def _generate_integration_test(self, nodes: Dict[str, Dict[str, Any]]) -> GeneratedTest:
        """Generate integration test."""
        test_name = "test_integration"
        
        if self.test_framework == 'pytest':
            test_code = f'''"""
Auto-generated integration test.
Generated: {datetime.now().isoformat()}
"""

import pytest
from callflow_tracer import trace_scope


def test_integration():
    """Integration test - verifies all components work together."""
    with trace_scope() as graph:
        # TODO: Call your function here
        pass
    
    # Verify all expected functions are called
    assert graph.node_count > 0, "No functions traced"
    assert graph.total_time > 0, "No execution time recorded"
'''
        else:
            test_code = f'''"""
Auto-generated integration test.
Generated: {datetime.now().isoformat()}
"""

import unittest
from callflow_tracer import trace_scope


class TestIntegration(unittest.TestCase):
    """Integration tests."""
    
    def test_integration(self):
        """Integration test - verifies all components work together."""
        with trace_scope() as graph:
            # TODO: Call your function here
            pass
        
        self.assertGreater(graph.node_count, 0, "No functions traced")
        self.assertGreater(graph.total_time, 0, "No execution time recorded")


if __name__ == '__main__':
    unittest.main()
'''
        
        return GeneratedTest(
            test_name=test_name,
            test_code=test_code,
            framework=self.test_framework,
            assertions=["node_count > 0", "total_time > 0"],
            test_type='integration'
        )
    
    def _generate_load_test(self, nodes: Dict[str, Dict[str, Any]],
                           total_time: float) -> GeneratedTest:
        """Generate load test."""
        test_name = "test_load"
        
        if self.test_framework == 'pytest':
            test_code = f'''"""
Auto-generated load test.
Generated: {datetime.now().isoformat()}
"""

import pytest
import concurrent.futures
from callflow_tracer import trace_scope


@pytest.mark.performance
def test_load_concurrent_10():
    """Load test with 10 concurrent requests."""
    def run_request():
        with trace_scope() as graph:
            # TODO: Call your function here
            pass
        return graph.total_time
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        times = list(executor.map(lambda _: run_request(), range(10)))
    
    avg_time = sum(times) / len(times)
    assert avg_time < {total_time * 1.5:.3f}, \\
        f"Load test failed: avg {{avg_time}} > {total_time * 1.5:.3f}s"


@pytest.mark.performance
def test_load_concurrent_50():
    """Load test with 50 concurrent requests."""
    def run_request():
        with trace_scope() as graph:
            # TODO: Call your function here
            pass
        return graph.total_time
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        times = list(executor.map(lambda _: run_request(), range(50)))
    
    avg_time = sum(times) / len(times)
    assert avg_time < {total_time * 2.0:.3f}, \\
        f"Load test failed: avg {{avg_time}} > {total_time * 2.0:.3f}s"
'''
        else:
            test_code = f'''"""
Auto-generated load test.
Generated: {datetime.now().isoformat()}
"""

import unittest
import concurrent.futures
from callflow_tracer import trace_scope


class TestLoad(unittest.TestCase):
    """Load tests."""
    
    def test_load_concurrent_10(self):
        """Load test with 10 concurrent requests."""
        def run_request():
            with trace_scope() as graph:
                # TODO: Call your function here
                pass
            return graph.total_time
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            times = list(executor.map(lambda _: run_request(), range(10)))
        
        avg_time = sum(times) / len(times)
        self.assertLess(
            avg_time,
            {total_time * 1.5:.3f},
            f"Load test failed: avg {{avg_time}} > {total_time * 1.5:.3f}s"
        )


if __name__ == '__main__':
    unittest.main()
'''
        
        return GeneratedTest(
            test_name=test_name,
            test_code=test_code,
            framework=self.test_framework,
            assertions=[f"avg_time < {total_time * 1.5:.3f}"],
            test_type='load'
        )
    
    def _extract_assertions(self, nodes: Dict[str, Dict[str, Any]],
                           total_time: float) -> List[str]:
        """Extract assertions from nodes."""
        assertions = [
            f"total_time < {total_time * 1.1:.3f}s",
            f"node_count > 0",
        ]
        
        for node_key, node in list(nodes.items())[:3]:
            func_name = node.get('name', 'unknown')
            func_time = node.get('total_time', 0)
            call_count = node.get('call_count', 0)
            
            assertions.append(f"{func_name} < {func_time * 1.2:.3f}s")
            if call_count > 0:
                assertions.append(f"{func_name} call_count <= {call_count}")
        
        return assertions
    
    def _format_test(self, test: GeneratedTest) -> Dict[str, Any]:
        """Format test for output."""
        return {
            'test_name': test.test_name,
            'test_code': test.test_code,
            'framework': test.framework,
            'assertions': test.assertions,
            'test_type': test.test_type
        }
    
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


def generate_performance_tests(graph: Dict[str, Any],
                              test_framework: str = 'pytest',
                              include_assertions: bool = True,
                              include_load_tests: bool = False) -> List[Dict[str, Any]]:
    """
    Generate performance tests from trace.
    
    Args:
        graph: Execution trace graph
        test_framework: Test framework ('pytest' or 'unittest')
        include_assertions: Include timing assertions
        include_load_tests: Include load tests
        
    Returns:
        List of generated tests
    """
    generator = TestGenerator(test_framework)
    return generator.generate_tests(graph, include_assertions, include_load_tests)
