"""
Security and privacy analysis module for CallFlow Tracer.

Detect security issues and data leaks in execution traces.
Identifies sensitive data exposure, insecure functions, and permission issues.

Example:
    from callflow_tracer.ai import analyze_security
    
    security = analyze_security(graph)
    
    print(security['sensitive_data_exposure'])
    print(security['insecure_functions'])
    print(security['excessive_permissions'])
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import re


@dataclass
class SecurityIssue:
    """A security issue."""
    issue_type: str  # 'pii_exposure', 'sql_injection', 'insecure_crypto', etc
    severity: str  # 'critical', 'high', 'medium', 'low'
    function_name: str
    description: str
    recommendation: str
    affected_data: Optional[str] = None


class SecurityAnalyzer:
    """Analyze security issues in execution traces."""
    
    def __init__(self):
        """Initialize security analyzer."""
        # Patterns for sensitive data
        self.pii_patterns = {
            'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
            'api_key': r'[a-zA-Z0-9_-]{32,}',
            'password': r'password\s*=\s*["\'].*?["\']',
        }
        
        # Insecure function patterns
        self.insecure_functions = {
            'eval': 'Using eval() is dangerous',
            'exec': 'Using exec() is dangerous',
            'pickle': 'Using pickle is insecure',
            'subprocess.call': 'Using subprocess.call without shell=False',
            'os.system': 'Using os.system is insecure',
        }
    
    def analyze(self, graph: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze security issues in trace.
        
        Args:
            graph: Execution trace graph
            
        Returns:
            Security analysis results
        """
        nodes = self._extract_nodes(graph)
        
        issues = []
        pii_exposure = []
        insecure_functions = []
        excessive_permissions = []
        
        # Analyze each function
        for node_key, node in nodes.items():
            func_name = node.get('name', 'unknown')
            module = node.get('module', 'unknown')
            
            # Check for insecure functions
            for insecure_func, description in self.insecure_functions.items():
                if insecure_func in func_name.lower():
                    issue = SecurityIssue(
                        issue_type='insecure_function',
                        severity='high',
                        function_name=func_name,
                        description=description,
                        recommendation=f"Replace {insecure_func} with safer alternative"
                    )
                    insecure_functions.append(issue)
                    issues.append(issue)
            
            # Check for excessive permissions
            if 'admin' in func_name.lower() or 'root' in func_name.lower():
                call_count = node.get('call_count', 0)
                if call_count > 10:
                    issue = SecurityIssue(
                        issue_type='excessive_permissions',
                        severity='high',
                        function_name=func_name,
                        description=f"Privileged function called {call_count} times",
                        recommendation="Limit privileged operations to necessary calls only"
                    )
                    excessive_permissions.append(issue)
                    issues.append(issue)
        
        # Check for potential SQL injection
        sql_injection_issues = self._check_sql_injection(nodes)
        issues.extend(sql_injection_issues)
        
        # Check for crypto issues
        crypto_issues = self._check_crypto_issues(nodes)
        issues.extend(crypto_issues)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_issues': len(issues),
            'critical_issues': len([i for i in issues if i.severity == 'critical']),
            'high_issues': len([i for i in issues if i.severity == 'high']),
            'sensitive_data_exposure': [asdict(i) for i in pii_exposure],
            'insecure_functions': [asdict(i) for i in insecure_functions],
            'excessive_permissions': [asdict(i) for i in excessive_permissions],
            'sql_injection_risks': [asdict(i) for i in sql_injection_issues],
            'crypto_issues': [asdict(i) for i in crypto_issues],
            'all_issues': [asdict(i) for i in issues],
            'recommendations': self._generate_recommendations(issues)
        }
    
    def _check_sql_injection(self, nodes: Dict[str, Dict[str, Any]]) -> List[SecurityIssue]:
        """Check for SQL injection vulnerabilities."""
        issues = []
        
        for node_key, node in nodes.items():
            func_name = node.get('name', 'unknown')
            
            # Heuristic: functions with 'query' or 'sql' in name that are called frequently
            if ('query' in func_name.lower() or 'sql' in func_name.lower()):
                call_count = node.get('call_count', 0)
                
                if call_count > 5:
                    issue = SecurityIssue(
                        issue_type='sql_injection_risk',
                        severity='high',
                        function_name=func_name,
                        description=f"SQL function called {call_count} times - potential injection risk",
                        recommendation="Use parameterized queries and prepared statements"
                    )
                    issues.append(issue)
        
        return issues
    
    def _check_crypto_issues(self, nodes: Dict[str, Dict[str, Any]]) -> List[SecurityIssue]:
        """Check for cryptography issues."""
        issues = []
        
        insecure_crypto = ['md5', 'sha1', 'des', 'rc4']
        
        for node_key, node in nodes.items():
            func_name = node.get('name', 'unknown').lower()
            
            for insecure in insecure_crypto:
                if insecure in func_name:
                    issue = SecurityIssue(
                        issue_type='weak_crypto',
                        severity='high',
                        function_name=node.get('name', 'unknown'),
                        description=f"Using weak cryptography: {insecure}",
                        recommendation=f"Replace {insecure} with SHA-256 or stronger"
                    )
                    issues.append(issue)
                    break
        
        return issues
    
    def _generate_recommendations(self, issues: List[SecurityIssue]) -> List[str]:
        """Generate security recommendations."""
        recommendations = []
        
        if not issues:
            recommendations.append("✅ No security issues detected")
            return recommendations
        
        critical = [i for i in issues if i.severity == 'critical']
        high = [i for i in issues if i.severity == 'high']
        
        if critical:
            recommendations.append(
                f"🔴 CRITICAL: {len(critical)} critical security issue(s) found. "
                f"Address immediately: {critical[0].description}"
            )
        
        if high:
            recommendations.append(
                f"⚠️ HIGH: {len(high)} high-severity issue(s) found. "
                f"Review and fix: {high[0].description}"
            )
        
        # Specific recommendations
        issue_types = set(i.issue_type for i in issues)
        
        if 'sql_injection_risk' in issue_types:
            recommendations.append(
                "🛡️ Use parameterized queries and prepared statements to prevent SQL injection"
            )
        
        if 'weak_crypto' in issue_types:
            recommendations.append(
                "🔐 Update cryptographic algorithms to SHA-256 or stronger"
            )
        
        if 'insecure_function' in issue_types:
            recommendations.append(
                "⚠️ Replace unsafe functions (eval, exec, pickle) with safer alternatives"
            )
        
        if 'excessive_permissions' in issue_types:
            recommendations.append(
                "👤 Implement principle of least privilege - limit admin/root operations"
            )
        
        return recommendations
    
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


def analyze_security(graph: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze security issues in trace.
    
    Args:
        graph: Execution trace graph
        
    Returns:
        Security analysis results
    """
    analyzer = SecurityAnalyzer()
    return analyzer.analyze(graph)
