"""EmailAccount fixture factories for credential accessor tests."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any


def app_password_account(**overrides: Any) -> SimpleNamespace:
    account = SimpleNamespace(
        pk=1,
        owner_id=10,
        email_host_user='app-user@example.com',
        email_host='smtp.example.com',
        imap_host='imap.example.com',
        email_host_password='host-secret',
        email_app_password='app-secret',
        refresh_token='',
        email_port=587,
        email_use_tls=True,
        email_use_ssl=False,
    )
    account.__dict__.update(overrides)
    return account


def host_password_account(**overrides: Any) -> SimpleNamespace:
    account = SimpleNamespace(
        pk=2,
        owner_id=11,
        email_host_user='host-user@example.com',
        email_host='smtp.example.com',
        imap_host='imap.example.com',
        email_host_password='host-only-secret',
        email_app_password='',
        refresh_token='',
        email_port=587,
        email_use_tls=True,
        email_use_ssl=False,
    )
    account.__dict__.update(overrides)
    return account


def no_credential_account(**overrides: Any) -> SimpleNamespace:
    account = SimpleNamespace(
        pk=3,
        owner_id=12,
        email_host_user='missing-user@example.com',
        email_host='smtp.example.com',
        imap_host='imap.example.com',
        email_host_password='',
        email_app_password='',
        refresh_token='',
    )
    account.__dict__.update(overrides)
    return account


def oauth2_account(**overrides: Any) -> SimpleNamespace:
    account = SimpleNamespace(
        pk=4,
        owner_id=13,
        email_host_user='oauth-user@gmail.com',
        email_host='smtp.gmail.com',
        imap_host='imap.gmail.com',
        email_host_password='ignored-host-secret',
        email_app_password='ignored-app-secret',
        refresh_token='oauth-refresh-token-value',
        email_port=587,
        email_use_tls=True,
        email_use_ssl=False,
    )
    account.__dict__.update(overrides)
    return account
