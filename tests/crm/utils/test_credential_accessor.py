"""Tests for sharedkernel CredentialAccessor and call-site integration."""

from __future__ import annotations

import ast
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, tag, override_settings

from crm.utils.crm_imap import CrmIMAP
from crm.utils.manage_imaps import CrmImapManager
from crm.utils.send_email import send_email
from massmail.models import EmailAccount
from massmail.utils.email_creators import email_connection
from sharedkernel.credentials import (
    CREDENTIAL_MASK,
    AuthKind,
    CredentialAccessor,
    MailboxCredential,
    MissingMailCredentialError,
)
from tests.base_test_classes import BaseTestCase
from tests.fixtures.email_account_credentials import (
    app_password_account,
    host_password_account,
    no_credential_account,
    oauth2_account,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CALL_SITE_FILES = (
    PROJECT_ROOT / 'crm/utils/crm_imap.py',
    PROJECT_ROOT / 'crm/utils/manage_imaps.py',
    PROJECT_ROOT / 'crm/utils/send_email.py',
    PROJECT_ROOT / 'crm/utils/import_emails.py',
    PROJECT_ROOT / 'massmail/utils/email_creators.py',
    PROJECT_ROOT / 'massmail/utils/sendmassmail.py',
    PROJECT_ROOT / 'massmail/backends/smtp.py',
)


class CredentialAccessorUnitTests(SimpleTestCase):
    def test_app_password_precedence(self):
        account = app_password_account()
        credential = CredentialAccessor.for_imap(account)
        self.assertEqual(credential.secret, 'app-secret')
        self.assertEqual(credential.auth_kind, AuthKind.PASSWORD)

    def test_host_password_fallback(self):
        account = host_password_account()
        credential = CredentialAccessor.for_smtp(account)
        self.assertEqual(credential.secret, 'host-only-secret')
        self.assertEqual(credential.auth_kind, AuthKind.PASSWORD)

    def test_missing_credential_raises_named_error(self):
        account = no_credential_account()
        with self.assertRaises(MissingMailCredentialError) as ctx:
            CredentialAccessor.for_imap(account)
        self.assertEqual(ctx.exception.account_id, 3)

    def test_oauth2_account_returns_token_auth_kind(self):
        account = oauth2_account()
        credential = CredentialAccessor.for_smtp(account)
        self.assertEqual(credential.auth_kind, AuthKind.OAUTH2)
        self.assertEqual(credential.secret, 'oauth-refresh-token-value')

    def test_credential_masks_repr_and_str(self):
        credential = MailboxCredential(
            user='user@example.com',
            host='imap.example.com',
            auth_kind=AuthKind.PASSWORD,
            _secret='super-secret-value',
        )
        rendered = f'{credential!r}{credential!s}'
        self.assertIn(CREDENTIAL_MASK, rendered)
        self.assertNotIn('super-secret-value', rendered)

    def test_whitespace_password_is_preserved(self):
        account = host_password_account(email_host_password=' spaced secret ')
        credential = CredentialAccessor.for_imap(account)
        self.assertEqual(credential.secret, ' spaced secret ')

    def test_structured_log_masks_secret(self):
        account = app_password_account()
        with self.assertLogs('sharedkernel.credentials', level='INFO') as logs:
            CredentialAccessor.for_imap(account)
        log_output = '\n'.join(logs.output)
        self.assertIn(CREDENTIAL_MASK, log_output)
        self.assertNotIn('app-secret', log_output)


class CredentialCallSiteStaticTests(SimpleTestCase):
    def test_call_sites_do_not_read_password_fields_directly(self):
        forbidden = {'email_app_password', 'email_host_password', 'refresh_token'}
        for path in CALL_SITE_FILES:
            tree = ast.parse(path.read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                    if node.value.id == 'email_account' and node.attr in forbidden:
                        self.fail(f'{path} reads email_account.{node.attr} directly')
                if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Attribute):
                    if (
                        isinstance(node.value.value, ast.Name)
                        and node.value.value.id == 'self'
                        and node.value.attr == 'ea'
                        and node.attr in forbidden
                    ):
                        self.fail(f'{path} reads self.ea.{node.attr} directly')


@tag('TestCase')
class CrmImapCredentialIntegrationTests(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        user_model = get_user_model()
        cls.owner, _ = user_model.objects.get_or_create(
            username='credential_imap_owner',
            defaults={'email': 'credential_imap_owner@example.com'},
        )

    def setUp(self):
        self.email_account = EmailAccount.objects.create(
            name='Credential IMAP Account',
            email_host='smtp.example.com',
            imap_host='imap.example.com',
            email_port=993,
            email_host_user='imap-user@example.com',
            email_host_password='host-password',
            email_app_password='app-password',
            from_email='imap-user@example.com',
            owner=self.owner,
        )
        self.crmimap = CrmIMAP(self.email_account.email_host_user)
        self.crmimap.ea = self.email_account
        self.crmimap.error = None

    @mock.patch('crm.utils.crm_imap.CrmIMAP._execute')
    def test_login_uses_app_password_precedence(self, mock_execute):
        mock_execute.return_value = ('OK', None, None)
        self.crmimap.connection = mock.Mock()
        self.crmimap._log_in()
        params = mock_execute.call_args[0][1]
        self.assertEqual(params[1], 'app-password')

    @mock.patch('crm.utils.crm_imap.report_mail_incident')
    def test_missing_credential_skips_transport_login(self, mock_report):
        self.crmimap.ea.email_app_password = ''
        self.crmimap.ea.email_host_password = ''
        self.crmimap.ea.refresh_token = ''
        self.crmimap._log_in()
        self.assertIsInstance(self.crmimap.error, MissingMailCredentialError)
        mock_report.assert_called_once()
        self.assertEqual(mock_report.call_args.kwargs['operation'], 'imap_login')


@tag('TestCase')
class ManageImapsCredentialIntegrationTests(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        user_model = get_user_model()
        cls.owner, _ = user_model.objects.get_or_create(
            username='credential_manage_owner',
            defaults={'email': 'credential_manage_owner@example.com'},
        )

    @mock.patch('crm.utils.manage_imaps.report_mail_incident')
    @override_settings(REUSE_IMAP_CONNECTION=True)
    def test_missing_credential_returns_none(self, mock_report):
        account = EmailAccount.objects.create(
            name='Missing Credential Account',
            email_host='smtp.example.com',
            imap_host='imap.example.com',
            email_port=993,
            email_host_user='missing@example.com',
            email_host_password='',
            email_app_password='',
            from_email='missing@example.com',
            owner=self.owner,
        )
        manager = CrmImapManager(mock.Mock())
        result = manager._create_crmimap(account)
        self.assertIsNone(result)
        mock_report.assert_called_once()
        self.assertEqual(mock_report.call_args.kwargs['operation'], 'create_crmimap')


@tag('TestCase')
class SendEmailCredentialIntegrationTests(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        user_model = get_user_model()
        cls.owner, _ = user_model.objects.get_or_create(
            username='credential_send_owner',
            defaults={'email': 'credential_send_owner@example.com'},
        )

    @mock.patch('massmail.utils.email_creators.email_creator')
    def test_missing_credential_surfaces_user_error(self, mock_email_creator):
        EmailAccount.objects.create(
            name='Missing SMTP Account',
            email_host='smtp.example.com',
            email_port=587,
            email_host_user='missing-smtp@example.com',
            email_host_password='',
            email_app_password='',
            from_email='missing-smtp@example.com',
            main=True,
            owner=self.owner,
        )
        crm_email = SimpleNamespace(
            id=1,
            owner=self.owner,
            subject='Subject',
            content='Body',
            to='recipient@example.com',
            cc='',
            bcc='',
            sent=False,
            deal=None,
            save=mock.Mock(),
        )
        request = SimpleNamespace()
        with mock.patch('crm.utils.send_email.messages') as mock_messages:
            send_email(request, crm_email)
        mock_email_creator.assert_not_called()
        mock_messages.error.assert_called_once()


class EmailConnectionStubTests(SimpleTestCase):
    def test_stubbed_smtp_transport_receives_accessor_secret(self):
        account = app_password_account()
        with mock.patch('massmail.utils.email_creators.mail.get_connection') as mock_get:
            connection = mock.Mock()
            mock_get.return_value = connection
            email_connection(account)
        self.assertEqual(connection.password, 'app-secret')
        self.assertEqual(connection.username, 'app-user@example.com')

    def test_oauth2_backend_receives_refresh_token(self):
        account = oauth2_account()
        with mock.patch('massmail.utils.email_creators.OAuth2EmailBackend') as mock_backend:
            backend = mock.Mock()
            mock_backend.from_smtp_credentials.return_value = backend
            email_connection(account)
        credentials = CredentialAccessor.get_smtp_credentials(account)
        mock_backend.from_smtp_credentials.assert_called_once_with(
            credentials,
            email_account=account,
        )
