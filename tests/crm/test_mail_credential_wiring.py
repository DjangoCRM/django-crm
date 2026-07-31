"""Characterization and wiring tests for mail credential accessor call sites."""

from __future__ import annotations

import ast
import queue
from pathlib import Path
from unittest import mock

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import SimpleTestCase, override_settings, tag

from crm.utils.crm_imap import CrmIMAP
from crm.utils.import_emails import ImportEmails
from crm.utils.manage_imaps import CrmImapManager
from massmail.models import EmailAccount
from massmail.utils.email_creators import email_connection
from sharedkernel.credentials import (
    AUTH_MECHANISM_OAUTH2,
    AUTH_MECHANISM_PASSWORD,
    CredentialAccessor,
    MissingMailCredentialError,
)
from tests.base_test_classes import BaseTestCase
from tests.doubles.fake_imap import FakeIMAP4SSL
from tests.fixtures.email_account_credentials import (
    app_password_account,
    host_password_account,
    oauth2_account,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CALL_SITE_FILES = (
    PROJECT_ROOT / 'crm/utils/crm_imap.py',
    PROJECT_ROOT / 'crm/utils/manage_imaps.py',
    PROJECT_ROOT / 'crm/utils/send_email.py',
    PROJECT_ROOT / 'crm/utils/import_emails.py',
    PROJECT_ROOT / 'massmail/utils/email_creators.py',
    PROJECT_ROOT / 'massmail/utils/sendmassmail.py',
    PROJECT_ROOT / 'massmail/backends/smtp.py',
)
FORBIDDEN_CREDENTIAL_ATTRS = frozenset({
    'email_app_password',
    'email_host_password',
    'refresh_token',
    'email_imail_ssl_keyfile',
})


class MailCredentialStaticWiringTests(SimpleTestCase):
    def test_call_sites_do_not_read_credential_columns_directly(self):
        for path in CALL_SITE_FILES:
            tree = ast.parse(path.read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                    if node.value.id in {'ea', 'email_account', 'eac'} and node.attr in FORBIDDEN_CREDENTIAL_ATTRS:
                        self.fail(f'{path} reads {node.value.id}.{node.attr} directly')
                if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Attribute):
                    if (
                        isinstance(node.value.value, ast.Name)
                        and node.value.value.id == 'self'
                        and node.value.attr == 'ea'
                        and node.attr in FORBIDDEN_CREDENTIAL_ATTRS
                    ):
                        self.fail(f'{path} reads self.ea.{node.attr} directly')


class MailCredentialCharacterizationTests(SimpleTestCase):
    def test_password_account_imap_login_parameters(self):
        account = app_password_account()
        expected = (
            CredentialAccessor.get_imap_credentials(account).user,
            CredentialAccessor.get_imap_credentials(account).password,
        )
        FakeIMAP4SSL.reset()
        with mock.patch('crm.utils.crm_imap.imaplib.IMAP4_SSL', FakeIMAP4SSL):
            crmimap = CrmIMAP(account.email_host_user)
            crmimap.ea = account
            crmimap.error = None
            crmimap.connection = FakeIMAP4SSL('imap.example.com')
            crmimap._log_in()
        self.assertEqual(FakeIMAP4SSL.login_calls, [expected])

    def test_host_password_account_smtp_connection_parameters(self):
        account = host_password_account()
        with mock.patch('massmail.utils.email_creators.mail.get_connection') as mock_get:
            connection = mock.Mock()
            mock_get.return_value = connection
            email_connection(account)
        credentials = CredentialAccessor.get_smtp_credentials(account)
        self.assertEqual(connection.username, credentials.user)
        self.assertEqual(connection.password, credentials.password)
        self.assertEqual(connection.host, credentials.host)
        self.assertEqual(connection.port, credentials.port)
        self.assertEqual(connection.use_tls, credentials.use_tls)

    def test_oauth_account_builds_oauth_backend_from_smtp_credentials(self):
        account = oauth2_account()
        with mock.patch('massmail.utils.email_creators.OAuth2EmailBackend') as mock_backend:
            backend = mock.Mock()
            mock_backend.from_smtp_credentials.return_value = backend
            result = email_connection(account)
        credentials = CredentialAccessor.get_smtp_credentials(account)
        mock_backend.from_smtp_credentials.assert_called_once_with(
            credentials,
            email_account=account,
        )
        self.assertIs(result, backend)
        self.assertEqual(credentials.auth_mechanism, AUTH_MECHANISM_OAUTH2)


@tag('TestCase')
class MailCredentialPoolWiringTests(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        user_model = get_user_model()
        cls.owner, _ = user_model.objects.get_or_create(
            username='credential_pool_owner',
            defaults={'email': 'credential_pool_owner@example.com'},
        )

    def setUp(self):
        self.manager = CrmImapManager(queue.Queue())

    @mock.patch('crm.utils.manage_imaps.CrmIMAP')
    @override_settings(REUSE_IMAP_CONNECTION=True)
    def test_manage_imaps_reuses_pool_entry_for_same_account(self, mock_crmimap_class):
        account = EmailAccount.objects.create(
            name='Pool Account',
            email_host='smtp.example.com',
            imap_host='imap.example.com',
            email_port=993,
            email_host_user='pool-user@example.com',
            email_host_password='host-password',
            email_app_password='app-password',
            from_email='pool-user@example.com',
            owner=self.owner,
        )
        mock_crmimap = mock.Mock()
        mock_crmimap.email_host_user = account.email_host_user
        mock_crmimap.error = False
        mock_crmimap.boxes = {'INBOX': {'name on server': 'INBOX'}}
        mock_crmimap_class.return_value = mock_crmimap

        first = self.manager._create_crmimap(account)
        second = self.manager._create_crmimap(account)

        self.assertIs(first, second)
        pool_key = CredentialAccessor.get_imap_credentials(account).user
        self.assertIn(pool_key, self.manager.crmimap_storage)

    @mock.patch('crm.utils.manage_imaps.CrmIMAP')
    @override_settings(REUSE_IMAP_CONNECTION=True)
    def test_manage_imaps_creates_distinct_pool_entries_for_distinct_accounts(
        self,
        mock_crmimap_class,
    ):
        first_account = EmailAccount.objects.create(
            name='Pool Account A',
            email_host='smtp.example.com',
            imap_host='imap.example.com',
            email_port=993,
            email_host_user='pool-a@example.com',
            email_host_password='host-password',
            email_app_password='app-password',
            from_email='pool-a@example.com',
            owner=self.owner,
        )
        second_account = EmailAccount.objects.create(
            name='Pool Account B',
            email_host='smtp.example.com',
            imap_host='imap.example.com',
            email_port=993,
            email_host_user='pool-b@example.com',
            email_host_password='host-password',
            email_app_password='app-password',
            from_email='pool-b@example.com',
            owner=self.owner,
        )

        def _make_mock(user: str):
            mock_crmimap = mock.Mock()
            mock_crmimap.email_host_user = user
            mock_crmimap.error = False
            mock_crmimap.boxes = {'INBOX': {'name on server': 'INBOX'}}
            return mock_crmimap

        mock_crmimap_class.side_effect = [
            _make_mock(first_account.email_host_user),
            _make_mock(second_account.email_host_user),
        ]

        first = self.manager._create_crmimap(first_account)
        second = self.manager._create_crmimap(second_account)

        self.assertIsNot(first, second)
        self.assertEqual(len(self.manager.crmimap_storage), 2)

    def test_import_emails_skips_queue_when_pool_key_already_present(self):
        account = EmailAccount.objects.create(
            name='Import Pool Account',
            email_host='smtp.example.com',
            imap_host='imap.example.com',
            email_port=993,
            email_host_user='import-user@example.com',
            email_host_password='host-password',
            email_app_password='app-password',
            from_email='import-user@example.com',
            do_import=True,
            owner=self.owner,
        )
        pool_key = CredentialAccessor.get_imap_credentials(account).user
        with mock.patch('crm.utils.import_emails.app_config') as mock_config:
            mock_config.mci.crmimap_storage = {pool_key: mock.Mock()}
            importer = ImportEmails(queue.Queue(), queue.Queue())
            with mock.patch.object(importer.ea_queue, 'put') as mock_put:
                with override_settings(REUSE_IMAP_CONNECTION=True):
                    importer.send(self.owner)
        mock_put.assert_not_called()

    def test_import_emails_queues_when_pool_key_missing(self):
        account = EmailAccount.objects.create(
            name='Import Queue Account',
            email_host='smtp.example.com',
            imap_host='imap.example.com',
            email_port=993,
            email_host_user='import-queue@example.com',
            email_host_password='host-password',
            email_app_password='app-password',
            from_email='import-queue@example.com',
            do_import=True,
            owner=self.owner,
        )
        with mock.patch('crm.utils.import_emails.app_config') as mock_config:
            mock_config.mci.crmimap_storage = {}
            importer = ImportEmails(queue.Queue(), queue.Queue())
            with mock.patch.object(importer.ea_queue, 'put') as mock_put:
                with override_settings(REUSE_IMAP_CONNECTION=True):
                    importer.send(self.owner)
        mock_put.assert_called_once_with(account)


@tag('TestCase')
class MailCredentialNegativePathTests(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        user_model = get_user_model()
        cls.owner, _ = user_model.objects.get_or_create(
            username='credential_negative_owner',
            defaults={'email': 'credential_negative_owner@example.com'},
        )

    @mock.patch('crm.utils.crm_imap.report_mail_incident')
    def test_missing_imap_credentials_skip_login(self, mock_report):
        account = EmailAccount.objects.create(
            name='Missing IMAP Account',
            email_host='smtp.example.com',
            imap_host='imap.example.com',
            email_port=993,
            email_host_user='missing-imap@example.com',
            email_host_password='',
            email_app_password='',
            refresh_token='',
            from_email='missing-imap@example.com',
            owner=self.owner,
        )
        FakeIMAP4SSL.reset()
        crmimap = CrmIMAP(account.email_host_user)
        crmimap.ea = account
        crmimap.error = None
        crmimap.connection = FakeIMAP4SSL('imap.example.com')
        crmimap._log_in()
        self.assertEqual(FakeIMAP4SSL.login_calls, [])
        self.assertIsInstance(crmimap.error, MissingMailCredentialError)
        mock_report.assert_called_once()

    @mock.patch('crm.utils.manage_imaps.report_mail_incident')
    def test_manage_imaps_returns_none_without_login_attempt(self, mock_report):
        account = EmailAccount.objects.create(
            name='Missing Pool Account',
            email_host='smtp.example.com',
            imap_host='imap.example.com',
            email_port=993,
            email_host_user='missing-pool@example.com',
            email_host_password='',
            email_app_password='',
            refresh_token='',
            from_email='missing-pool@example.com',
            owner=self.owner,
        )
        manager = CrmImapManager(queue.Queue())
        with mock.patch('crm.utils.manage_imaps.CrmIMAP') as mock_crmimap_class:
            result = manager._create_crmimap(account)
        self.assertIsNone(result)
        mock_crmimap_class.assert_not_called()
        mock_report.assert_called_once()


@tag('TestCase')
class MailCredentialServiceBoundaryTests(BaseTestCase):
    fixtures = BaseTestCase.fixtures + ('email_account.json',)

    @mock.patch('crm.utils.crm_imap.imaplib.IMAP4_SSL', FakeIMAP4SSL)
    def test_inbound_imap_login_succeeds_through_accessor(self):
        account = EmailAccount.objects.get(pk=9001)
        FakeIMAP4SSL.reset()
        crmimap = CrmIMAP(account.email_host_user)
        crmimap.ea = account
        crmimap.error = None
        crmimap.connection = FakeIMAP4SSL('imap.example.com')
        crmimap._log_in()
        self.assertEqual(
            FakeIMAP4SSL.login_calls,
            [(account.email_host_user, 'placeholder-app-password')],
        )

    def test_outbound_smtp_send_uses_accessor_backed_connection(self):
        account = EmailAccount.objects.get(pk=9001)
        with mock.patch('massmail.utils.email_creators.mail.get_connection') as mock_get:
            connection = mock.Mock()
            mock_get.return_value = connection
            email_connection(account)
        credentials = CredentialAccessor.get_smtp_credentials(account)
        self.assertEqual(connection.username, credentials.user)
        self.assertEqual(connection.password, credentials.password)
        self.assertEqual(connection.host, credentials.host)
        self.assertEqual(credentials.auth_mechanism, AUTH_MECHANISM_PASSWORD)

    def test_outbound_send_fails_fast_when_credentials_missing(self):
        account = EmailAccount.objects.create(
            name='Missing SMTP Account',
            email_host='smtp.example.com',
            email_port=587,
            email_host_user='missing-smtp@example.com',
            email_host_password='',
            email_app_password='',
            refresh_token='',
            from_email='missing-smtp@example.com',
            owner=EmailAccount.objects.get(pk=9001).owner,
        )
        with self.assertRaises(MissingMailCredentialError):
            email_connection(account)
