"""
tools/base.py — Tool ABC (Command Pattern).

Each tool is a stateless callable object with a stable name, a description
shown to the LLM, and an execute() method that does one concrete thing.

Layer 2 — imports nothing from the agent package.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Tool(ABC):
    """
    Abstract base for all agent tools.

    Subclasses MUST be stateless — all state lives in execute() locals.
    Tools MUST NOT import from agents/ or orchestration/.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Stable key used by the LLM and ToolRegistry lookup."""

    @property
    @abstractmethod
    def description(self) -> str:
        """One-sentence description shown to the LLM."""

    @property
    @abstractmethod
    def param_schema(self) -> dict[str, str]:
        """
        Dict of param_name → description for prompt inclusion.
        Not full JSON Schema — simple enough for any LLM to parse.
        """

    @abstractmethod
    def execute(self, **kwargs: Any) -> str:
        """
        Run the tool and return a plain-text observation string.
        Must never raise — catch internally and return an error string.
        """
