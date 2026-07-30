"""Layering contract tests for the sharedkernel app."""

from __future__ import annotations

import ast
import importlib
import pkgutil
from pathlib import Path

from django.test import SimpleTestCase

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SHAREDKERNEL_ROOT = PROJECT_ROOT / 'sharedkernel'

FORBIDDEN_PROJECT_APPS = frozenset({
    'analytics',
    'chat',
    'common',
    'crm',
    'help',
    'massmail',
    'quality',
    'settings',
    'tasks',
    'voip',
})


def iter_sharedkernel_python_files():
    for path in sorted(SHAREDKERNEL_ROOT.rglob('*.py')):
        if path.name == '__pycache__':
            continue
        yield path


def find_forbidden_imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split('.')[0]
                if root in FORBIDDEN_PROJECT_APPS:
                    violations.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root = node.module.split('.')[0]
                if root in FORBIDDEN_PROJECT_APPS:
                    violations.append(node.module)
    return violations


class SharedKernelLayeringTests(SimpleTestCase):
    def test_sharedkernel_has_no_inbound_project_app_imports(self):
        for path in iter_sharedkernel_python_files():
            violations = find_forbidden_imports(path)
            self.assertEqual(
                violations,
                [],
                msg=f'{path.relative_to(PROJECT_ROOT)} imports forbidden apps: {violations}',
            )

    def test_sharedkernel_submodules_import_cleanly(self):
        import sharedkernel

        module_names = [
            sharedkernel.__name__,
            *(f'sharedkernel.{name}' for _, name, _ in pkgutil.iter_modules(sharedkernel.__path__)),
        ]
        for module_name in sorted(set(module_names)):
            with self.subTest(module=module_name):
                importlib.import_module(module_name)
