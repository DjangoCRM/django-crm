"""Legacy compatibility shim for relocated common utilities.

Import presentation helpers from ``sharedkernel.presentation``, ORM query
helpers from ``common.queries``, and workflow helpers from ``common.services``.
Accessing moved symbols through this module emits a :class:`DeprecationWarning`
and will stop working when the shim is removed in 3.0.0.
"""

from __future__ import annotations

import importlib
import warnings

from django.contrib.auth import get_user_model

from common.services.tokens import token_default

_REMOVAL_RELEASE = '3.0.0'
_OLD_MODULE = 'common.utils.helpers'

_LEGACY_EXPORTS: dict[str, str] = {
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
    'get_trans_for_lang': 'common.services.translations',
    'get_trans_for_user': 'common.services.translations',
    'get_user_language_code': 'common.services.translations',
}

__all__ = sorted(_LEGACY_EXPORTS) + ['USER_MODEL', 'token_default']

_warned_symbols: set[str] = set()


def __getattr__(name: str):
    canonical_module = _LEGACY_EXPORTS.get(name)
    if canonical_module is None:
        raise AttributeError(f'module {_OLD_MODULE!r} has no attribute {name!r}')

    new_path = f'{canonical_module}.{name}'
    if name not in _warned_symbols:
        warnings.warn(
            (
                f'{_OLD_MODULE}.{name} is deprecated; import from {new_path} '
                f'instead. The shim will be removed in {_REMOVAL_RELEASE}.'
            ),
            DeprecationWarning,
            stacklevel=2,
        )
        _warned_symbols.add(name)

    value = getattr(importlib.import_module(canonical_module), name)
    globals()[name] = value
    return value


USER_MODEL = get_user_model()
