"""AST-based scan for secret-shaped literal assignments in settings modules."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path

SECRET_NAME_PATTERN = re.compile(
    r'(key|secret|password|token|passwd|credential)',
    re.IGNORECASE,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

SETTINGS_SCAN_TARGETS = [
    REPO_ROOT / 'webcrm/settings.py',
    REPO_ROOT / 'webcrm/config.py',
    REPO_ROOT / 'webcrm/datetime_settings.py',
    REPO_ROOT / 'crm/settings.py',
    REPO_ROOT / 'common/settings.py',
    REPO_ROOT / 'tasks/settings.py',
    REPO_ROOT / 'voip/settings.py',
]

ENV_EXAMPLE_PATH = REPO_ROOT / '.env.example'

# file path (repo-relative) -> variable name -> justification
ALLOWLIST: dict[str, dict[str, str]] = {
    'webcrm/config.py': {
        'SECRET_MASK': 'Public mask token displayed in diagnostics; not a credential.',
    },
    'webcrm/settings.py': {
        'token_command': 'OAuth2 URL path fragment, not a credential.',
    },
    'webcrm/voip_config.py': {
        'BACKEND': 'Dotted Python import path for the VoIP backend class.',
        'PROVIDER': 'Public provider label used for routing, not a credential.',
    },
}

ENV_PLACEHOLDER_RE = re.compile(r'^<[^>]+>$')
ENV_NUMERIC_OR_BOOL_RE = re.compile(r'^(true|false|\d+)$', re.IGNORECASE)


@dataclass(frozen=True)
class SecretLiteralFinding:
    path: str
    lineno: int
    name: str
    reason: str


def _relative_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _is_secret_shaped(name: str) -> bool:
    return bool(SECRET_NAME_PATTERN.search(name))


def _literal_value(node: ast.AST) -> object | None:
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.JoinedStr):
        return '<f-string>'
    return None


def _is_non_empty_literal(node: ast.AST) -> bool:
    value = _literal_value(node)
    if value is None:
        return False
    if value == '' or value == '<f-string>':
        return value == '<f-string>'
    if isinstance(value, (str, int, bytes)):
        return True
    return False


def _allowlisted(path: Path, name: str) -> bool:
    rel = _relative_path(path)
    return name in ALLOWLIST.get(rel, {})


def _check_binding(
    path: Path,
    name: str,
    value_node: ast.AST,
    lineno: int,
    findings: list[SecretLiteralFinding],
) -> None:
    if not _is_secret_shaped(name):
        return
    if _allowlisted(path, name):
        return
    if not _is_non_empty_literal(value_node):
        return
    findings.append(
        SecretLiteralFinding(
            path=_relative_path(path),
            lineno=lineno,
            name=name,
            reason='Secret-shaped name assigned a non-empty literal value',
        )
    )


def _walk_dict_literals(
    path: Path,
    node: ast.Dict,
    lineno: int,
    findings: list[SecretLiteralFinding],
) -> None:
    for key, value in zip(node.keys, node.values):
        if key is None or value is None:
            continue
        if isinstance(key, ast.Constant) and isinstance(key.value, str):
            _check_binding(path, key.value, value, lineno, findings)
        _walk_container_literals(path, value, lineno, findings)


def _walk_container_literals(
    path: Path,
    node: ast.AST,
    lineno: int,
    findings: list[SecretLiteralFinding],
) -> None:
    if isinstance(node, ast.Dict):
        _walk_dict_literals(path, node, lineno, findings)
    elif isinstance(node, ast.List):
        for element in node.elts:
            _walk_container_literals(path, element, lineno, findings)


class _SecretLiteralVisitor(ast.NodeVisitor):
    def __init__(self, path: Path) -> None:
        self.path = path
        self.findings: list[SecretLiteralFinding] = []

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            self._visit_target(target, node.value, node.lineno)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if node.value is not None and node.target is not None:
            self._visit_target(node.target, node.value, node.lineno)
        self.generic_visit(node)

    def _visit_target(self, target: ast.AST, value: ast.AST, lineno: int) -> None:
        if isinstance(target, ast.Name):
            _check_binding(self.path, target.id, value, lineno, self.findings)
        elif isinstance(target, (ast.Tuple, ast.List)):
            for element in target.elts:
                self._visit_target(element, value, lineno)
        if isinstance(value, ast.Dict):
            _walk_container_literals(self.path, value, lineno, self.findings)
        elif isinstance(value, ast.List):
            _walk_container_literals(self.path, value, lineno, self.findings)


def scan_python_file(path: Path) -> list[SecretLiteralFinding]:
    source = path.read_text(encoding='utf-8')
    tree = ast.parse(source, filename=str(path))
    visitor = _SecretLiteralVisitor(path)
    visitor.visit(tree)
    return visitor.findings


def scan_env_example(path: Path = ENV_EXAMPLE_PATH) -> list[SecretLiteralFinding]:
    findings: list[SecretLiteralFinding] = []
    for index, line in enumerate(path.read_text(encoding='utf-8').splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith('#') or '=' not in stripped:
            continue
        key, _, raw_value = stripped.partition('=')
        name = key.strip()
        value = raw_value.strip()
        if not _is_secret_shaped(name):
            continue
        if ENV_PLACEHOLDER_RE.match(value):
            continue
        if ENV_NUMERIC_OR_BOOL_RE.match(value):
            continue
        if value == '':
            continue
        findings.append(
            SecretLiteralFinding(
                path=_relative_path(path),
                lineno=index,
                name=name,
                reason='Secret-shaped env example value is not an angle-bracket placeholder',
            )
        )
    return findings


def scan_repository(
    *,
    extra_python_files: list[Path] | None = None,
    include_env_example: bool = True,
) -> list[SecretLiteralFinding]:
    findings: list[SecretLiteralFinding] = []
    targets = list(SETTINGS_SCAN_TARGETS)
    if extra_python_files:
        targets.extend(extra_python_files)
    for path in targets:
        findings.extend(scan_python_file(path))
    if include_env_example and ENV_EXAMPLE_PATH.is_file():
        findings.extend(scan_env_example(ENV_EXAMPLE_PATH))
    return findings
