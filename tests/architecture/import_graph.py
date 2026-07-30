"""Static import-graph analysis for project layering guardrails."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROJECT_APPS = frozenset({
    'analytics',
    'chat',
    'common',
    'crm',
    'help',
    'massmail',
    'quality',
    'settings',
    'sharedkernel',
    'tasks',
    'voip',
    'webcrm',
})

LAYERING_VIOLATION_APPS = PROJECT_APPS - {'sharedkernel'}


@dataclass(frozen=True, slots=True)
class ImportEdge:
    importing_file: str
    imported_module: str
    source_app: str
    target_app: str

    def as_key(self) -> tuple[str, str]:
        return (self.importing_file, self.imported_module)


def app_for_path(path: Path) -> str | None:
    relative = path.relative_to(PROJECT_ROOT)
    if not relative.parts:
        return None
    root = relative.parts[0]
    if root == 'tests':
        return None
    if root in PROJECT_APPS:
        return root
    return None


def module_roots_from_node(node: ast.AST) -> list[str]:
    if isinstance(node, ast.Import):
        return [alias.name for alias in node.names]
    if isinstance(node, ast.ImportFrom):
        if node.module:
            return [node.module]
        return []
    return []


def target_app_for_module(module_name: str) -> str | None:
    root = module_name.split('.')[0]
    if root in PROJECT_APPS:
        return root
    return None


def parse_import_edges(path: Path, *, source_app: str | None = None) -> list[ImportEdge]:
    resolved_source_app = source_app or app_for_path(path)
    if resolved_source_app is None or resolved_source_app == 'sharedkernel':
        return []

    tree = ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    try:
        relative_file = path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        relative_file = path.as_posix()
    edges: list[ImportEdge] = []
    for node in ast.walk(tree):
        for module_name in module_roots_from_node(node):
            target_app = target_app_for_module(module_name)
            if target_app is None or target_app == resolved_source_app:
                continue
            if target_app == 'sharedkernel':
                continue
            edges.append(
                ImportEdge(
                    importing_file=relative_file,
                    imported_module=module_name,
                    source_app=resolved_source_app,
                    target_app=target_app,
                ),
            )
    return edges


def build_layering_violations(app_roots: list[Path] | None = None) -> list[ImportEdge]:
    roots = app_roots or [PROJECT_ROOT / app for app in sorted(LAYERING_VIOLATION_APPS)]
    violations: list[ImportEdge] = []
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob('*.py')):
            if path.name == '__pycache__':
                continue
            violations.extend(parse_import_edges(path))
    return sorted(violations, key=lambda edge: edge.as_key())


def helpers_fan_in(app_roots: list[Path] | None = None) -> list[str]:
    roots = app_roots or [PROJECT_ROOT / app for app in sorted(LAYERING_VIOLATION_APPS)]
    importers: list[str] = []
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob('*.py')):
            if path.name == '__pycache__':
                continue
            tree = ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
            for node in ast.walk(tree):
                for module_name in module_roots_from_node(node):
                    if module_name == 'common.utils.helpers' or module_name.startswith(
                        'common.utils.helpers.',
                    ):
                        importers.append(path.relative_to(PROJECT_ROOT).as_posix())
                        break
    tests_root = PROJECT_ROOT / 'tests'
    if tests_root.exists():
        for path in sorted(tests_root.rglob('*.py')):
            tree = ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
            for node in ast.walk(tree):
                for module_name in module_roots_from_node(node):
                    if module_name == 'common.utils.helpers' or module_name.startswith(
                        'common.utils.helpers.',
                    ):
                        importers.append(path.relative_to(PROJECT_ROOT).as_posix())
                        break
    return sorted(set(importers))
