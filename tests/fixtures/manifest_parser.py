"""Parse and compare dependency manifest files."""

from __future__ import annotations

import configparser
import re
from pathlib import Path

_REQUIREMENT_PATTERN = re.compile(
    r'^(?P<name>[A-Za-z0-9_.-]+(?:\[[^\]]+\])?)'
    r'(?P<specifier>\s*==[^\s;]+)?'
)


def parse_requirements_text(text: str) -> dict[str, str]:
    """Return a normalised package-name to specifier mapping."""
    requirements: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#'):
            continue
        match = _REQUIREMENT_PATTERN.match(line)
        if match is None:
            raise ValueError(f'Unparseable requirement line: {raw_line!r}')
        name = match.group('name').lower()
        specifier = (match.group('specifier') or '').strip()
        requirements[name] = specifier or 'unspecified'
    return requirements


def parse_requirements_file(path: Path) -> dict[str, str]:
    return parse_requirements_text(path.read_text(encoding='utf-8'))


def parse_setup_cfg_install_requires(path: Path) -> dict[str, str]:
    parser = configparser.ConfigParser()
    parser.read(path, encoding='utf-8')
    lines = parser['options']['install_requires'].splitlines()
    return parse_requirements_text('\n'.join(lines))


def compare_manifests(
    left: dict[str, str],
    right: dict[str, str],
    left_label: str,
    right_label: str,
) -> list[str]:
    """Return human-readable diff lines for manifest drift."""
    diffs: list[str] = []
    left_names = set(left)
    right_names = set(right)

    for name in sorted(left_names - right_names):
        diffs.append(f'missing in {right_label}: {name}{left[name]}')
    for name in sorted(right_names - left_names):
        diffs.append(f'extra in {right_label}: {name}{right[name]}')
    for name in sorted(left_names & right_names):
        if left[name] != right[name]:
            diffs.append(
                f'version mismatch for {name}: '
                f'{left_label} has {left[name]!r}, {right_label} has {right[name]!r}'
            )
    return diffs
