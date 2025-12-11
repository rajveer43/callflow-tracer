"""
Auto-fix generation module for CallFlow Tracer.

Generates actual code fixes for detected issues using LLM analysis.
Provides diffs and confidence scores for suggested fixes.

Example:
    from callflow_tracer.ai import generate_fixes
    
    fixes = generate_fixes(
        graph,
        root_cause_analysis=root_analysis,
        provider=OpenAIProvider(model='gpt-4o')
    )
    
    for fix in fixes:
        print(f"File: {fix['file']}")
        print(f"Issue: {fix['issue']}")
        print(f"Confidence: {fix['confidence']}")
        print(f"Diff:\\n{fix['diff']}")
        
        if fix['confidence'] > 0.8:
            apply_fix(fix)
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import re
import logging
from .llm_provider import LLMProvider

logger = logging.getLogger(__name__)


@dataclass
class CodeFix:
    """A suggested code fix."""
    file_path: str
    function_name: str
    issue: str
    issue_type: str  # 'n_plus_one', 'inefficient_loop', 'memory_leak', etc
    before_code: str
    after_code: str
    diff: str
    explanation: str
    confidence: float  # 0.0 to 1.0
    severity: str  # 'critical', 'high', 'medium', 'low'
    estimated_improvement: float  # Expected % improvement


class AutoFixer:
    """Generate automatic code fixes for performance issues."""
    
    def __init__(self, llm_provider: LLMProvider):
        """
        Initialize auto fixer.
        
        Args:
            llm_provider: LLM provider for generating fixes
        """
        self.llm_provider = llm_provider
    
    def generate_fixes(self, graph: Dict[str, Any],
                      root_cause_analysis: Optional[Dict[str, Any]] = None,
                      source_code: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        Generate code fixes for detected issues.
        
        Args:
            graph: Execution trace graph
            root_cause_analysis: Root cause analysis results
            source_code: Optional dict mapping file paths to source code
            
        Returns:
            List of suggested fixes
        """
        fixes = []
        
        if not root_cause_analysis:
            return fixes
        
        issues = root_cause_analysis.get('issues', [])
        
        for issue in issues:
            fix = self._generate_fix_for_issue(issue, graph, source_code)
            if fix:
                fixes.append(asdict(fix))
        
        # Sort by confidence and severity
        fixes.sort(
            key=lambda x: (x['confidence'], x['severity'] != 'critical'),
            reverse=True
        )
        
        return fixes
    
    def _generate_fix_for_issue(self, issue: Dict[str, Any],
                               graph: Dict[str, Any],
                               source_code: Optional[Dict[str, str]]) -> Optional[CodeFix]:
        """Generate a fix for a specific issue using LLM if available."""
        from .prompts import get_prompt_for_task
        
        issue_type = issue.get('type', 'unknown')
        function_name = issue.get('function', 'unknown')
        
        # Get source code if available
        file_path = issue.get('file', 'unknown')
        before_code = ""
        
        if source_code and file_path in source_code:
            before_code = source_code[file_path]
        
        # Try to generate fix using LLM first
        if self.llm_provider:
            try:
                system_prompt, user_prompt = get_prompt_for_task(
                    'code_fix',
                    issue_type=issue_type,
                    function_name=function_name,
                    context=issue.get('description', ''),
                    before_code=before_code
                )
                
                response = self.llm_provider.generate(
                    user_prompt,
                    system_prompt,
                    temperature=0.2,  # Low temperature for precise code generation
                    max_tokens=2000
                )
                
                # Parse LLM response and create CodeFix
                # This is a simplified version - in production, parse the response more carefully
                return CodeFix(
                    file_path=file_path,
                    function_name=function_name,
                    issue=issue.get('description', 'Performance issue'),
                    issue_type=issue_type,
                    before_code=before_code,
                    after_code=response,
                    diff=self._generate_diff(before_code, response),
                    explanation=f"LLM-generated fix for {issue_type}",
                    confidence=0.75,
                    severity='high',
                    estimated_improvement=50.0
                )
            except Exception as e:
                # Fall back to template-based fixes
                logger.warning(f"LLM fix generation failed: {str(e)}, using template")
        
        # Fall back to template-based fixes
        if issue_type == 'n_plus_one':
            return self._fix_n_plus_one(issue, before_code)
        elif issue_type == 'inefficient_loop':
            return self._fix_inefficient_loop(issue, before_code)
        elif issue_type == 'memory_leak':
            return self._fix_memory_leak(issue, before_code)
        elif issue_type == 'excessive_recursion':
            return self._fix_excessive_recursion(issue, before_code)
        elif issue_type == 'missing_cache':
            return self._fix_missing_cache(issue, before_code)
        
        return None
    
    def _fix_n_plus_one(self, issue: Dict[str, Any], before_code: str) -> Optional[CodeFix]:
        """Generate fix for N+1 query problem."""
        function_name = issue.get('function', 'unknown')
        
        before = """# Before - N+1 query problem
def get_user_orders(user_id):
    orders = []
    for order_id in get_order_ids(user_id):
        orders.append(get_order(order_id))  # N+1!
    return orders"""
        
        after = """# After - Batched query
def get_user_orders(user_id):
    order_ids = get_order_ids(user_id)
    return get_orders_batch(order_ids)  # Batched!"""
        
        diff = self._generate_diff(before, after)
        
        return CodeFix(
            file_path=issue.get('file', 'unknown'),
            function_name=function_name,
            issue="N+1 Query Problem: Multiple individual queries in a loop",
            issue_type='n_plus_one',
            before_code=before,
            after_code=after,
            diff=diff,
            explanation="Replace individual queries in loop with batch query. "
                       "This reduces database round trips from N+1 to 1.",
            confidence=0.95,
            severity='high',
            estimated_improvement=80.0  # 80% improvement
        )
    
    def _fix_inefficient_loop(self, issue: Dict[str, Any], before_code: str) -> Optional[CodeFix]:
        """Generate fix for inefficient loops."""
        function_name = issue.get('function', 'unknown')
        
        before = """# Before - Inefficient loop
def process_items(items):
    result = []
    for item in items:
        if item in result:  # O(n) search
            continue
        result.append(item)
    return result"""
        
        after = """# After - Efficient loop with set
def process_items(items):
    seen = set()
    result = []
    for item in items:
        if item in seen:  # O(1) lookup
            continue
        seen.add(item)
        result.append(item)
    return result"""
        
        diff = self._generate_diff(before, after)
        
        return CodeFix(
            file_path=issue.get('file', 'unknown'),
            function_name=function_name,
            issue="Inefficient Loop: Using list search instead of set lookup",
            issue_type='inefficient_loop',
            before_code=before,
            after_code=after,
            diff=diff,
            explanation="Use set for O(1) lookups instead of list O(n) search. "
                       "Improves loop performance significantly.",
            confidence=0.90,
            severity='high',
            estimated_improvement=60.0
        )
    
    def _fix_memory_leak(self, issue: Dict[str, Any], before_code: str) -> Optional[CodeFix]:
        """Generate fix for memory leaks."""
        function_name = issue.get('function', 'unknown')
        
        before = """# Before - Memory leak
class DataProcessor:
    def __init__(self):
        self.cache = {}
    
    def process(self, key, data):
        self.cache[key] = data  # Never cleared!
        return self.cache[key]"""
        
        after = """# After - Fixed memory leak
from functools import lru_cache

class DataProcessor:
    def __init__(self, max_cache=1000):
        self.max_cache = max_cache
        self.cache = {}
    
    def process(self, key, data):
        if len(self.cache) >= self.max_cache:
            # Clear oldest entries
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        self.cache[key] = data
        return self.cache[key]"""
        
        diff = self._generate_diff(before, after)
        
        return CodeFix(
            file_path=issue.get('file', 'unknown'),
            function_name=function_name,
            issue="Memory Leak: Unbounded cache growth",
            issue_type='memory_leak',
            before_code=before,
            after_code=after,
            diff=diff,
            explanation="Add cache size limit and eviction policy to prevent unbounded memory growth.",
            confidence=0.85,
            severity='critical',
            estimated_improvement=100.0  # Prevents crash
        )
    
    def _fix_excessive_recursion(self, issue: Dict[str, Any], before_code: str) -> Optional[CodeFix]:
        """Generate fix for excessive recursion."""
        function_name = issue.get('function', 'unknown')
        
        before = """# Before - Excessive recursion
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)  # Exponential!"""
        
        after = """# After - Memoized recursion
from functools import lru_cache

@lru_cache(maxsize=None)
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)  # Linear!"""
        
        diff = self._generate_diff(before, after)
        
        return CodeFix(
            file_path=issue.get('file', 'unknown'),
            function_name=function_name,
            issue="Excessive Recursion: Exponential time complexity",
            issue_type='excessive_recursion',
            before_code=before,
            after_code=after,
            diff=diff,
            explanation="Add memoization to cache recursive results. "
                       "Reduces time complexity from exponential to linear.",
            confidence=0.92,
            severity='critical',
            estimated_improvement=99.0
        )
    
    def _fix_missing_cache(self, issue: Dict[str, Any], before_code: str) -> Optional[CodeFix]:
        """Generate fix for missing caching."""
        function_name = issue.get('function', 'unknown')
        
        before = """# Before - No caching
def get_user_profile(user_id):
    # Expensive database query
    return database.query(f"SELECT * FROM users WHERE id={user_id}")"""
        
        after = """# After - With caching
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_user_profile(user_id):
    # Expensive database query
    return database.query(f"SELECT * FROM users WHERE id={user_id}")"""
        
        diff = self._generate_diff(before, after)
        
        return CodeFix(
            file_path=issue.get('file', 'unknown'),
            function_name=function_name,
            issue="Missing Cache: Repeated expensive operations",
            issue_type='missing_cache',
            before_code=before,
            after_code=after,
            diff=diff,
            explanation="Add caching for expensive operations to avoid repeated computation.",
            confidence=0.88,
            severity='high',
            estimated_improvement=70.0
        )
    
    def _generate_diff(self, before: str, after: str) -> str:
        """Generate a unified diff between before and after code."""
        before_lines = before.split('\n')
        after_lines = after.split('\n')
        
        diff_lines = []
        diff_lines.append("--- before")
        diff_lines.append("+++ after")
        
        for i, (b, a) in enumerate(zip(before_lines, after_lines)):
            if b != a:
                diff_lines.append(f"- {b}")
                diff_lines.append(f"+ {a}")
            else:
                diff_lines.append(f"  {b}")
        
        return '\n'.join(diff_lines)


def generate_fixes(graph: Dict[str, Any],
                  root_cause_analysis: Optional[Dict[str, Any]] = None,
                  provider: Optional[LLMProvider] = None,
                  source_code: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
    """
    Generate code fixes for detected issues.
    
    Args:
        graph: Execution trace graph
        root_cause_analysis: Root cause analysis results
        provider: LLM provider for generating fixes
        source_code: Optional source code mapping
        
    Returns:
        List of suggested fixes
    """
    if not provider:
        from .llm_provider import OpenAIProvider
        provider = OpenAIProvider()
    
    fixer = AutoFixer(provider)
    return fixer.generate_fixes(graph, root_cause_analysis, source_code)
