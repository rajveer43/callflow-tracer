"""Static AST parser — extract function-level call edges from Python source.

Uses Python's stdlib `ast` module so there are no extra dependencies.
The resulting graph is a dict-of-dicts adjacency structure that can be
merged with the runtime CallGraph for a unified static+dynamic view.

DSA used:
  - Adjacency list (dict[str, set[str]]) for O(1) edge lookup
  - DFS via ast.NodeVisitor for the function-scope stack
"""

from __future__ import annotations

import ast
import os
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional, Set


@dataclass
class ASTNode:
    full_name: str        # module.ClassName.method_name
    module: str
    lineno: int
    col_offset: int
    is_method: bool = False
    class_name: Optional[str] = None


@dataclass
class StaticCallGraph:
    """Adjacency list: caller full_name → set of callee full_names."""

    nodes: Dict[str, ASTNode] = field(default_factory=dict)
    edges: Dict[str, Set[str]] = field(default_factory=lambda: defaultdict(set))

    def add_edge(self, caller: str, callee: str) -> None:
        self.edges[caller].add(callee)

    def to_dict(self) -> dict:
        return {
            "nodes": {k: {"full_name": v.full_name, "module": v.module, "lineno": v.lineno}
                      for k, v in self.nodes.items()},
            "edges": {k: sorted(v) for k, v in self.edges.items()},
        }


class _CallVisitor(ast.NodeVisitor):
    """Walks a single module's AST and records caller→callee pairs."""

    def __init__(self, module_name: str, graph: StaticCallGraph) -> None:
        self._module = module_name
        self._graph = graph
        # Stack tracks the current function scope: list of full_name strings
        self._scope_stack: list[str] = []
        self._class_stack: list[str] = []

    def _current_scope(self) -> Optional[str]:
        return self._scope_stack[-1] if self._scope_stack else None

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._class_stack.append(node.name)
        self.generic_visit(node)
        self._class_stack.pop()

    def _enter_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        cls = self._class_stack[-1] if self._class_stack else None
        if cls:
            full_name = f"{self._module}.{cls}.{node.name}"
        else:
            full_name = f"{self._module}.{node.name}"

        ast_node = ASTNode(
            full_name=full_name,
            module=self._module,
            lineno=node.lineno,
            col_offset=node.col_offset,
            is_method=bool(cls),
            class_name=cls,
        )
        self._graph.nodes[full_name] = ast_node
        self._scope_stack.append(full_name)
        self.generic_visit(node)
        self._scope_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._enter_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._enter_function(node)

    def visit_Call(self, node: ast.Call) -> None:
        caller = self._current_scope()
        if caller is None:
            self.generic_visit(node)
            return

        callee_name: Optional[str] = None
        if isinstance(node.func, ast.Name):
            callee_name = f"{self._module}.{node.func.id}"
        elif isinstance(node.func, ast.Attribute):
            callee_name = node.func.attr  # simplified; no full resolution

        if callee_name:
            self._graph.add_edge(caller, callee_name)
        self.generic_visit(node)


class ASTParser:
    """Parse one or more Python files / directories into a StaticCallGraph."""

    def __init__(self) -> None:
        self._graph = StaticCallGraph()

    def parse_file(self, path: str | Path, module_name: Optional[str] = None) -> None:
        path = Path(path)
        if module_name is None:
            module_name = path.stem
        try:
            source = path.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source, filename=str(path))
        except SyntaxError:
            return
        visitor = _CallVisitor(module_name, self._graph)
        visitor.visit(tree)

    def parse_directory(self, root: str | Path, package: str = "") -> None:
        root = Path(root)
        for py_file in sorted(root.rglob("*.py")):
            rel = py_file.relative_to(root)
            parts = list(rel.with_suffix("").parts)
            if package:
                parts = [package] + parts
            module_name = ".".join(parts).replace("__init__", "").strip(".")
            self.parse_file(py_file, module_name or py_file.stem)

    @property
    def graph(self) -> StaticCallGraph:
        return self._graph
