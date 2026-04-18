"""
agent/skills/bundled.py — Pre-built bundled skills.

These are compositions of existing tools with focused prompt fragments.
RouterAgent can assign any of these by name to any dispatched agent.

Four bundled skills:
  StaticAnalysis   — static code search and file reading
  DependencyTrace  — dynamic execution tracing + call chain analysis
  CostProfiling    — LLM cost/token/timeline analysis
  SecurityScan     — security-focused grep + file inspection
"""

from __future__ import annotations

from ..tools.callflow import RunAgentTraceTool, RunContextTool, RunWhyTool
from ..tools.search import GrepCodebaseTool, ListFilesTool, ReadFileTool
from .base import Skill, SkillRegistry, SkillTier

# ── Skill definitions ──────────────────────────────────────────────────────────

STATIC_ANALYSIS = Skill(
    name="StaticAnalysis",
    tools=(GrepCodebaseTool(), ListFilesTool(), ReadFileTool()),
    description="Search and read code statically — grep patterns, list files, read source",
    prompt_fragment=(
        "You have static analysis capabilities. Use grep_codebase to search for "
        "patterns, list_files to discover relevant files, and read_file to inspect "
        "source code. Focus on structure, imports, class hierarchies, and usage patterns."
    ),
    tier=SkillTier.BUNDLED,
)

DEPENDENCY_TRACE = Skill(
    name="DependencyTrace",
    tools=(RunContextTool(), RunWhyTool()),
    description="Trace execution dynamically — profile hot functions, trace call chains",
    prompt_fragment=(
        "You have dynamic tracing capabilities. Use run_context to execute a script "
        "and profile the most-called functions by time and frequency. Use run_why to "
        "trace every call chain leading to a specific function. Prioritize functions "
        "with high call counts or total time."
    ),
    tier=SkillTier.BUNDLED,
)

COST_PROFILING = Skill(
    name="CostProfiling",
    tools=(RunAgentTraceTool(), GrepCodebaseTool()),
    description="Measure LLM API costs and token usage in agent scripts",
    prompt_fragment=(
        "You have LLM cost profiling capabilities. Use run_agent_trace to execute a "
        "script and measure LLM API calls, token consumption, and estimated USD cost. "
        "Use grep_codebase to locate API call sites and model configurations in source. "
        "Report cost per call type, total tokens, and the most expensive operations."
    ),
    tier=SkillTier.BUNDLED,
)

SECURITY_SCAN = Skill(
    name="SecurityScan",
    tools=(GrepCodebaseTool(), ReadFileTool()),
    description="Scan for OWASP Top 10 vulnerabilities, hardcoded secrets, and dangerous patterns",
    prompt_fragment=(
        "You have security scanning capabilities. Search for OWASP Top 10 risks: "
        "SQL injection (string concatenation in queries), hardcoded credentials "
        "(API keys, passwords, tokens), dangerous eval/exec calls, path traversal "
        "(user input in file paths), insecure deserialization (pickle.loads on untrusted "
        "data), and missing input validation at entry points. Report file, line, and "
        "severity for each finding."
    ),
    tier=SkillTier.BUNDLED,
)

# ── Registry factory ───────────────────────────────────────────────────────────

BUNDLED_SKILLS: list[Skill] = [
    STATIC_ANALYSIS,
    DEPENDENCY_TRACE,
    COST_PROFILING,
    SECURITY_SCAN,
]


def build_bundled_registry() -> SkillRegistry:
    """Return a SkillRegistry pre-loaded with all bundled skills."""
    return SkillRegistry(BUNDLED_SKILLS)
