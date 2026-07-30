#!/usr/bin/env python3
"""Mechanically migrate legacy common.utils.helpers imports to canonical modules."""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

LEGACY_EXPORTS: dict[str, str] = {
    'add_chat_context': 'common.queries',
    'add_phone_q_params': 'common.queries',
    'annotate_chat': 'common.queries',
    'get_active_users': 'common.queries',
    'get_department_id': 'common.queries',
    'get_manager_departments': 'common.queries',
    'CONTENT_COPY_ICON': 'sharedkernel.presentation',
    'CONTENT_COPY_LINK': 'sharedkernel.presentation',
    'COPY_STR': 'sharedkernel.presentation',
    'CRM_NOTICE': 'sharedkernel.presentation',
    'FRIDAY_SATURDAY_SUNDAY_MSG': 'sharedkernel.presentation',
    'LEADERS': 'sharedkernel.presentation',
    'OBJ_DOESNT_EXIT_STR': 'sharedkernel.presentation',
    'ONCLICK_STR': 'sharedkernel.presentation',
    'SAFE_ATTACH_FILE_ICON': 'sharedkernel.presentation',
    'SAFE_SUBJECT_ICON': 'sharedkernel.presentation',
    'get_formatted_short_date': 'sharedkernel.presentation',
    'get_verbose_name': 'sharedkernel.presentation',
    'popup_window': 'sharedkernel.presentation',
    'compose_message': 'common.services.messaging',
    'compose_subject': 'common.services.messaging',
    'get_delta_date': 'common.services.datetimes',
    'get_now': 'common.services.datetimes',
    'get_today': 'common.services.datetimes',
    'notify_admins_no_email': 'common.services.notifications',
    'save_message': 'common.services.notifications',
    'send_crm_email': 'common.services.notifications',
    'set_toggle_tooltip': 'common.services.notifications',
    'token_default': 'common.services.tokens',
    'get_trans_for_lang': 'common.services.translations',
    'get_trans_for_user': 'common.services.translations',
    'get_user_language_code': 'common.services.translations',
}

RESIDENT_SYMBOLS = frozenset({'USER_MODEL'})

EXCLUDE_PATH_PARTS = frozenset({'migrations', '__pycache__'})

EXCLUDE_FILES = frozenset({
    PROJECT_ROOT / 'common/utils/helpers.py',
    PROJECT_ROOT / 'tests/common/test_helpers_shim.py',
    PROJECT_ROOT / 'tests/common/test_helpers_queries_characterization.py',
    PROJECT_ROOT / 'tests/common/test_helpers_services_characterization.py',
    PROJECT_ROOT / 'tests/common/test_helpers_presentation_characterization.py',
    PROJECT_ROOT / 'tests/common/services/test_tokens.py',
    PROJECT_ROOT / 'scripts/migrate_helper_imports.py',
})


def should_process(path: Path) -> bool:
    if path.suffix != '.py' or not path.is_file():
        return False
    if path in EXCLUDE_FILES:
        return False
    return not any(part in EXCLUDE_PATH_PARTS for part in path.parts)


def replacement_lines_for_import(stripped: str) -> list[str]:
    imported = stripped[len('from common.utils.helpers import '):].strip()
    by_module: dict[str, list[str]] = defaultdict(list)
    helpers_only: list[str] = []
    for part in imported.split(','):
        chunk = part.strip()
        if not chunk:
            continue
        if ' as ' in chunk:
            name, alias = chunk.split(' as ', 1)
            name = name.strip()
            alias = alias.strip()
            line_suffix = f' as {alias}'
        else:
            name = chunk
            line_suffix = ''
        if name in RESIDENT_SYMBOLS:
            helpers_only.append(f'from common.utils.helpers import {name}{line_suffix}\n')
        elif name in LEGACY_EXPORTS:
            by_module[LEGACY_EXPORTS[name]].append(
                f'from {LEGACY_EXPORTS[name]} import {name}{line_suffix}\n',
            )
        else:
            raise ValueError(f'unknown helper symbol {name!r}')
    lines: list[str] = []
    for module in sorted(by_module):
        lines.extend(by_module[module])
    lines.extend(sorted(set(helpers_only)))
    return lines


def rewrite_source(source: str, path: Path) -> tuple[str, bool]:
    lines = source.splitlines(keepends=True)
    output: list[str] = []
    changed = False
    skip_utils_helpers = False

    for line in lines:
        stripped = line.strip()
        indent = line[: len(line) - len(line.lstrip())]
        if stripped.startswith('from common.utils.helpers import '):
            changed = True
            for replacement in replacement_lines_for_import(stripped):
                output.append(f'{indent}{replacement.lstrip()}')
            continue
        if stripped == 'from common.utils import helpers':
            changed = True
            skip_utils_helpers = True
            continue
        output.append(line)

    if not changed:
        return source, False

    if skip_utils_helpers:
        text = ''.join(output)
        for symbol in sorted(LEGACY_EXPORTS, key=len, reverse=True):
            text = text.replace(f'helpers.{symbol}', symbol)
        return text, True

    return ''.join(output), True


def main() -> int:
    changed: list[Path] = []
    for path in sorted(PROJECT_ROOT.rglob('*.py')):
        if not should_process(path):
            continue
        original = path.read_text(encoding='utf-8')
        updated, did_change = rewrite_source(original, path)
        if did_change and updated != original:
            path.write_text(updated, encoding='utf-8')
            changed.append(path)
    print(f'Updated {len(changed)} files')
    return 0


if __name__ == '__main__':
    sys.exit(main())
