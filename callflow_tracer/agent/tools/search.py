"""
tools/search.py — Static search tools (grep, list files, read file).

Layer 2 — imports only from tools/base.py (same layer).

DSA:
  set[str]  : O(1) extension filter
  os.walk   : O(files) — bounded by scope/max_files
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from .base import Tool

_PY_EXTENSIONS: frozenset[str] = frozenset({".py", ".pyi"})
_MAX_GREP_FILES = 200
_MAX_FILE_LINES = 300


class GrepCodebaseTool(Tool):
    """Search Python files for a pattern using Python re (no subprocess)."""

    @property
    def name(self) -> str:
        return "grep_codebase"

    @property
    def description(self) -> str:
        return "Search all Python files for a regex pattern and return matching lines"

    @property
    def param_schema(self) -> dict[str, str]:
        return {
            "pattern": "regex or literal string to search",
            "directory": "directory to search (default: '.')",
            "max_results": "max matching lines to return (default: 20)",
        }

    def execute(
        self,
        pattern: str = "",
        directory: str = ".",
        max_results: int = 20,
    ) -> str:
        if not pattern:
            return "Error: pattern is required"

        try:
            regex = re.compile(pattern, re.IGNORECASE)
        except re.error as exc:
            return f"Invalid regex '{pattern}': {exc}"

        results: list[str] = []
        files_searched = 0

        for root, _dirs, files in os.walk(directory):
            _dirs[:] = [d for d in _dirs if not d.startswith((".", "__pycache__", "venv", "env", ".venv", "node_modules"))]
            for fname in files:
                if Path(fname).suffix not in _PY_EXTENSIONS:
                    continue
                if files_searched >= _MAX_GREP_FILES:
                    break
                fpath = os.path.join(root, fname)
                files_searched += 1
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        for lineno, line in enumerate(f, 1):
                            if regex.search(line):
                                rel = os.path.relpath(fpath, directory)
                                results.append(f"{rel}:{lineno}: {line.rstrip()}")
                                if len(results) >= max_results:
                                    break
                except OSError:
                    continue
            if len(results) >= max_results:
                break

        if not results:
            return f"No matches found for '{pattern}' in {directory}"
        return f"Found {len(results)} match(es):\n" + "\n".join(results)


class ListFilesTool(Tool):
    """List Python files in a directory, optionally filtered by name pattern."""

    @property
    def name(self) -> str:
        return "list_files"

    @property
    def description(self) -> str:
        return "List Python files in a directory, with optional name filter"

    @property
    def param_schema(self) -> dict[str, str]:
        return {
            "directory": "directory to list (default: '.')",
            "filter": "optional substring filter on filename",
            "max_files": "max files to return (default: 30)",
        }

    def execute(
        self,
        directory: str = ".",
        filter: str = "",
        max_files: int = 30,
    ) -> str:
        files: list[str] = []
        for root, dirs, fnames in os.walk(directory):
            dirs[:] = [d for d in dirs if not d.startswith((".", "__pycache__", "venv", ".venv"))]
            for fname in fnames:
                if Path(fname).suffix not in _PY_EXTENSIONS:
                    continue
                if filter and filter.lower() not in fname.lower():
                    continue
                rel = os.path.relpath(os.path.join(root, fname), directory)
                files.append(rel)
                if len(files) >= max_files:
                    break
            if len(files) >= max_files:
                break

        if not files:
            return f"No Python files found in '{directory}'"
        return f"{len(files)} file(s):\n" + "\n".join(files)


class ReadFileTool(Tool):
    """Read a file, optionally with a line range."""

    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return "Read a source file, optionally between start_line and end_line"

    @property
    def param_schema(self) -> dict[str, str]:
        return {
            "path": "file path to read",
            "start_line": "first line to include (1-indexed, optional)",
            "end_line": "last line to include (inclusive, optional)",
        }

    def execute(
        self,
        path: str = "",
        start_line: int = 1,
        end_line: int = _MAX_FILE_LINES,
    ) -> str:
        if not path:
            return "Error: path is required"
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except OSError as exc:
            return f"Cannot read '{path}': {exc}"

        start = max(0, start_line - 1)
        end   = min(len(lines), end_line)
        snippet = lines[start:end]
        header = f"# {path} (lines {start+1}–{start+len(snippet)})\n"
        return header + "".join(snippet)
