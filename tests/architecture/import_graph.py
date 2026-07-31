"""Static import-graph analysis for project layering guardrails."""

from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ALLOWED_EXCEPTIONS_FILE = Path(__file__).resolve().parent / 'allowed_exceptions_data.json'

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

SHARED_MODULE_PREFIXES = (
    'sharedkernel.',
    'common.queries',
    'common.services.',
)

HELPERS_SHIM_MODULE = 'common.utils.helpers'
HELPERS_RELOCATED_SYMBOLS = frozenset({
    'add_chat_context',
    'add_phone_q_params',
    'annotate_chat',
    'get_active_users',
    'get_department_id',
    'get_manager_departments',
    'CONTENT_COPY_ICON',
    'CONTENT_COPY_LINK',
    'COPY_STR',
    'CRM_NOTICE',
    'FRIDAY_SATURDAY_SUNDAY_MSG',
    'LEADERS',
    'OBJ_DOESNT_EXIT_STR',
    'ONCLICK_STR',
    'SAFE_ATTACH_FILE_ICON',
    'SAFE_SUBJECT_ICON',
    'get_formatted_short_date',
    'get_verbose_name',
    'popup_window',
    'compose_message',
    'compose_subject',
    'get_delta_date',
    'get_now',
    'get_today',
    'notify_admins_no_email',
    'save_message',
    'send_crm_email',
    'set_toggle_tooltip',
    'get_trans_for_lang',
    'get_trans_for_user',
    'get_user_language_code',
})

SHARED_MODULE_FAN_IN_CEILING = 60


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


def relocated_helpers_symbol_importers(app_roots: list[Path] | None = None) -> list[tuple[str, str]]:
    """Return direct imports of relocated symbols from the helpers shim."""
    roots = app_roots or [PROJECT_ROOT / app for app in sorted(LAYERING_VIOLATION_APPS)]
    search_roots = list(roots) + [PROJECT_ROOT / 'tests']
    importers: list[tuple[str, str]] = []
    for root in search_roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob('*.py')):
            if path.name == '__pycache__':
                continue
            tree = ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
            relative_file = path.relative_to(PROJECT_ROOT).as_posix()
            for node in ast.walk(tree):
                if not isinstance(node, ast.ImportFrom) or node.module != HELPERS_SHIM_MODULE:
                    continue
                for alias in node.names:
                    if alias.name in HELPERS_RELOCATED_SYMBOLS:
                        importers.append((relative_file, alias.name))
    return sorted(set(importers))


def shared_module_key(module_name: str) -> str | None:
    if module_name.startswith('sharedkernel.'):
        parts = module_name.split('.')
        return '.'.join(parts[:2]) if len(parts) >= 2 else module_name
    if module_name == 'common.queries' or module_name.startswith('common.queries.'):
        return 'common.queries'
    if module_name.startswith('common.services.'):
        parts = module_name.split('.')
        return '.'.join(parts[:3]) if len(parts) >= 3 else module_name
    return None


def shared_module_fan_in(app_roots: list[Path] | None = None) -> dict[str, list[str]]:
    roots = app_roots or [PROJECT_ROOT / app for app in sorted(LAYERING_VIOLATION_APPS)]
    search_roots = list(roots) + [PROJECT_ROOT / 'tests']
    fan_in: dict[str, set[str]] = {}
    for root in search_roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob('*.py')):
            if path.name == '__pycache__':
                continue
            tree = ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
            relative_file = path.relative_to(PROJECT_ROOT).as_posix()
            for node in ast.walk(tree):
                for module_name in module_roots_from_node(node):
                    module_key = shared_module_key(module_name)
                    if module_key is None:
                        continue
                    fan_in.setdefault(module_key, set()).add(relative_file)
    return {
        module: sorted(importers)
        for module, importers in sorted(fan_in.items())
    }


def load_allowed_exceptions():
    from tests.architecture.allowed_exceptions import AllowedException

    payload = json.loads(ALLOWED_EXCEPTIONS_FILE.read_text(encoding='utf-8'))
    return [
        AllowedException(
            importing_file=entry['importing_file'],
            imported_module=entry['imported_module'],
            reason=entry['reason'],
            owner=entry['owner'],
        )
        for entry in payload
    ]
