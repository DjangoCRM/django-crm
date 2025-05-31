import json
import requests
from random import random
from unittest.mock import patch, MagicMock
from django.contrib.messages.storage import default_storage
from django.test import Client, RequestFactory
from django.urls import reverse

from common.utils.helpers import USER_MODEL
from massmail.models.email_account import EmailAccount
from massmail.views.get_oauth2_tokens import request_authorization_code, get_refresh_token
from tests.base_test_classes import BaseTestCase

MESSAGE_STORAGE='django.contrib.messages.storage.cookie.CookieStorage'


class GetOauth2TokensTestCase(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.owner = USER_MODEL.objects.get(username="Andrew.Manager.Global")
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

    def test_request_authorization_code(self):
        url = reverse("request_authorization_code", args=(self.ea.id,))
        request = self.factory.get(url)
        request.user = self.owner
        response = request_authorization_code(request, self.ea.id)
        self.assertEqual(response.status_code, 302)

    def test_request_authorization_code_no_data(self):
        url = reverse("request_authorization_code", args=(self.ea.id,))
        request = self.factory.get(url)
        request.user = self.owner
        with self.settings(OAUTH2_DATA={}, MESSAGE_STORAGE=MESSAGE_STORAGE):
            request._messages = default_storage(request)
            response = request_authorization_code(request, self.ea.id)
        self.assertEqual(response.status_code, 302)

    @patch("massmail.views.get_oauth2_tokens.requests.post")
    def test_get_refresh_token_success_success(self, mock_post):
        refresh_token = str(random())
        mock_token = {"refresh_token": refresh_token}
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.text = json.dumps(mock_token)
        mock_post.return_value = mock_response
        self.get_test('valid_code', refresh_token)

    @patch("massmail.views.get_oauth2_tokens.requests.post")
    def test_get_refresh_token_success_error(self, mock_post):
        error_msg = "invalid credentials"
        mock_token = {"error": error_msg}
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 302
        mock_response.text = json.dumps(mock_token)
        mock_post.return_value = mock_response
        self.get_test('valid_code','')

    def test_get_refresh_token_success_without_code(self):
        self.get_test('', '')

    def get_test(self, code, refresh_token):
        request = self.factory.get(self.url + f"?code={code}&user={self.ea.email_host_user}")
        with self.settings(MESSAGE_STORAGE=MESSAGE_STORAGE):
            request._messages = default_storage(request)
            response = get_refresh_token(request)
        self.assertEqual(response.status_code, 302)
        self.ea.refresh_from_db()
        self.assertEqual(self.ea.refresh_token, refresh_token)
