"""Tests for shared OAuth token exchange helpers."""

from __future__ import annotations

import json
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase, override_settings

from sharedkernel.credentials import OAuthCredentials, OAuthTokenExchangeError
from sharedkernel.oauth_exchange import (
    exchange_authorization_code,
    exchange_refresh_token,
)

FIXTURES = Path(__file__).resolve().parent.parent / 'fixtures'
SENTINEL_CLIENT_SECRET = 'sentinel-client-secret-xyz'
SENTINEL_REFRESH = 'sentinel-refresh-token-xyz'


def _credentials(**overrides) -> OAuthCredentials:
    base = {
        'client_id': 'test-client-id',
        'client_secret': SENTINEL_CLIENT_SECRET,
        'refresh_token': SENTINEL_REFRESH,
        'token_endpoint': 'https://accounts.example.com/o/oauth2/token',
        'scope': 'https://mail.example.com/',
    }
    base.update(overrides)
    return OAuthCredentials(**base)


def _mock_response(status_code: int, payload: dict):
    response = mock.Mock()
    response.status_code = status_code
    response.json.return_value = payload
    response.text = json.dumps(payload)
    return response


class OAuthExchangeTests(SimpleTestCase):
    @mock.patch('sharedkernel.oauth_exchange.requests.post')
    def test_exchange_refresh_token_success(self, mock_post):
        payload = json.loads((FIXTURES / 'oauth_token_refresh_success.json').read_text())
        mock_post.return_value = _mock_response(200, payload)

        response = exchange_refresh_token(_credentials())

        self.assertEqual(response.access_token, 'stub-access-token-value')
        self.assertEqual(response.expires_in, 3600)
        mock_post.assert_called_once()
        posted_params = mock_post.call_args.kwargs.get('params') or mock_post.call_args.args[1]
        self.assertEqual(posted_params['client_secret'], SENTINEL_CLIENT_SECRET)
        self.assertEqual(posted_params['refresh_token'], SENTINEL_REFRESH)

    @mock.patch('sharedkernel.oauth_exchange.requests.post')
    def test_exchange_refresh_token_provider_error_does_not_leak_body(self, mock_post):
        payload = json.loads((FIXTURES / 'oauth_token_refresh_error.json').read_text())
        mock_post.return_value = _mock_response(400, payload)

        with self.assertRaises(OAuthTokenExchangeError) as ctx:
            exchange_refresh_token(_credentials())

        err = ctx.exception
        self.assertEqual(err.status_code, 400)
        self.assertEqual(err.provider_error, 'invalid_grant')
        self.assertNotIn(SENTINEL_CLIENT_SECRET, str(err))
        self.assertNotIn(payload['error_description'], str(err))

    @mock.patch('sharedkernel.oauth_exchange.requests.post')
    def test_exchange_authorization_code_success(self, mock_post):
        payload = json.loads((FIXTURES / 'oauth_token_auth_code_success.json').read_text())
        mock_post.return_value = _mock_response(200, payload)

        response = exchange_authorization_code(
            _credentials(refresh_token=''),
            authorization_code='auth-code',
            redirect_uri='https://example.com/callback',
        )

        self.assertEqual(response.access_token, 'stub-access-token-value')
        self.assertEqual(response.refresh_token, 'stub-refresh-token-value')

    @mock.patch('sharedkernel.oauth_exchange.requests.post')
    def test_exchange_refresh_token_transport_error(self, mock_post):
        mock_post.side_effect = ConnectionError('network down')

        with self.assertRaises(OAuthTokenExchangeError) as ctx:
            exchange_refresh_token(_credentials())

        self.assertEqual(ctx.exception.provider_error, 'transport_error')


class OAuthCredentialsAccessorTests(SimpleTestCase):
    @override_settings(
        CLIENT_ID='configured-client-id',
        CLIENT_SECRET='configured-client-secret',
        OAUTH2_DATA={
            'smtp.gmail.com': {
                'accounts_base_url': 'https://accounts.example.com',
                'token_command': 'o/oauth2/token',
                'scope': 'https://mail.example.com/',
            },
        },
    )
    def test_get_oauth_credentials_masks_repr(self):
        from sharedkernel.credentials import CREDENTIAL_MASK, CredentialAccessor

        account = mock.Mock()
        account.pk = 42
        account.owner_id = 7
        account.email_host = 'smtp.gmail.com'
        account.refresh_token = SENTINEL_REFRESH

        credentials = CredentialAccessor.get_oauth_credentials(account)
        rendered = repr(credentials)

        self.assertIn(CREDENTIAL_MASK, rendered)
        self.assertNotIn(SENTINEL_REFRESH, rendered)
        self.assertNotIn('configured-client-secret', rendered)

    @override_settings(CLIENT_ID='', CLIENT_SECRET='')
    def test_get_oauth_credentials_missing_client_id(self):
        from sharedkernel.credentials import CredentialAccessor, MissingOAuthConfigError

        account = mock.Mock()
        account.email_host = 'smtp.gmail.com'
        account.refresh_token = SENTINEL_REFRESH

        with self.assertRaises(MissingOAuthConfigError):
            CredentialAccessor.get_oauth_credentials(account)
