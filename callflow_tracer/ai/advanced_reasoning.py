"""
Advanced reasoning capabilities for AI analysis.

Provides:
- Self-critique and verification passes
- Chain-of-tools workflows
- Organization-aware prompts
- Multi-step reasoning chains
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import json

from .llm_provider import LLMProvider
from .prompts import PromptTemplates

logger = logging.getLogger(__name__)


@dataclass
class CritiqueResult:
    """Result from self-critique pass."""
    original_response: str
    critique: str
    issues_found: List[str]
    confidence_score: float  # 0-100
    is_safe: bool
    recommendations: List[str]


@dataclass
class WorkflowStep:
    """Single step in a workflow."""
    name: str
    task_type: str
    inputs: Dict[str, Any]
    output: Optional[str] = None
    status: str = "pending"  # pending, running, completed, failed


@dataclass
class WorkflowResult:
    """Result from workflow execution."""
    workflow_name: str
    steps: List[WorkflowStep]
    final_output: str
    total_cost: float
    total_time_ms: float
    success: bool


@dataclass
class OrgProfile:
    """Organization configuration for AI analysis."""
    name: str
    coding_guidelines: List[str]
    preferred_frameworks: List[str]
    performance_sla: Dict[str, float]  # e.g., {"p99_latency_ms": 100}
    security_policies: List[str]
    compliance_requirements: List[str]  # e.g., ["GDPR", "HIPAA"]
    team_expertise: List[str]  # e.g., ["Python", "Kubernetes"]


class SelfCritique:
    """
    Self-critique mechanism for LLM responses.
    
    Validates LLM outputs for:
    - Hallucinations
    - Missing metrics
    - Unsafe recommendations
    - Logical consistency
    """
    
    def __init__(self, provider: LLMProvider):
        """Initialize self-critique."""
        self.provider = provider
    
    def critique(
        self,
        original_response: str,
        task_type: str,
        context: str,
    ) -> CritiqueResult:
        """
        Critique an LLM response.
        
        Args:
            original_response: The original LLM response
            task_type: Type of task (e.g., 'code_fix')
            context: Original context/input
            
        Returns:
            CritiqueResult with issues and confidence score
        """
        critique_prompt = self._build_critique_prompt(
            original_response, task_type, context
        )
        
        # Get critique from LLM
        critique_response = self.provider.generate(
            critique_prompt,
            system=self._get_critique_system_prompt(task_type),
            temperature=0.3,  # Lower temperature for consistency
        )
        
        # Parse critique
        issues, confidence, is_safe, recommendations = self._parse_critique(
            critique_response, task_type
        )
        
        logger.info(
            f"Critique complete: {len(issues)} issues found, "
            f"confidence={confidence:.1f}%, safe={is_safe}"
        )
        
        return CritiqueResult(
            original_response=original_response,
            critique=critique_response,
            issues_found=issues,
            confidence_score=confidence,
            is_safe=is_safe,
            recommendations=recommendations,
        )
    
    def _build_critique_prompt(
        self, response: str, task_type: str, context: str
    ) -> str:
        """Build critique prompt."""
        return f"""Review this {task_type} response for issues:

ORIGINAL CONTEXT:
{context}

RESPONSE TO CRITIQUE:
{response}

CRITIQUE CHECKLIST:
1. Are all claims supported by evidence?
2. Are there any hallucinations or made-up metrics?
3. Are recommendations safe and implementable?
4. Is the logic consistent and sound?
5. Are there missing important considerations?
6. Would this response cause problems if implemented?

Provide:
- List of issues found (if any)
- Confidence score (0-100) in the original response
- Is this response safe to implement? (yes/no)
- Recommendations for improvement"""
    
    def _get_critique_system_prompt(self, task_type: str) -> str:
        """Get system prompt for critique."""
        return f"""You are an expert critic specializing in {task_type} analysis.
Your job is to identify issues, hallucinations, and unsafe recommendations.
Be thorough but fair. Focus on substantive issues, not minor wording."""
    
    def _parse_critique(
        self, critique_response: str, task_type: str
    ) -> Tuple[List[str], float, bool, List[str]]:
        """Parse critique response."""
        # Simple parsing (would be more sophisticated in production)
        issues = []
        confidence = 75.0
        is_safe = True
        recommendations = []
        
        lines = critique_response.split('\n')
        
        for line in lines:
            if 'issue' in line.lower():
                issues.append(line.strip())
            if 'confidence' in line.lower():
                try:
                    confidence = float(''.join(c for c in line if c.isdigit() or c == '.'))
                except:
                    pass
            if 'unsafe' in line.lower() or 'dangerous' in line.lower():
                is_safe = False
            if 'recommend' in line.lower():
                recommendations.append(line.strip())
        
        return issues, confidence, is_safe, recommendations


class ChainOfTools:
    """
    Chain-of-tools workflow execution.
    
    Pre-built workflows like:
    - Find bottlenecks → root cause → propose fix → generate tests
    """
    
    def __init__(self, provider: LLMProvider, tool_executor):
        """Initialize chain-of-tools."""
        self.provider = provider
        self.tool_executor = tool_executor
        self.workflows: Dict[str, List[Dict[str, Any]]] = self._define_workflows()
    
    def _define_workflows(self) -> Dict[str, List[Dict[str, Any]]]:
        """Define available workflows."""
        return {
            "analyze_and_fix_performance": [
                {
                    "name": "Identify Bottlenecks",
                    "task_type": "performance_analysis",
                    "tools": ["get_callgraph_summary"],
                },
                {
                    "name": "Root Cause Analysis",
                    "task_type": "root_cause_analysis",
                    "tools": ["get_function_metrics"],
                },
                {
                    "name": "Generate Fix",
                    "task_type": "code_fix",
                    "tools": ["get_function_metrics"],
                },
                {
                    "name": "Generate Tests",
                    "task_type": "test_generation",
                    "tools": [],
                },
            ],
            "security_analysis_and_fix": [
                {
                    "name": "Analyze Security",
                    "task_type": "security_analysis",
                    "tools": ["analyze_security"],
                },
                {
                    "name": "Generate Fix",
                    "task_type": "code_fix",
                    "tools": [],
                },
                {
                    "name": "Generate Tests",
                    "task_type": "test_generation",
                    "tools": [],
                },
            ],
            "refactor_and_test": [
                {
                    "name": "Suggest Refactoring",
                    "task_type": "refactoring",
                    "tools": [],
                },
                {
                    "name": "Generate Tests",
                    "task_type": "test_generation",
                    "tools": [],
                },
            ],
        }
    
    def execute(
        self,
        workflow_name: str,
        context: Dict[str, Any],
    ) -> WorkflowResult:
        """
        Execute a workflow.
        
        Args:
            workflow_name: Name of workflow to execute
            context: Input context for workflow
            
        Returns:
            WorkflowResult with all steps and final output
        """
        if workflow_name not in self.workflows:
            raise ValueError(f"Unknown workflow: {workflow_name}")
        
        workflow_def = self.workflows[workflow_name]
        steps: List[WorkflowStep] = []
        current_output = None
        total_cost = 0.0
        total_time_ms = 0.0
        
        logger.info(f"Executing workflow: {workflow_name}")
        
        for step_def in workflow_def:
            step = WorkflowStep(
                name=step_def["name"],
                task_type=step_def["task_type"],
                inputs=context,
            )
            
            try:
                # Execute tools if needed
                for tool_name in step_def.get("tools", []):
                    tool_output = self.tool_executor.execute_tool(
                        tool_name, **context
                    )
                    context[f"{tool_name}_output"] = tool_output
                
                # Execute task
                step.output = self._execute_task(
                    step.task_type, context, current_output
                )
                step.status = "completed"
                current_output = step.output
                
                logger.info(f"Step '{step.name}' completed")
                
            except Exception as e:
                step.status = "failed"
                logger.error(f"Step '{step.name}' failed: {e}")
            
            steps.append(step)
        
        return WorkflowResult(
            workflow_name=workflow_name,
            steps=steps,
            final_output=current_output or "",
            total_cost=total_cost,
            total_time_ms=total_time_ms,
            success=all(s.status == "completed" for s in steps),
        )
    
    def _execute_task(
        self, task_type: str, context: Dict[str, Any], previous_output: Optional[str]
    ) -> str:
        """Execute a single task."""
        # Get prompt for task
        prompt_kwargs = {
            "graph_summary": context.get("graph_summary", ""),
            "question": context.get("question", ""),
            "root_causes": context.get("root_causes", ""),
            "impact": context.get("impact", ""),
            "issue_type": context.get("issue_type", ""),
            "function_code": context.get("function_code", ""),
            "function_name": context.get("function_name", ""),
            "context": context.get("context", ""),
            "before_code": context.get("before_code", ""),
            "anomalies": context.get("anomalies", ""),
            "baseline": context.get("baseline", ""),
            "issues": context.get("issues", ""),
            "code_context": context.get("code_context", ""),
            "metrics": context.get("metrics", {}),
        }
        
        # Filter to only needed kwargs
        system_prompt, user_prompt = self._get_task_prompt(task_type, prompt_kwargs)
        
        # Add previous output if available
        if previous_output:
            user_prompt += f"\n\nPREVIOUS ANALYSIS:\n{previous_output}"
        
        # Generate response
        response = self.provider.generate(
            user_prompt,
            system=system_prompt,
            temperature=0.3,
        )
        
        return response
    
    def _get_task_prompt(
        self, task_type: str, kwargs: Dict[str, Any]
    ) -> Tuple[str, str]:
        """Get prompt for task type."""
        # Filter kwargs to only those needed
        if task_type == "performance_analysis":
            return PromptTemplates.query_performance_analysis(
                kwargs["graph_summary"], kwargs["question"]
            )
        elif task_type == "root_cause_analysis":
            return PromptTemplates.root_cause_analysis(
                kwargs["root_causes"], kwargs["impact"], kwargs["issue_type"]
            )
        elif task_type == "code_fix":
            return PromptTemplates.generate_code_fix(
                kwargs["issue_type"],
                kwargs["function_name"],
                kwargs["context"],
                kwargs.get("before_code"),
            )
        elif task_type == "security_analysis":
            return PromptTemplates.analyze_security_issues(
                kwargs["issues"], kwargs.get("code_context")
            )
        elif task_type == "refactoring":
            return PromptTemplates.suggest_refactoring(
                kwargs["function_code"], kwargs["metrics"]
            )
        elif task_type == "test_generation":
            return PromptTemplates.generate_tests(
                kwargs["function_code"], kwargs["function_name"]
            )
        else:
            return "You are a helpful AI assistant.", "Analyze the following: " + str(kwargs)


class OrgAwarePrompts:
    """
    Organization-aware prompt generation.
    
    Injects org profile into prompts for:
    - Coding guidelines
    - Preferred frameworks
    - Performance SLAs
    - Security policies
    - Compliance requirements
    """
    
    def __init__(self, org_profile: Optional[OrgProfile] = None):
        """Initialize org-aware prompts."""
        self.org_profile = org_profile or self._get_default_profile()
    
    def _get_default_profile(self) -> OrgProfile:
        """Get default org profile."""
        return OrgProfile(
            name="Default Organization",
            coding_guidelines=[
                "Follow PEP 8",
                "Use type hints",
                "Write docstrings",
            ],
            preferred_frameworks=["FastAPI", "SQLAlchemy", "pytest"],
            performance_sla={"p99_latency_ms": 100, "error_rate": 0.001},
            security_policies=[
                "No hardcoded secrets",
                "Input validation required",
                "Use parameterized queries",
            ],
            compliance_requirements=[],
            team_expertise=["Python", "SQL"],
        )
    
    def enhance_system_prompt(self, base_prompt: str) -> str:
        """
        Enhance system prompt with org context.
        
        Args:
            base_prompt: Base system prompt
            
        Returns:
            Enhanced prompt with org context
        """
        org_context = self._build_org_context()
        return f"{base_prompt}\n\n{org_context}"
    
    def enhance_user_prompt(self, base_prompt: str) -> str:
        """
        Enhance user prompt with org context.
        
        Args:
            base_prompt: Base user prompt
            
        Returns:
            Enhanced prompt with org context
        """
        org_context = self._build_org_context()
        return f"{base_prompt}\n\n{org_context}"
    
    def _build_org_context(self) -> str:
        """Build organization context string."""
        context = f"""
ORGANIZATION CONTEXT:
Organization: {self.org_profile.name}

CODING GUIDELINES:
{chr(10).join(f"- {g}" for g in self.org_profile.coding_guidelines)}

PREFERRED FRAMEWORKS:
{chr(10).join(f"- {f}" for f in self.org_profile.preferred_frameworks)}

PERFORMANCE SLAs:
{chr(10).join(f"- {k}: {v}" for k, v in self.org_profile.performance_sla.items())}

SECURITY POLICIES:
{chr(10).join(f"- {p}" for p in self.org_profile.security_policies)}

TEAM EXPERTISE:
{chr(10).join(f"- {e}" for e in self.org_profile.team_expertise)}
"""
        
        if self.org_profile.compliance_requirements:
            context += f"""
COMPLIANCE REQUIREMENTS:
{chr(10).join(f"- {c}" for c in self.org_profile.compliance_requirements)}
"""
        
        return context
    
    def set_org_profile(self, profile: OrgProfile):
        """Set organization profile."""
        self.org_profile = profile
        logger.info(f"Organization profile set: {profile.name}")
