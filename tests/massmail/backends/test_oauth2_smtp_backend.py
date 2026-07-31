"""Tests for OAuth2EmailBackend token refresh via accessor."""

from __future__ import annotations

from unittest import mock

from django.test import SimpleTestCase, override_settings

from massmail.backends.smtp import OAuth2EmailBackend
from sharedkernel.credentials import (
    AUTH_MECHANISM_OAUTH2,
    OAuthTokenExchangeError,
    SmtpCredentials,
)
from sharedkernel.oauth_exchange import OAuthTokenResponse

SENTINEL_REFRESH = 'sentinel-refresh-token-xyz'
SENTINEL_ACCESS = 'sentinel-access-token-xyz'


def _oauth_account():
    account = mock.Mock(spec=['pk', 'owner_id', 'email_host', 'refresh_token', 'save'])
    account.pk = 99
    account.owner_id = 1
    account.email_host = 'smtp.gmail.com'
    account.refresh_token = SENTINEL_REFRESH
    return account


class OAuth2EmailBackendTests(SimpleTestCase):
    @override_settings(
        CLIENT_ID='test-client-id',
        CLIENT_SECRET='test-client-secret',
        OAUTH2_DATA={
            'smtp.gmail.com': {
                'accounts_base_url': 'https://accounts.example.com',
                'token_command': 'o/oauth2/token',
                'scope': 'https://mail.example.com/',
            },
        },
    )
    @mock.patch('massmail.backends.smtp.exchange_refresh_token')
    def test_get_access_token_uses_accessor_and_stores_rotated_refresh(self, mock_exchange):
        account = _oauth_account()
        mock_exchange.return_value = OAuthTokenResponse(
            access_token=SENTINEL_ACCESS,
            refresh_token='rotated-refresh-token',
        )
        backend = OAuth2EmailBackend.from_smtp_credentials(
            SmtpCredentials(
                host='smtp.gmail.com',
                port=587,
                user='user@example.com',
                password=SENTINEL_REFRESH,
                use_tls=True,
                auth_mechanism=AUTH_MECHANISM_OAUTH2,
            ),
            email_account=account,
        )

        token = backend.get_access_token()

        self.assertEqual(token, SENTINEL_ACCESS)
        mock_exchange.assert_called_once()
        credentials = mock_exchange.call_args.args[0]
        self.assertEqual(credentials.refresh_token, SENTINEL_REFRESH)
        account.save.assert_called_once_with(update_fields=['refresh_token'])
        self.assertEqual(account.refresh_token, 'rotated-refresh-token')

    @override_settings(
        CLIENT_ID='test-client-id',
        CLIENT_SECRET='test-client-secret',
        OAUTH2_DATA={
            'smtp.gmail.com': {
                'accounts_base_url': 'https://accounts.example.com',
                'token_command': 'o/oauth2/token',
                'scope': 'https://mail.example.com/',
            },
        },
    )
    @mock.patch('massmail.backends.smtp.exchange_refresh_token')
    def test_get_access_token_surfaces_sanitized_exchange_error(self, mock_exchange):
        account = _oauth_account()
        mock_exchange.side_effect = OAuthTokenExchangeError(400, 'invalid_grant')
        backend = OAuth2EmailBackend.from_smtp_credentials(
            SmtpCredentials(
                host='smtp.gmail.com',
                port=587,
                user='user@example.com',
                password=SENTINEL_REFRESH,
                use_tls=True,
                auth_mechanism=AUTH_MECHANISM_OAUTH2,
            ),
            email_account=account,
        )

        with self.assertRaises(OAuthTokenExchangeError) as ctx:
            backend.get_access_token()

        err = ctx.exception
        self.assertEqual(err.status_code, 400)
        self.assertEqual(err.provider_error, 'invalid_grant')
        self.assertEqual(err.account_id, 99)
        self.assertNotIn(SENTINEL_REFRESH, str(err))
