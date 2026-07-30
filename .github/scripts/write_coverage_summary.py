#!/usr/bin/env python3
"""Render per-application coverage into the GitHub Actions job summary."""

from __future__ import annotations

import json
import os
from pathlib import Path

APPLICATIONS = (
    'common',
    'crm',
    'analytics',
    'tasks',
    'massmail',
    'chat',
    'voip',
    'quality',
    'help',
    'settings',
    'webcrm',
)


def _app_files(files: dict, app: str) -> dict:
    prefix = f'{app}/'
    return {
        path: meta
        for path, meta in files.items()
        if path.startswith(prefix) or f'/{prefix}' in path.replace('\\', '/')
    }


def main() -> None:
    coverage_data = json.loads(Path('coverage.json').read_text(encoding='utf-8'))
    totals = coverage_data['totals']
    summary_path = os.environ['GITHUB_STEP_SUMMARY']
    lines = [
        '## Coverage (sqlite leg)',
        '',
        f"**Total coverage:** {totals['percent_covered_display']}",
        '',
        '| Application | Statements | Miss | Cover |',
        '|---|---:|---:|---:|',
    ]
    for app in APPLICATIONS:
        matched = _app_files(coverage_data['files'], app)
        if not matched:
            lines.append(f'| {app} | 0 | 0 | n/a |')
            continue
        statements = sum(item['summary']['num_statements'] for item in matched.values())
        missing = sum(len(item['missing_lines']) for item in matched.values())
        covered = statements - missing
        percent = (covered / statements * 100) if statements else 0.0
        lines.append(f'| {app} | {statements} | {missing} | {percent:.1f}% |')
    with open(summary_path, 'a', encoding='utf-8') as handle:
        handle.write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()
