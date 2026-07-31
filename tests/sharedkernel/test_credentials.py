"""Unit and integration tests for sharedkernel CredentialAccessor."""

from __future__ import annotations

import logging
from types import SimpleNamespace
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.test import SimpleTestCase, tag

from massmail.models import EmailAccount
from sharedkernel.credentials import (
    AUTH_MECHANISM_OAUTH2,
    AUTH_MECHANISM_PASSWORD,
    CREDENTIAL_MASK,
    SECRET_FIELD_NAMES,
    AuthKind,
    CredentialAccessor,
    ImapCredentials,
    MissingMailCredentialError,
    SmtpCredentials,
    mask_secret,
    resolve_for_user,
)
from tests.base_test_classes import BaseTestCase
from tests.fixtures.email_account_credentials import (
    app_password_account,
    host_password_account,
    no_credential_account,
    oauth2_account,
)


class CredentialAccessorUnitTests(SimpleTestCase):
    def test_secret_field_names_constant(self):
        self.assertEqual(
            SECRET_FIELD_NAMES,
            (
                'email_host_password',
                'email_app_password',
                'refresh_token',
                'email_imail_ssl_keyfile',
            ),
        )

    def test_mask_secret_redacts_non_empty_values(self):
        self.assertEqual(mask_secret('secret-value'), CREDENTIAL_MASK)
        self.assertEqual(mask_secret(''), '')

    def test_app_password_precedence_for_imap(self):
        account = app_password_account()
        credentials = CredentialAccessor.get_imap_credentials(account)
        self.assertEqual(credentials.password, 'app-secret')
        self.assertEqual(credentials.host, 'imap.example.com')
        self.assertEqual(credentials.user, 'app-user@example.com')

    def test_host_password_fallback_for_smtp(self):
        account = host_password_account()
        credentials = CredentialAccessor.get_smtp_credentials(account)
        self.assertEqual(credentials.password, 'host-only-secret')
        self.assertEqual(credentials.auth_mechanism, AUTH_MECHANISM_PASSWORD)

    def test_missing_credentials_raise_named_error_without_secret(self):
        account = no_credential_account()
        with self.assertRaises(MissingMailCredentialError) as ctx:
            CredentialAccessor.get_imap_credentials(account)
        self.assertEqual(ctx.exception.account_id, 3)
        self.assertEqual(ctx.exception.field_name, 'email_host_password')
        self.assertNotIn('host-only-secret', str(ctx.exception))
        self.assertNotIn(CREDENTIAL_MASK, str(ctx.exception))

    def test_oauth_account_returns_oauth_auth_mechanism(self):
        account = oauth2_account()
        credentials = CredentialAccessor.get_smtp_credentials(account)
        self.assertEqual(credentials.auth_mechanism, AUTH_MECHANISM_OAUTH2)
        self.assertEqual(credentials.password, 'oauth-refresh-token-value')

    def test_imap_credentials_mask_repr_and_str(self):
        credentials = ImapCredentials(
            host='imap.example.com',
            port=993,
            user='user@example.com',
            password='super-secret-value',
            use_ssl=True,
            ssl_keyfile='/tmp/key.pem',
        )
        rendered = f'{credentials!r}{credentials!s}'
        self.assertIn(CREDENTIAL_MASK, rendered)
        self.assertNotIn('super-secret-value', rendered)

    def test_smtp_credentials_mask_f_string_interpolation(self):
        credentials = SmtpCredentials(
            host='smtp.example.com',
            port=587,
            user='user@example.com',
            password='smtp-secret',
            use_tls=True,
            auth_mechanism=AUTH_MECHANISM_PASSWORD,
        )
        rendered = f'credential={credentials}'
        self.assertIn(CREDENTIAL_MASK, rendered)
        self.assertNotIn('smtp-secret', rendered)

    def test_whitespace_password_is_preserved(self):
        account = host_password_account(email_host_password=' spaced secret ')
        credentials = CredentialAccessor.get_imap_credentials(account)
        self.assertEqual(credentials.password, ' spaced secret ')

    def test_structured_log_masks_secret(self):
        account = app_password_account()
        with self.assertLogs('sharedkernel.credentials', level='INFO') as logs:
            CredentialAccessor.get_imap_credentials(account)
        log_output = '\n'.join(logs.output)
        self.assertIn(CREDENTIAL_MASK, log_output)
        self.assertNotIn('app-secret', log_output)

    def test_logging_info_of_credentials_never_leaks_secret(self):
        credentials = SmtpCredentials(
            host='smtp.example.com',
            port=587,
            user='user@example.com',
            password='logging-secret',
            use_tls=True,
            auth_mechanism=AUTH_MECHANISM_PASSWORD,
        )
        with self.assertLogs('sharedkernel.credentials', level='INFO') as logs:
            logging.getLogger('sharedkernel.credentials').info('probe %s', credentials)
        self.assertNotIn('logging-secret', '\n'.join(logs.output))

    def test_resolve_for_user_allows_owner(self):
        user = SimpleNamespace(pk=10, is_superuser=False)
        account = app_password_account(owner_id=10)
        self.assertIs(resolve_for_user(user, account), account)

    def test_resolve_for_user_allows_co_owner(self):
        user = SimpleNamespace(pk=99, is_superuser=False)
        account = app_password_account(owner_id=10, co_owner_id=99)
        self.assertIs(resolve_for_user(user, account), account)

    def test_resolve_for_user_allows_superuser(self):
        user = SimpleNamespace(pk=1, is_superuser=True)
        account = app_password_account(owner_id=10)
        self.assertIs(resolve_for_user(user, account), account)

    def test_resolve_for_user_denies_other_users(self):
        user = SimpleNamespace(pk=55, is_superuser=False)
        account = app_password_account(owner_id=10, co_owner_id=99)
        with self.assertRaises(PermissionDenied):
            resolve_for_user(user, account)

    def test_legacy_mailbox_credential_wrapper_still_masks(self):
        account = app_password_account()
        credential = CredentialAccessor.for_imap(account)
        self.assertEqual(credential.secret, 'app-secret')
        self.assertEqual(credential.auth_kind, AuthKind.PASSWORD)
        self.assertNotIn('app-secret', repr(credential))


@tag('TestCase')
class CredentialAccessorFixtureIntegrationTests(BaseTestCase):
    fixtures = BaseTestCase.fixtures + ('email_account.json',)

    def test_fixture_account_resolves_app_password_without_log_leak(self):
        account = EmailAccount.objects.get(pk=9001)
        with self.assertLogs('sharedkernel.credentials', level='INFO') as logs:
            credentials = CredentialAccessor.get_smtp_credentials(account)
        self.assertEqual(credentials.password, 'placeholder-app-password')
        self.assertEqual(credentials.host, 'smtp.example.com')
        self.assertEqual(credentials.port, 587)
        log_output = '\n'.join(logs.output)
        self.assertNotIn('placeholder-app-password', log_output)
        self.assertNotIn('placeholder-host-password', log_output)

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        user_model = get_user_model()
        cls.owner, _ = user_model.objects.get_or_create(
            username='credential_fixture_owner',
            defaults={'email': 'credential_fixture_owner@example.com'},
        )

    def test_persisted_account_matches_database_values(self):
        account = EmailAccount.objects.create(
            name='Inline Credential Account',
            email_host='smtp.example.com',
            imap_host='imap.example.com',
            email_port=465,
            email_host_user='inline-user@example.com',
            email_host_password='db-host-password',
            email_app_password='db-app-password',
            from_email='inline-user@example.com',
            owner=self.owner,
        )
        credentials = CredentialAccessor.get_imap_credentials(account)
        self.assertEqual(credentials.password, 'db-app-password')
        self.assertEqual(credentials.user, account.email_host_user)
