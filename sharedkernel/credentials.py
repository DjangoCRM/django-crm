"""Mailbox credential resolution for IMAP and SMTP access."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Protocol

from django.core.exceptions import PermissionDenied

CREDENTIAL_MASK = '***REDACTED***'

SECRET_FIELD_NAMES = (
    'email_host_password',
    'email_app_password',
    'refresh_token',
    'email_imail_ssl_keyfile',
)

logger = logging.getLogger('sharedkernel.credentials')

AUTH_MECHANISM_PASSWORD = 'password'
AUTH_MECHANISM_OAUTH2 = 'oauth2'


class AuthKind(str, Enum):
    PASSWORD = AUTH_MECHANISM_PASSWORD
    OAUTH2 = AUTH_MECHANISM_OAUTH2


class MissingMailCredentialError(Exception):
    """Raised when a mailbox account has no usable credential."""

    def __init__(self, account_id: int | str, field_name: str) -> None:
        self.account_id = account_id
        self.field_name = field_name
        super().__init__(f'EmailAccount {account_id} is missing {field_name}')


class OAuthTokenExchangeError(Exception):
    """Raised when a provider token exchange fails without echoing response bodies."""

    def __init__(
        self,
        status_code: int,
        provider_error: str,
        *,
        account_id: int | str | None = None,
    ) -> None:
        self.status_code = status_code
        self.provider_error = provider_error
        self.account_id = account_id
        super().__init__(
            f'OAuth token exchange failed with status {status_code} '
            f'and error {provider_error}'
        )


class MissingOAuthConfigError(Exception):
    """Raised when OAuth client configuration is absent."""

    def __init__(self, setting_name: str) -> None:
        self.setting_name = setting_name
        super().__init__(f'Missing OAuth configuration: {setting_name}')


MissingCredentialError = MissingMailCredentialError


class EmailAccountLike(Protocol):
    pk: int | None
    owner_id: int | None
    co_owner_id: int | None
    email_host_user: str
    email_host: str
    imap_host: str
    email_host_password: str
    email_app_password: str
    refresh_token: str
    email_port: int
    email_use_tls: bool
    email_use_ssl: bool
    email_imail_ssl_keyfile: str


def mask_secret(value: str) -> str:
    return CREDENTIAL_MASK if value else ''


@dataclass(frozen=True)
class ImapCredentials:
    host: str
    port: int
    user: str
    password: str
    use_ssl: bool
    ssl_keyfile: str

    def __repr__(self) -> str:
        return (
            f'ImapCredentials(host={self.host!r}, port={self.port!r}, user={self.user!r}, '
            f'password={CREDENTIAL_MASK}, use_ssl={self.use_ssl!r}, '
            f'ssl_keyfile={self.ssl_keyfile!r})'
        )

    def __str__(self) -> str:
        return repr(self)


@dataclass(frozen=True)
class SmtpCredentials:
    host: str
    port: int
    user: str
    password: str
    use_tls: bool
    auth_mechanism: str

    def __repr__(self) -> str:
        return (
            f'SmtpCredentials(host={self.host!r}, port={self.port!r}, user={self.user!r}, '
            f'password={CREDENTIAL_MASK}, use_tls={self.use_tls!r}, '
            f'auth_mechanism={self.auth_mechanism!r})'
        )

    def __str__(self) -> str:
        return repr(self)


@dataclass(frozen=True)
class OAuthCredentials:
    client_id: str
    client_secret: str
    refresh_token: str
    token_endpoint: str
    scope: str

    def __repr__(self) -> str:
        return (
            f'OAuthCredentials(client_id={self.client_id!r}, '
            f'client_secret={CREDENTIAL_MASK}, refresh_token={CREDENTIAL_MASK}, '
            f'token_endpoint={self.token_endpoint!r}, scope={self.scope!r})'
        )

    def __str__(self) -> str:
        return repr(self)


@dataclass(frozen=True)
class MailboxCredential:
    user: str
    host: str
    auth_kind: AuthKind
    _secret: str

    @property
    def secret(self) -> str:
        return self._secret

    def __repr__(self) -> str:
        return (
            f'MailboxCredential(user={self.user!r}, host={self.host!r}, '
            f'auth_kind={self.auth_kind.value!r}, secret={CREDENTIAL_MASK})'
        )

    def __str__(self) -> str:
        return repr(self)


def resolve_for_user(user: Any, email_account: EmailAccountLike) -> EmailAccountLike:
    """Mirror EmailAccountAdmin ownership scoping before reading credentials."""
    if getattr(user, 'is_superuser', False):
        return email_account

    user_id = getattr(user, 'pk', None)
    if user_id in (email_account.owner_id, getattr(email_account, 'co_owner_id', None)):
        return email_account

    raise PermissionDenied('User cannot access credentials for this EmailAccount.')


class CredentialAccessor:
    """Resolve IMAP and SMTP credentials from EmailAccount records."""

    @staticmethod
    def get_imap_credentials(email_account: EmailAccountLike) -> ImapCredentials:
        password, auth_mechanism = _resolve_password(email_account)
        credentials = ImapCredentials(
            host=email_account.imap_host or email_account.email_host,
            port=_imap_port(email_account),
            user=email_account.email_host_user,
            password=password,
            use_ssl=bool(getattr(email_account, 'email_use_ssl', True)),
            ssl_keyfile=getattr(email_account, 'email_imail_ssl_keyfile', '') or '',
        )
        _log_credential_resolution(
            email_account,
            operation='imap',
            auth_mechanism=auth_mechanism,
            credential=credentials,
        )
        return credentials

    @staticmethod
    def get_smtp_credentials(email_account: EmailAccountLike) -> SmtpCredentials:
        password, auth_mechanism = _resolve_password(email_account)
        credentials = SmtpCredentials(
            host=email_account.email_host,
            port=email_account.email_port,
            user=email_account.email_host_user,
            password=password,
            use_tls=bool(getattr(email_account, 'email_use_tls', False)),
            auth_mechanism=auth_mechanism,
        )
        _log_credential_resolution(
            email_account,
            operation='smtp',
            auth_mechanism=auth_mechanism,
            credential=credentials,
        )
        return credentials

    @staticmethod
    def for_imap(email_account: EmailAccountLike) -> MailboxCredential:
        password, auth_mechanism = _resolve_password(email_account)
        host = email_account.imap_host or email_account.email_host
        _log_credential_resolution(
            email_account,
            operation='imap',
            auth_mechanism=auth_mechanism,
            credential=ImapCredentials(
                host=host,
                port=_imap_port(email_account),
                user=email_account.email_host_user,
                password=password,
                use_ssl=bool(getattr(email_account, 'email_use_ssl', True)),
                ssl_keyfile=getattr(email_account, 'email_imail_ssl_keyfile', '') or '',
            ),
        )
        return MailboxCredential(
            user=email_account.email_host_user,
            host=host,
            auth_kind=AuthKind(auth_mechanism),
            _secret=password,
        )

    @staticmethod
    def for_smtp(email_account: EmailAccountLike) -> MailboxCredential:
        password, auth_mechanism = _resolve_password(email_account)
        _log_credential_resolution(
            email_account,
            operation='smtp',
            auth_mechanism=auth_mechanism,
            credential=SmtpCredentials(
                host=email_account.email_host,
                port=email_account.email_port,
                user=email_account.email_host_user,
                password=password,
                use_tls=bool(getattr(email_account, 'email_use_tls', False)),
                auth_mechanism=auth_mechanism,
            ),
        )
        return MailboxCredential(
            user=email_account.email_host_user,
            host=email_account.email_host,
            auth_kind=AuthKind(auth_mechanism),
            _secret=password,
        )

    @staticmethod
    def get_oauth_credentials(email_account: EmailAccountLike) -> OAuthCredentials:
        from django.conf import settings

        client_id = getattr(settings, 'CLIENT_ID', '') or ''
        client_secret = getattr(settings, 'CLIENT_SECRET', '') or ''
        if not client_id:
            raise MissingOAuthConfigError('GOOGLE_OAUTH2_CLIENT_ID')
        if not client_secret:
            raise MissingOAuthConfigError('GOOGLE_OAUTH2_CLIENT_SECRET')

        provider_settings = settings.OAUTH2_DATA.get(email_account.email_host)
        if not provider_settings:
            raise MissingOAuthConfigError('OAUTH2_DATA')

        token_endpoint = (
            f"{provider_settings['accounts_base_url']}/"
            f"{provider_settings['token_command']}"
        )
        credentials = OAuthCredentials(
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=getattr(email_account, 'refresh_token', '') or '',
            token_endpoint=token_endpoint,
            scope=provider_settings['scope'],
        )
        logger.info(
            'Resolved OAuth credentials account_id=%s owner_id=%s credential=%s',
            email_account.pk,
            email_account.owner_id,
            credentials,
            extra={
                'account_id': email_account.pk,
                'owner_id': email_account.owner_id,
                'credential': str(credentials),
            },
        )
        return credentials

    @staticmethod
    def store_refresh_token(email_account: EmailAccountLike, token: str) -> None:
        email_account.refresh_token = token
        email_account.save(update_fields=['refresh_token'])

    @staticmethod
    def store_access_token(
        email_account: EmailAccountLike,
        token: str,
        expires_at=None,
    ) -> None:
        update_fields = []
        if hasattr(email_account, 'access_token'):
            email_account.access_token = token
            update_fields.append('access_token')
        if hasattr(email_account, 'access_token_expires_at') and expires_at is not None:
            email_account.access_token_expires_at = expires_at
            update_fields.append('access_token_expires_at')
        if update_fields:
            email_account.save(update_fields=update_fields)


def _imap_port(email_account: EmailAccountLike) -> int:
    if getattr(email_account, 'email_use_ssl', False):
        return 993
    return 143


def _resolve_password(email_account: EmailAccountLike) -> tuple[str, str]:
    refresh_token = getattr(email_account, 'refresh_token', '') or ''
    if refresh_token:
        return refresh_token, AUTH_MECHANISM_OAUTH2

    app_password = email_account.email_app_password
    if app_password:
        return app_password, AUTH_MECHANISM_PASSWORD

    host_password = email_account.email_host_password
    if host_password:
        return host_password, AUTH_MECHANISM_PASSWORD

    account_id = email_account.pk if email_account.pk is not None else 'unsaved'
    raise MissingMailCredentialError(account_id, 'email_host_password')


def _log_credential_resolution(
    email_account: EmailAccountLike,
    *,
    operation: str,
    auth_mechanism: str,
    credential: ImapCredentials | SmtpCredentials,
) -> None:
    logger.info(
        'Resolved mailbox credential account_id=%s owner_id=%s operation=%s '
        'auth_mechanism=%s credential=%s',
        email_account.pk,
        email_account.owner_id,
        operation,
        auth_mechanism,
        credential,
        extra={
            'account_id': email_account.pk,
            'owner_id': email_account.owner_id,
            'operation': operation,
            'auth_mechanism': auth_mechanism,
            'credential': str(credential),
        },
    )
