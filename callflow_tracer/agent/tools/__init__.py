"""
tools — Layer 2: stateless Tool implementations + ToolRegistry.

Public surface (everything agents need to import):
  Tool             ← base.py (Command ABC)
  ToolRegistry     ← registry.py
  GrepCodebaseTool, ListFilesTool, ReadFileTool  ← search.py
  RunContextTool, RunWhyTool, RunAgentTraceTool  ← callflow.py
  TOOL_CATALOG     ← dict[name → Tool] for extra-tool lookup by RouterAgent
"""

from .base import Tool
from .callflow import RunAgentTraceTool, RunContextTool, RunWhyTool
from .registry import ToolRegistry
from .search import GrepCodebaseTool, ListFilesTool, ReadFileTool

# Singleton instances — tools are stateless so one per type is sufficient.
# RouterAgent uses this catalogue when assigning individual extra_tools to agents.
TOOL_CATALOG: dict[str, Tool] = {
    "grep_codebase":  GrepCodebaseTool(),
    "list_files":     ListFilesTool(),
    "read_file":      ReadFileTool(),
    "run_context":    RunContextTool(),
    "run_why":        RunWhyTool(),
    "run_agent_trace": RunAgentTraceTool(),
}

__all__ = [
    "Tool",
    "ToolRegistry",
    "TOOL_CATALOG",
    "GrepCodebaseTool",
    "ListFilesTool",
    "ReadFileTool",
    "RunContextTool",
    "RunWhyTool",
    "RunAgentTraceTool",
]
