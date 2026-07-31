import json
from random import random
from unittest.mock import patch, MagicMock
from django.contrib.messages import get_messages
from django.contrib.messages.storage import default_storage
from django.contrib.sessions.middleware import SessionMiddleware
from django.core import mail
from django.test import Client, RequestFactory
from django.urls import reverse

from common.utils.helpers import USER_MODEL
from massmail.models.email_account import EmailAccount
from massmail.views.get_oauth2_tokens import (
    OAUTH2_SESSION_KEY,
    request_authorization_code,
    get_refresh_token,
)
from sharedkernel.credentials import CREDENTIAL_MASK
from sharedkernel.oauth_exchange import OAuthTokenResponse
from tests.base_test_classes import BaseTestCase

MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'
SENTINEL_REFRESH = 'sentinel-refresh-token-xyz'
SENTINEL_SECRET = 'sentinel-client-secret-xyz'


class GetOauth2TokensTestCase(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.owner = USER_MODEL.objects.get(username="Andrew.Manager.Global")
        cls.other_user = USER_MODEL.objects.get(username="Masha.Co-worker.Bookkeeping")
        cls.ea = EmailAccount.objects.create(
            name='CRM Email Account',
            email_host='smtp.gmail.com',
            email_port=587,
            email_host_user='andrew@example.com',
            email_host_password='password',
            from_email='andrew@example.com',
            owner=cls.owner,
        )
        cls.url = reverse("get_refresh_token")
        cls.client = Client()

    def setUp(self):
        print("Run Test Method:", self._testMethodName)
        self.factory = RequestFactory()
        self.client.force_login(self.owner)
        mail.outbox.clear()

    def _session_request(self, url, *, user=None, session_data=None):
        request = self.factory.get(url)
        request.user = user or self.owner
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        if session_data:
            request.session.update(session_data)
        request.session.save()
        request._messages = default_storage(request)
        return request

    def test_request_authorization_code(self):
        url = reverse("request_authorization_code", args=(self.ea.id,))
        request = self._session_request(url)
        response = request_authorization_code(request, self.ea.id)
        self.assertEqual(response.status_code, 302)
        self.assertIn('state=', response.url)
        self.assertEqual(
            request.session[OAUTH2_SESSION_KEY]['account_id'],
            self.ea.id,
        )

    def test_request_authorization_code_denies_other_user(self):
        url = reverse("request_authorization_code", args=(self.ea.id,))
        request = self._session_request(url, user=self.other_user)
        response = request_authorization_code(request, self.ea.id)
        self.assertEqual(response.status_code, 403)

    def test_request_authorization_code_no_data(self):
        url = reverse("request_authorization_code", args=(self.ea.id,))
        request = self._session_request(url)
        with self.settings(OAUTH2_DATA={}, MESSAGE_STORAGE=MESSAGE_STORAGE):
            response = request_authorization_code(request, self.ea.id)
        self.assertEqual(response.status_code, 302)

    @patch("massmail.views.get_oauth2_tokens.exchange_authorization_code")
    def test_get_refresh_token_success(self, mock_exchange):
        refresh_token = str(random())
        mock_exchange.return_value = OAuthTokenResponse(
            access_token='stub-access-token',
            refresh_token=refresh_token,
        )
        state = 'test-state-token'
        request = self._session_request(
            self.url + f"?code=valid_code&user={self.ea.email_host_user}&state={state}",
            session_data={
                OAUTH2_SESSION_KEY: {
                    'state': state,
                    'account_id': self.ea.pk,
                },
            },
        )
        with self.settings(
            MESSAGE_STORAGE=MESSAGE_STORAGE,
            CLIENT_ID='test-client-id',
            CLIENT_SECRET=SENTINEL_SECRET,
            OAUTH2_DATA={
                'smtp.gmail.com': {
                    'accounts_base_url': 'https://accounts.example.com',
                    'token_command': 'o/oauth2/token',
                    'scope': 'https://mail.example.com/',
                },
            },
        ):
            response = get_refresh_token(request)
        self.assertEqual(response.status_code, 302)
        self.ea.refresh_from_db()
        self.assertEqual(self.ea.refresh_token, refresh_token)
        messages = [str(message) for message in get_messages(request)]
        self.assertTrue(any('successfully' in message.lower() for message in messages))
        for message in messages:
            self.assertNotIn(SENTINEL_SECRET, message)
            self.assertNotIn(refresh_token, message)

    @patch("massmail.views.get_oauth2_tokens.exchange_authorization_code")
    @patch("massmail.views.get_oauth2_tokens.report_mail_incident")
    def test_get_refresh_token_exchange_error_is_sanitized(self, mock_report, mock_exchange):
        from sharedkernel.credentials import OAuthTokenExchangeError

        mock_exchange.side_effect = OAuthTokenExchangeError(
            400,
            'invalid_grant',
            account_id=self.ea.pk,
        )
        state = 'test-state-token'
        request = self._session_request(
            self.url + f"?code=valid_code&user={self.ea.email_host_user}&state={state}",
            session_data={
                OAUTH2_SESSION_KEY: {
                    'state': state,
                    'account_id': self.ea.pk,
                },
            },
        )
        with self.settings(
            MESSAGE_STORAGE=MESSAGE_STORAGE,
            CLIENT_ID='test-client-id',
            CLIENT_SECRET=SENTINEL_SECRET,
            OAUTH2_DATA={
                'smtp.gmail.com': {
                    'accounts_base_url': 'https://accounts.example.com',
                    'token_command': 'o/oauth2/token',
                    'scope': 'https://mail.example.com/',
                },
            },
        ):
            response = get_refresh_token(request)
        self.assertEqual(response.status_code, 302)
        self.ea.refresh_from_db()
        self.assertEqual(self.ea.refresh_token, '')
        messages = [str(message) for message in get_messages(request)]
        self.assertTrue(any('failed' in message.lower() for message in messages))
        for message in messages:
            self.assertNotIn(SENTINEL_SECRET, message)
        mock_report.assert_called_once()
        self.assertEqual(len(mail.outbox), 0)

    def test_get_refresh_token_rejects_invalid_state(self):
        request = self._session_request(
            self.url + f"?code=valid_code&user={self.ea.email_host_user}&state=wrong",
            session_data={
                OAUTH2_SESSION_KEY: {
                    'state': 'expected-state',
                    'account_id': self.ea.pk,
                },
            },
        )
        response = get_refresh_token(request)
        self.assertEqual(response.status_code, 403)

    def test_get_refresh_token_success_without_code(self):
        state = 'test-state-token'
        request = self._session_request(
            self.url + f"?user={self.ea.email_host_user}&state={state}",
            session_data={
                OAUTH2_SESSION_KEY: {
                    'state': state,
                    'account_id': self.ea.pk,
                },
            },
        )
        with self.settings(MESSAGE_STORAGE=MESSAGE_STORAGE):
            response = get_refresh_token(request)
        self.assertEqual(response.status_code, 302)
        self.ea.refresh_from_db()
        self.assertEqual(self.ea.refresh_token, '')
