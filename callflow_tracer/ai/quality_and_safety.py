"""
Quality and safety mechanisms for AI-generated code.

Provides:
- Safety filters for generated code
- Cost and token tracking
- Audit logging
- Compliance checking
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging
import json
from pathlib import Path
import subprocess

logger = logging.getLogger(__name__)


@dataclass
class SafetyCheckResult:
    """Result from safety checks."""
    passed: bool
    checks_run: List[str]
    issues_found: List[Dict[str, Any]]
    severity_levels: Dict[str, int]  # e.g., {"critical": 0, "high": 2}
    recommendations: List[str]


@dataclass
class CostRecord:
    """Record of AI API cost."""
    timestamp: datetime
    task_type: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    duration_ms: float


@dataclass
class AuditLogEntry:
    """Entry in AI audit log."""
    timestamp: datetime
    task_type: str
    model: str
    prompt_hash: str
    response_hash: str
    cost_usd: float
    safety_passed: bool
    issues_found: List[str]


class SafetyChecker:
    """
    Validates AI-generated code for safety.
    
    Checks:
    - No hardcoded secrets
    - No dangerous functions
    - Valid Python syntax
    - Type hints present
    - No SQL injection vulnerabilities
    """
    
    def __init__(self):
        """Initialize safety checker."""
        self.dangerous_patterns = [
            r"os\.system",
            r"eval\(",
            r"exec\(",
            r"__import__",
            r"pickle\.load",
            r"subprocess\.call\(",
        ]
        
        self.secret_patterns = [
            r"api[_-]?key\s*=",
            r"password\s*=",
            r"secret\s*=",
            r"token\s*=",
            r"aws_access_key",
        ]
    
    def check_code(self, code: str) -> SafetyCheckResult:
        """
        Check generated code for safety issues.
        
        Args:
            code: Generated code to check
            
        Returns:
            SafetyCheckResult with issues found
        """
        checks_run = []
        issues_found = []
        severity_levels = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        
        # Check 1: Syntax validation
        checks_run.append("syntax_validation")
        syntax_issues = self._check_syntax(code)
        if syntax_issues:
            issues_found.extend(syntax_issues)
            severity_levels["critical"] += len(syntax_issues)
        
        # Check 2: Dangerous patterns
        checks_run.append("dangerous_patterns")
        dangerous = self._check_dangerous_patterns(code)
        if dangerous:
            issues_found.extend(dangerous)
            severity_levels["high"] += len(dangerous)
        
        # Check 3: Hardcoded secrets
        checks_run.append("hardcoded_secrets")
        secrets = self._check_hardcoded_secrets(code)
        if secrets:
            issues_found.extend(secrets)
            severity_levels["critical"] += len(secrets)
        
        # Check 4: SQL injection
        checks_run.append("sql_injection")
        sql_issues = self._check_sql_injection(code)
        if sql_issues:
            issues_found.extend(sql_issues)
            severity_levels["high"] += len(sql_issues)
        
        # Check 5: Type hints
        checks_run.append("type_hints")
        type_issues = self._check_type_hints(code)
        if type_issues:
            issues_found.extend(type_issues)
            severity_levels["low"] += len(type_issues)
        
        passed = severity_levels["critical"] == 0 and severity_levels["high"] == 0
        recommendations = self._generate_recommendations(issues_found)
        
        logger.info(
            f"Safety check complete: {len(issues_found)} issues, "
            f"critical={severity_levels['critical']}, high={severity_levels['high']}"
        )
        
        return SafetyCheckResult(
            passed=passed,
            checks_run=checks_run,
            issues_found=issues_found,
            severity_levels=severity_levels,
            recommendations=recommendations,
        )
    
    def _check_syntax(self, code: str) -> List[Dict[str, Any]]:
        """Check Python syntax."""
        issues = []
        try:
            compile(code, '<string>', 'exec')
        except SyntaxError as e:
            issues.append({
                "type": "syntax_error",
                "severity": "critical",
                "message": f"Syntax error: {e.msg}",
                "line": e.lineno,
            })
        return issues
    
    def _check_dangerous_patterns(self, code: str) -> List[Dict[str, Any]]:
        """Check for dangerous patterns."""
        import re
        issues = []
        
        for pattern in self.dangerous_patterns:
            if re.search(pattern, code):
                issues.append({
                    "type": "dangerous_pattern",
                    "severity": "high",
                    "message": f"Dangerous pattern found: {pattern}",
                    "pattern": pattern,
                })
        
        return issues
    
    def _check_hardcoded_secrets(self, code: str) -> List[Dict[str, Any]]:
        """Check for hardcoded secrets."""
        import re
        issues = []
        
        for pattern in self.secret_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append({
                    "type": "hardcoded_secret",
                    "severity": "critical",
                    "message": f"Potential hardcoded secret: {pattern}",
                    "pattern": pattern,
                })
        
        return issues
    
    def _check_sql_injection(self, code: str) -> List[Dict[str, Any]]:
        """Check for SQL injection vulnerabilities."""
        issues = []
        
        # Check for string concatenation in SQL
        if "SELECT" in code or "INSERT" in code or "UPDATE" in code:
            if "+" in code and ("SELECT" in code or "INSERT" in code):
                issues.append({
                    "type": "sql_injection_risk",
                    "severity": "high",
                    "message": "Potential SQL injection: string concatenation detected",
                })
        
        return issues
    
    def _check_type_hints(self, code: str) -> List[Dict[str, Any]]:
        """Check for missing type hints."""
        issues = []
        
        # Simple check: count functions without type hints
        import re
        functions = re.findall(r'def\s+\w+\([^)]*\):', code)
        functions_with_hints = re.findall(r'def\s+\w+\([^)]*\)\s*->', code)
        
        if functions and len(functions_with_hints) < len(functions) / 2:
            issues.append({
                "type": "missing_type_hints",
                "severity": "low",
                "message": f"Missing type hints in {len(functions) - len(functions_with_hints)} functions",
            })
        
        return issues
    
    def _generate_recommendations(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on issues."""
        recommendations = []
        
        for issue in issues:
            if issue["type"] == "hardcoded_secret":
                recommendations.append("Use environment variables or secrets manager for sensitive data")
            elif issue["type"] == "dangerous_pattern":
                recommendations.append("Use safer alternatives (e.g., subprocess.run with list args)")
            elif issue["type"] == "sql_injection_risk":
                recommendations.append("Use parameterized queries or ORM")
            elif issue["type"] == "missing_type_hints":
                recommendations.append("Add type hints to all function parameters and return values")
        
        return list(set(recommendations))


class CostTracker:
    """
    Tracks AI API costs and token usage.
    
    Records:
    - Token usage per task
    - Cost per model
    - Total spend
    - Cost trends
    """
    
    def __init__(self, log_file: str = "ai_costs.json"):
        """Initialize cost tracker."""
        self.log_file = log_file
        self.records: List[CostRecord] = self._load_records()
        self.total_cost = sum(r.cost_usd for r in self.records)
    
    def _load_records(self) -> List[CostRecord]:
        """Load cost records from file."""
        if Path(self.log_file).exists():
            with open(self.log_file, 'r') as f:
                data = json.load(f)
                return [
                    CostRecord(
                        timestamp=datetime.fromisoformat(r['timestamp']),
                        task_type=r['task_type'],
                        model=r['model'],
                        input_tokens=r['input_tokens'],
                        output_tokens=r['output_tokens'],
                        cost_usd=r['cost_usd'],
                        duration_ms=r['duration_ms'],
                    )
                    for r in data
                ]
        return []
    
    def record_cost(
        self,
        task_type: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float,
        duration_ms: float,
    ):
        """Record a cost entry."""
        record = CostRecord(
            timestamp=datetime.now(),
            task_type=task_type,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
            duration_ms=duration_ms,
        )
        
        self.records.append(record)
        self.total_cost += cost_usd
        
        # Save to file
        self._save_records()
        
        logger.info(f"Recorded cost: ${cost_usd:.4f} for {task_type} using {model}")
    
    def _save_records(self):
        """Save cost records to file."""
        data = [
            {
                'timestamp': r.timestamp.isoformat(),
                'task_type': r.task_type,
                'model': r.model,
                'input_tokens': r.input_tokens,
                'output_tokens': r.output_tokens,
                'cost_usd': r.cost_usd,
                'duration_ms': r.duration_ms,
            }
            for r in self.records
        ]
        
        with open(self.log_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get cost summary."""
        if not self.records:
            return {
                "total_cost": 0.0,
                "total_tokens": 0,
                "by_model": {},
                "by_task": {},
            }
        
        by_model = {}
        by_task = {}
        total_tokens = 0
        
        for record in self.records:
            # By model
            if record.model not in by_model:
                by_model[record.model] = {"cost": 0.0, "tokens": 0}
            by_model[record.model]["cost"] += record.cost_usd
            by_model[record.model]["tokens"] += record.input_tokens + record.output_tokens
            
            # By task
            if record.task_type not in by_task:
                by_task[record.task_type] = {"cost": 0.0, "count": 0}
            by_task[record.task_type]["cost"] += record.cost_usd
            by_task[record.task_type]["count"] += 1
            
            total_tokens += record.input_tokens + record.output_tokens
        
        return {
            "total_cost": self.total_cost,
            "total_tokens": total_tokens,
            "by_model": by_model,
            "by_task": by_task,
            "record_count": len(self.records),
        }


class AuditLogger:
    """
    Logs all AI decisions for compliance and debugging.
    
    Records:
    - Prompts and responses
    - Model and version used
    - Safety checks
    - Cost
    """
    
    def __init__(self, log_file: str = "ai_audit.json"):
        """Initialize audit logger."""
        self.log_file = log_file
        self.entries: List[AuditLogEntry] = self._load_entries()
    
    def _load_entries(self) -> List[AuditLogEntry]:
        """Load audit entries from file."""
        if Path(self.log_file).exists():
            with open(self.log_file, 'r') as f:
                data = json.load(f)
                return [
                    AuditLogEntry(
                        timestamp=datetime.fromisoformat(e['timestamp']),
                        task_type=e['task_type'],
                        model=e['model'],
                        prompt_hash=e['prompt_hash'],
                        response_hash=e['response_hash'],
                        cost_usd=e['cost_usd'],
                        safety_passed=e['safety_passed'],
                        issues_found=e['issues_found'],
                    )
                    for e in data
                ]
        return []
    
    def log_entry(
        self,
        task_type: str,
        model: str,
        prompt: str,
        response: str,
        cost_usd: float,
        safety_passed: bool,
        issues_found: List[str],
    ):
        """Log an AI decision."""
        import hashlib
        
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:16]
        response_hash = hashlib.sha256(response.encode()).hexdigest()[:16]
        
        entry = AuditLogEntry(
            timestamp=datetime.now(),
            task_type=task_type,
            model=model,
            prompt_hash=prompt_hash,
            response_hash=response_hash,
            cost_usd=cost_usd,
            safety_passed=safety_passed,
            issues_found=issues_found,
        )
        
        self.entries.append(entry)
        self._save_entries()
        
        logger.info(f"Audit logged: {task_type} using {model}")
    
    def _save_entries(self):
        """Save audit entries to file."""
        data = [
            {
                'timestamp': e.timestamp.isoformat(),
                'task_type': e.task_type,
                'model': e.model,
                'prompt_hash': e.prompt_hash,
                'response_hash': e.response_hash,
                'cost_usd': e.cost_usd,
                'safety_passed': e.safety_passed,
                'issues_found': e.issues_found,
            }
            for e in self.entries
        ]
        
        with open(self.log_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_audit_report(self, task_type: Optional[str] = None) -> Dict[str, Any]:
        """Get audit report."""
        entries = self.entries
        if task_type:
            entries = [e for e in entries if e.task_type == task_type]
        
        return {
            "total_entries": len(entries),
            "safety_passed": sum(1 for e in entries if e.safety_passed),
            "safety_failed": sum(1 for e in entries if not e.safety_passed),
            "total_cost": sum(e.cost_usd for e in entries),
            "by_model": self._group_by_model(entries),
        }
    
    def _group_by_model(self, entries: List[AuditLogEntry]) -> Dict[str, int]:
        """Group entries by model."""
        by_model = {}
        for entry in entries:
            by_model[entry.model] = by_model.get(entry.model, 0) + 1
        return by_model
