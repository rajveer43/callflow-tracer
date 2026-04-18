"""
tools/registry.py — ToolRegistry (dict-backed, O(1) lookup).

Layer 2 — imports only from tools/base.py (same layer).

DSA:
  dict[str, Tool] : O(1) dispatch by name
"""

from __future__ import annotations

from typing import Any

from .base import Tool


class ToolRegistry:
    """
    Holds a dict[name → Tool]. Every agent gets its own ToolRegistry
    instance containing only the tools that agent is allowed to use.
    """

    def __init__(self, tools: list[Tool]) -> None:
        self._tools: dict[str, Tool] = {t.name: t for t in tools}

    def execute(self, name: str, params: dict[str, Any]) -> str:
        """Execute a tool by name. Returns error string if name unknown."""
        tool = self._tools.get(name)
        if tool is None:
            known = ", ".join(self._tools)
            return f"Unknown tool '{name}'. Available: {known}"
        try:
            return tool.execute(**params)
        except TypeError as exc:
            return f"Tool '{name}' got wrong params: {exc}"

    def descriptions(self) -> str:
        """Build a formatted tool list for inclusion in the system prompt."""
        lines = []
        for tool in self._tools.values():
            params = ", ".join(f"{k}: {v}" for k, v in tool.param_schema.items())
            lines.append(f'  "{tool.name}" — {tool.description}\n    Params: {{{params}}}')
        return "\n".join(lines)

    def names(self) -> list[str]:
        return list(self._tools.keys())

    @property
    def tools(self) -> list[Tool]:
        """Expose the tool list so BaseAgent can merge skill-contributed tools."""
        return list(self._tools.values())
