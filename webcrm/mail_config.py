"""Assemble mail-related Django settings from environment variables."""

from __future__ import annotations

import logging
import re
from typing import Any

from django.core.exceptions import ImproperlyConfigured

from webcrm.config import ENV_REMEDIATION, config

logger = logging.getLogger(__name__)

_ADMIN_ENTRY_RE = re.compile(r'^\s*(.+?)\s*<([^>]+)>\s*$')

_MAIL_COMPLETENESS_KEYS = (
    'EMAIL_HOST',
    'EMAIL_HOST_USER',
    'EMAIL_HOST_PASSWORD',
    'DEFAULT_FROM_EMAIL',
    'SERVER_EMAIL',
)

_EMPTY_ADMINS_WARNING = (
    'DJANGO_ADMINS is unset or empty; mail_admins() will not deliver notifications.'
)


def parse_admin_recipients(value: str, variable_name: str) -> list[tuple[str, str]]:
    """Parse ``Name <address>`` entries into Django ADMINS/MANAGERS tuples."""
    if not value.strip():
        return []

    entries = [part.strip() for part in value.split(',') if part.strip()]
    recipients: list[tuple[str, str]] = []
    for index, entry in enumerate(entries, start=1):
        match = _ADMIN_ENTRY_RE.match(entry)
        if not match:
            raise ImproperlyConfigured(
                f"Malformed entry at position {index} in configuration variable "
                f"'{variable_name}'. Expected format: Name <address>. "
                f"{ENV_REMEDIATION}"
            )
        name, address = match.group(1), match.group(2).strip()
        if '@' not in address:
            raise ImproperlyConfigured(
                f"Malformed entry at position {index} in configuration variable "
                f"'{variable_name}'. Email address must contain '@'. "
                f"{ENV_REMEDIATION}"
            )
        recipients.append((name, address))
    return recipients


def _optional(name: str, *, secret: bool = False) -> str:
    return config.get(name, default='', secret=secret)


def _validate_mail_completeness(values: dict[str, str], *, debug: bool) -> None:
    supplied = {key: value for key, value in values.items() if value.strip()}
    if debug or not supplied:
        return

    missing = [
        key for key in _MAIL_COMPLETENESS_KEYS
        if not values[key].strip()
    ]
    if missing:
        raise ImproperlyConfigured(
            'Incomplete mail configuration: the following variables must all be '
            f"set when any mail setting is supplied: {', '.join(missing)}. "
            f"{ENV_REMEDIATION}"
        )


def _validate_tls_ssl(use_tls: bool, use_ssl: bool) -> None:
    if use_tls and use_ssl:
        raise ImproperlyConfigured(
            'EMAIL_USE_TLS and EMAIL_USE_SSL are mutually exclusive; enable only one. '
            f'{ENV_REMEDIATION}'
        )


def build_mail_settings(*, debug: bool) -> dict[str, Any]:
    """Return outbound mail settings resolved through ConfigAccessor."""
    config.register_secret('EMAIL_HOST_PASSWORD')
    config.register_secret('GOOGLE_OAUTH2_CLIENT_SECRET')

    host = _optional('EMAIL_HOST')
    user = _optional('EMAIL_HOST_USER')
    password = _optional('EMAIL_HOST_PASSWORD', secret=True)
    default_from = _optional('DEFAULT_FROM_EMAIL')
    server_email = _optional('SERVER_EMAIL')

    _validate_mail_completeness(
        {
            'EMAIL_HOST': host,
            'EMAIL_HOST_USER': user,
            'EMAIL_HOST_PASSWORD': password,
            'DEFAULT_FROM_EMAIL': default_from,
            'SERVER_EMAIL': server_email,
        },
        debug=debug,
    )

    use_tls = config.get_bool('EMAIL_USE_TLS', default=True)
    use_ssl = config.get_bool('EMAIL_USE_SSL', default=False)
    _validate_tls_ssl(use_tls, use_ssl)

    if not host.strip():
        if debug or config.is_testing():
            return {
                'EMAIL_BACKEND': 'django.core.mail.backends.console.EmailBackend',
                'EMAIL_HOST': '',
                'EMAIL_HOST_USER': '',
                'EMAIL_HOST_PASSWORD': '',
                'EMAIL_PORT': config.get_int('EMAIL_PORT', default=587),
                'EMAIL_USE_TLS': use_tls,
                'EMAIL_USE_SSL': use_ssl,
                'DEFAULT_FROM_EMAIL': default_from,
                'SERVER_EMAIL': server_email,
            }
        raise ImproperlyConfigured(
            "Required configuration variable 'EMAIL_HOST' is not set. "
            f'{ENV_REMEDIATION}'
        )

    return {
        'EMAIL_HOST': host,
        'EMAIL_HOST_USER': user,
        'EMAIL_HOST_PASSWORD': password,
        'EMAIL_PORT': config.get_int('EMAIL_PORT', default=587),
        'EMAIL_USE_TLS': use_tls,
        'EMAIL_USE_SSL': use_ssl,
        'DEFAULT_FROM_EMAIL': default_from,
        'SERVER_EMAIL': server_email,
    }


def build_admin_recipients(*, debug: bool) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    """Return ADMINS and MANAGERS parsed from the environment."""
    admins_raw = config.get('DJANGO_ADMINS', default='')
    managers_raw = config.get('DJANGO_MANAGERS', default='')
    admins = parse_admin_recipients(admins_raw, 'DJANGO_ADMINS')
    managers = parse_admin_recipients(managers_raw, 'DJANGO_MANAGERS')

    if not debug and not config.is_testing() and not admins:
        logger.warning(_EMPTY_ADMINS_WARNING)

    return admins, managers


def build_crm_identity_settings() -> dict[str, str]:
    """Return CRM self-reference and Google OAuth2 client settings."""
    return {
        'CRM_IP': config.get('CRM_IP', default='127.0.0.1'),
        'CRM_HOST': config.get('CRM_HOST', default='my_crm_host_name'),
        'CLIENT_ID': config.get('GOOGLE_OAUTH2_CLIENT_ID', default=''),
        'CLIENT_SECRET': config.get('GOOGLE_OAUTH2_CLIENT_SECRET', default='', secret=True),
    }
