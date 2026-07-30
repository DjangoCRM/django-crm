"""Security-related Django settings resolved through ConfigAccessor."""

from __future__ import annotations

import re

from django.core.exceptions import ImproperlyConfigured

from webcrm.config import ENV_REMEDIATION, config

_SCHEME_RE = re.compile(r'^[a-zA-Z][a-zA-Z0-9+.-]*://')


def normalize_url_prefix(name: str, value: str) -> str:
    """Normalize an obfuscated URL prefix to ``segment/`` with no leading slash."""
    stripped = value.strip()
    if not stripped:
        raise ImproperlyConfigured(
            f"Configuration variable '{name}' must not be empty. {ENV_REMEDIATION}"
        )
    if any(ch.isspace() for ch in stripped) or _SCHEME_RE.search(stripped):
        raise ImproperlyConfigured(
            f"Configuration variable '{name}' must not contain whitespace or a URL scheme. "
            f"{ENV_REMEDIATION}"
        )
    normalized = stripped.strip('/')
    if not normalized:
        raise ImproperlyConfigured(
            f"Configuration variable '{name}' must not be empty. {ENV_REMEDIATION}"
        )
    return f'{normalized}/'


def build_url_prefix_settings() -> dict[str, str]:
    """Return obfuscated admin, CRM and login URL prefixes."""
    return {
        'SECRET_CRM_PREFIX': normalize_url_prefix(
            'SECRET_CRM_PREFIX',
            config.get('SECRET_CRM_PREFIX', default='123/'),
        ),
        'SECRET_ADMIN_PREFIX': normalize_url_prefix(
            'SECRET_ADMIN_PREFIX',
            config.get('SECRET_ADMIN_PREFIX', default='456-admin/'),
        ),
        'SECRET_LOGIN_PREFIX': normalize_url_prefix(
            'SECRET_LOGIN_PREFIX',
            config.get('SECRET_LOGIN_PREFIX', default='789-login/'),
        ),
    }


def build_recaptcha_settings() -> dict[str, str]:
    """Return Google reCAPTCHA site and secret keys."""
    config.register_secret('GOOGLE_RECAPTCHA_SECRET_KEY')
    site_key = config.get('GOOGLE_RECAPTCHA_SITE_KEY', default='')
    secret_key = config.get('GOOGLE_RECAPTCHA_SECRET_KEY', default='', secret=True)
    if bool(site_key.strip()) ^ bool(secret_key.strip()):
        missing = (
            'GOOGLE_RECAPTCHA_SECRET_KEY'
            if site_key.strip()
            else 'GOOGLE_RECAPTCHA_SITE_KEY'
        )
        raise ImproperlyConfigured(
            f"Incomplete reCAPTCHA configuration: '{missing}' must be set when its "
            f"companion key is supplied. {ENV_REMEDIATION}"
        )
    return {
        'GOOGLE_RECAPTCHA_SITE_KEY': site_key,
        'GOOGLE_RECAPTCHA_SECRET_KEY': secret_key,
    }
