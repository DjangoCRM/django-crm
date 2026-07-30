"""Mailbox credential resolution for IMAP and SMTP access."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Protocol

CREDENTIAL_MASK = '***REDACTED***'

logger = logging.getLogger('sharedkernel.credentials')


class AuthKind(str, Enum):
    PASSWORD = 'password'
    OAUTH2 = 'oauth2'


class MissingCredentialError(Exception):
    """Raised when a mailbox account has no usable credential."""

    def __init__(
        self,
        account_id: int | str,
        owner_id: int | str | None,
        field_name: str,
    ) -> None:
        self.account_id = account_id
        self.owner_id = owner_id
        self.field_name = field_name
        super().__init__(
            f"EmailAccount {account_id} (owner {owner_id}) is missing {field_name}"
        )


class EmailAccountLike(Protocol):
    pk: int | None
    owner_id: int | None
    email_host_user: str
    email_host: str
    imap_host: str
    email_host_password: str
    email_app_password: str
    refresh_token: str


@dataclass(frozen=True)
class MailboxCredential:
    """Resolved mailbox credential with masked diagnostic output."""

    user: str
    host: str
    auth_kind: AuthKind
    _secret: str

    @property
    def secret(self) -> str:
        """Return the raw credential value for transport authentication."""
        return self._secret

    def __repr__(self) -> str:
        return (
            f'MailboxCredential(user={self.user!r}, host={self.host!r}, '
            f'auth_kind={self.auth_kind.value!r}, secret={CREDENTIAL_MASK})'
        )

    def __str__(self) -> str:
        return repr(self)


def log_credential_resolution(
    account: EmailAccountLike,
    operation: str,
    credential: MailboxCredential,
) -> None:
    """Emit a structured log record with masked credential output."""
    logger.info(
        'Resolved mailbox credential account_id=%s owner_id=%s operation=%s '
        'auth_kind=%s credential=%s',
        account.pk,
        account.owner_id,
        operation,
        credential.auth_kind.value,
        credential,
        extra={
            'account_id': account.pk,
            'owner_id': account.owner_id,
            'operation': operation,
            'auth_kind': credential.auth_kind.value,
            'credential': str(credential),
        },
    )


class CredentialAccessor:
    """Resolve IMAP and SMTP credentials from EmailAccount records."""

    @staticmethod
    def for_imap(account: EmailAccountLike) -> MailboxCredential:
        return _resolve(account, host=account.imap_host or account.email_host, operation='imap')

    @staticmethod
    def for_smtp(account: EmailAccountLike) -> MailboxCredential:
        return _resolve(account, host=account.email_host, operation='smtp')


def _resolve(
    account: EmailAccountLike,
    *,
    host: str,
    operation: str,
) -> MailboxCredential:
    refresh_token = getattr(account, 'refresh_token', '') or ''
    if refresh_token:
        credential = MailboxCredential(
            user=account.email_host_user,
            host=host,
            auth_kind=AuthKind.OAUTH2,
            _secret=refresh_token,
        )
        log_credential_resolution(account, operation, credential)
        return credential

    app_password = account.email_app_password
    if app_password:
        credential = MailboxCredential(
            user=account.email_host_user,
            host=host,
            auth_kind=AuthKind.PASSWORD,
            _secret=app_password,
        )
        log_credential_resolution(account, operation, credential)
        return credential

    host_password = account.email_host_password
    if host_password:
        credential = MailboxCredential(
            user=account.email_host_user,
            host=host,
            auth_kind=AuthKind.PASSWORD,
            _secret=host_password,
        )
        log_credential_resolution(account, operation, credential)
        return credential

    account_id = account.pk if account.pk is not None else 'unsaved'
    owner_id = account.owner_id
    raise MissingCredentialError(
        account_id=account_id,
        owner_id=owner_id,
        field_name='email_app_password or email_host_password or refresh_token',
    )
