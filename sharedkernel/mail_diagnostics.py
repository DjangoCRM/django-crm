"""Sanitized mail incident reporting for admin notifications and logs."""

from __future__ import annotations

import logging
import re
from typing import Any

from django.conf import settings
from django.core.cache import cache
from django.core.mail import mail_admins

from sharedkernel.credentials import CREDENTIAL_MASK, SECRET_FIELD_NAMES

logger = logging.getLogger('sharedkernel.mail_diagnostics')

DEFAULT_DEDUP_WINDOW_SECONDS = 300
CACHE_KEY_PREFIX = 'mail_diag_notify'

PROTOCOL_CREDENTIAL_TOKENS = (
    'LOGIN',
    'AUTHENTICATE',
    'PASS',
    'refresh_token',
    'access_token',
    'client_secret',
)

_SENSITIVE_KEY_PATTERN = re.compile(
    r'(' + '|'.join(re.escape(name) for name in (
        *SECRET_FIELD_NAMES,
        'refresh_token',
        'access_token',
        'client_secret',
    )) + r')\s*[=:]\s*([^\s,\)]+)',
    re.IGNORECASE,
)
_LOGIN_PATTERN = re.compile(
    r'(\bLOGIN\s+)(\S+)(?:\s+(\S+))?',
    re.IGNORECASE,
)
_AUTHENTICATE_PATTERN = re.compile(
    r'(\bAUTHENTICATE\s+\S+\s+)(\S+)',
    re.IGNORECASE,
)
_PASS_PATTERN = re.compile(r'(\bPASS\s+)(\S+)', re.IGNORECASE)


def _mask_login(match: re.Match[str]) -> str:
    prefix = match.group(1)
    if match.group(3):
        return f'{prefix}{match.group(2)} {CREDENTIAL_MASK}'
    return f'{prefix}{CREDENTIAL_MASK}'


def sanitize_text(text: str) -> str:
    """Mask credential values and protocol secrets in free-form text."""
    if not text:
        return ''

    result = str(text)
    result = _SENSITIVE_KEY_PATTERN.sub(rf'\1{CREDENTIAL_MASK}', result)
    result = _LOGIN_PATTERN.sub(_mask_login, result)
    result = _AUTHENTICATE_PATTERN.sub(rf'\1{CREDENTIAL_MASK}', result)
    result = _PASS_PATTERN.sub(rf'\1{CREDENTIAL_MASK}', result)
    return result


def summarize_payload(
    payload: Any,
    *,
    folder: str | None = None,
    uid: str | int | None = None,
    content_type: str | None = None,
) -> dict[str, Any]:
    """Return structural metadata for a raw payload without echoing its contents."""
    metadata: dict[str, Any] = {}
    if folder is not None:
        metadata['folder'] = folder
    if uid is not None:
        metadata['uid'] = uid
    if content_type is not None:
        metadata['content_type'] = content_type

    if payload is None:
        metadata['payload_bytes'] = 0
        return metadata

    if isinstance(payload, bytes):
        metadata['payload_bytes'] = len(payload)
        return metadata

    if isinstance(payload, str):
        metadata['payload_bytes'] = len(payload.encode('utf-8', errors='replace'))
        return metadata

    if isinstance(payload, (list, tuple)):
        metadata['payload_items'] = len(payload)
        metadata['payload_bytes'] = sum(
            len(item)
            for item in payload
            if isinstance(item, bytes)
        )
        return metadata

    metadata['payload_type'] = type(payload).__name__
    return metadata


def summarize_command_params(params: Any) -> str:
    """Describe IMAP command parameters without echoing credential values."""
    if params is None:
        return 'None'
    if isinstance(params, tuple):
        if len(params) >= 2:
            return f'({params[0]!r}, {CREDENTIAL_MASK})'
        if len(params) == 1:
            return f'({params[0]!r},)'
        return '()'
    return sanitize_text(repr(params))


def build_incident_summary(
    *,
    account_id: int | str | None,
    owner_id: int | str | None,
    operation: str,
    exception_class: str,
    exception_summary: str,
    context: dict[str, Any] | None = None,
    occurrence_count: int = 1,
) -> str:
    lines = [
        f'Operation: {operation}',
        f'Account id: {account_id}',
        f'Owner id: {owner_id}',
        f'Exception class: {exception_class}',
        f'Exception summary: {exception_summary}',
        f'Occurrence count: {occurrence_count}',
    ]
    for key, value in sorted((context or {}).items()):
        if isinstance(value, dict):
            rendered = ', '.join(f'{k}={v}' for k, v in value.items())
        else:
            rendered = sanitize_text(str(value))
        lines.append(f'{key}: {rendered}')
    return '\n'.join(lines)


def _dedup_window_seconds() -> int:
    return getattr(settings, 'MAIL_DIAGNOSTICS_DEDUP_SECONDS', DEFAULT_DEDUP_WINDOW_SECONDS)


def _notification_cache_key(account_id: Any, operation: str) -> str:
    return f'{CACHE_KEY_PREFIX}:{account_id}:{operation}'


def _next_occurrence_count(account_id: Any, operation: str) -> int:
    key = _notification_cache_key(account_id, operation)
    count = cache.get(key, 0) + 1
    cache.set(key, count, timeout=_dedup_window_seconds())
    return count


def _should_send_admin_notification(account_id: Any, operation: str) -> bool:
    key = f'{CACHE_KEY_PREFIX}:sent:{account_id}:{operation}'
    if cache.get(key):
        return False
    cache.set(key, True, timeout=_dedup_window_seconds())
    return True


def report_mail_incident(
    *,
    account: Any = None,
    operation: str,
    exception: BaseException | None = None,
    context: dict[str, Any] | None = None,
    subject: str | None = None,
    fail_silently: bool = True,
) -> str:
    """Log a structured incident, notify admins once per dedup window, return summary."""
    safe_context: dict[str, Any] = {}
    raw_context = context or {}

    account_id = getattr(account, 'pk', None) if account is not None else raw_context.get('account_id')
    owner_id = getattr(account, 'owner_id', None) if account is not None else raw_context.get('owner_id')

    payload_keys = {
        'raw_content', 'data', 'payload', 'message_bytes', 'richest', 'b_msg', 'message_data',
    }
    for key, value in raw_context.items():
        if key in payload_keys:
            safe_context[key] = summarize_payload(
                value,
                folder=raw_context.get('folder'),
                uid=raw_context.get('uid'),
                content_type=raw_context.get('content_type'),
            )
        elif key == 'params':
            safe_context[key] = summarize_command_params(value)
        else:
            safe_context[key] = sanitize_text(str(value)) if value is not None else ''

    exception_class = type(exception).__name__ if exception else str(
        raw_context.get('exception_class', 'Unknown')
    )
    exception_summary = sanitize_text(str(exception)) if exception else sanitize_text(
        str(raw_context.get('exception_summary', ''))
    )

    occurrence_count = _next_occurrence_count(account_id, operation)
    summary = build_incident_summary(
        account_id=account_id,
        owner_id=owner_id,
        operation=operation,
        exception_class=exception_class,
        exception_summary=exception_summary,
        context=safe_context,
        occurrence_count=occurrence_count,
    )

    logger.error(
        'Mail incident operation=%s account_id=%s owner_id=%s exception_class=%s '
        'occurrence_count=%s',
        operation,
        account_id,
        owner_id,
        exception_class,
        occurrence_count,
        extra={
            'operation': operation,
            'account_id': account_id,
            'owner_id': owner_id,
            'exception_class': exception_class,
            'occurrence_count': occurrence_count,
            'context': safe_context,
        },
    )

    if _should_send_admin_notification(account_id, operation):
        mail_admins(
            subject or f'Mail incident: {operation}',
            summary,
            fail_silently=fail_silently,
        )

    return summary
