import importlib
import logging
import os
import sys
from unittest import mock

from django.core.exceptions import ImproperlyConfigured
from django.core import mail
from django.core.mail import mail_admins, send_mail
from django.test import SimpleTestCase, override_settings

from tests.fixtures.mail_env import (
    CHARACTERIZATION_MAIL_ENV,
    COMPLETE_MAIL_ENV,
    DEBUG_NO_MAIL_ENV,
    INCOMPLETE_MAIL_ENV,
    LOC_MEM_MAIL_ENV,
)
from webcrm.config import SECRET_MASK, ConfigAccessor
from webcrm.mail_config import parse_admin_recipients


class MailSettingsCharacterizationTests(SimpleTestCase):
    def _reload_settings(self, env: dict[str, str], *, testing: bool = False):
        argv = ['manage.py', 'test'] if testing else ['manage.py', 'runserver']
        with mock.patch.dict(os.environ, env, clear=True):
            with mock.patch.object(sys, 'argv', argv):
                return importlib.reload(importlib.import_module('webcrm.settings'))

    def test_characterization_defaults_match_prior_literals(self):
        settings = self._reload_settings(CHARACTERIZATION_MAIL_ENV)
        self.assertEqual(settings.EMAIL_PORT, 587)
        self.assertTrue(settings.EMAIL_USE_TLS)
        self.assertFalse(settings.EMAIL_USE_SSL)
        self.assertEqual(settings.DEFAULT_FROM_EMAIL, 'test@example.com')
        self.assertEqual(settings.SERVER_EMAIL, 'test@example.com')
        self.assertEqual(
            settings.ADMINS,
            [('Admin1', 'admin1_box@example.com')],
        )


class ParseAdminRecipientsTests(SimpleTestCase):
    def test_single_entry(self):
        self.assertEqual(
            parse_admin_recipients('Admin1 <admin1@example.com>', 'DJANGO_ADMINS'),
            [('Admin1', 'admin1@example.com')],
        )

    def test_multiple_entries_with_whitespace(self):
        value = ' Admin One <one@example.com> , Admin Two <two@example.com> '
        self.assertEqual(
            parse_admin_recipients(value, 'DJANGO_ADMINS'),
            [
                ('Admin One', 'one@example.com'),
                ('Admin Two', 'two@example.com'),
            ],
        )

    def test_empty_value_returns_empty_list(self):
        self.assertEqual(parse_admin_recipients('', 'DJANGO_ADMINS'), [])

    def test_malformed_entry_raises_with_index(self):
        with self.assertRaises(ImproperlyConfigured) as ctx:
            parse_admin_recipients('not-an-email', 'DJANGO_ADMINS')
        message = str(ctx.exception)
        self.assertIn('DJANGO_ADMINS', message)
        self.assertIn('position 1', message)

    def test_missing_at_sign_raises_with_index(self):
        with self.assertRaises(ImproperlyConfigured) as ctx:
            parse_admin_recipients('Admin <invalid-address>', 'DJANGO_ADMINS')
        message = str(ctx.exception)
        self.assertIn('DJANGO_ADMINS', message)
        self.assertIn('position 1', message)


class MailConfigUnitTests(SimpleTestCase):
    def _reload_settings(self, env: dict[str, str], *, testing: bool = False):
        argv = ['manage.py', 'test'] if testing else ['manage.py', 'runserver']
        with mock.patch.dict(os.environ, env, clear=True):
            with mock.patch.object(sys, 'argv', argv):
                return importlib.reload(importlib.import_module('webcrm.settings'))

    def test_debug_without_mail_host_uses_console_backend(self):
        settings = self._reload_settings(DEBUG_NO_MAIL_ENV)
        self.assertEqual(
            settings.EMAIL_BACKEND,
            'django.core.mail.backends.console.EmailBackend',
        )

    def test_production_without_mail_host_raises(self):
        env = {
            'DJANGO_SECRET_KEY': 'test-mail-secret-key-not-for-production-use',
            'DJANGO_DEBUG': 'false',
            'DJANGO_ALLOWED_HOSTS': 'crm.example.com',
            'DJANGO_DB_ENGINE': 'sqlite3',
            'DJANGO_DB_NAME': ':memory:',
        }
        with self.assertRaises(ImproperlyConfigured) as ctx:
            self._reload_settings(env)
        self.assertIn('EMAIL_HOST', str(ctx.exception))

    def test_incomplete_mail_configuration_lists_missing_variables(self):
        with self.assertRaises(ImproperlyConfigured) as ctx:
            self._reload_settings(INCOMPLETE_MAIL_ENV)
        message = str(ctx.exception)
        self.assertIn('Incomplete mail configuration', message)
        self.assertIn('EMAIL_HOST_USER', message)
        self.assertIn('EMAIL_HOST_PASSWORD', message)

    def test_tls_and_ssl_both_enabled_raises(self):
        env = {
            **COMPLETE_MAIL_ENV,
            'EMAIL_USE_TLS': 'true',
            'EMAIL_USE_SSL': 'true',
        }
        with self.assertRaises(ImproperlyConfigured) as ctx:
            self._reload_settings(env)
        self.assertIn('mutually exclusive', str(ctx.exception))

    def test_non_numeric_email_port_raises(self):
        env = {**COMPLETE_MAIL_ENV, 'EMAIL_PORT': 'not-a-number'}
        with self.assertRaises(ImproperlyConfigured) as ctx:
            self._reload_settings(env)
        self.assertIn('EMAIL_PORT', str(ctx.exception))

    def test_mail_password_is_masked_in_diagnostics(self):
        accessor = ConfigAccessor()
        accessor.register_secret('EMAIL_HOST_PASSWORD')
        with mock.patch.dict(
            os.environ,
            {'EMAIL_HOST_PASSWORD': 'super-secret-mail-password'},
            clear=True,
        ):
            accessor.get('EMAIL_HOST_PASSWORD', secret=True)
            diagnostics = accessor.diagnostics()
        self.assertEqual(diagnostics['EMAIL_HOST_PASSWORD'], SECRET_MASK)
        self.assertNotIn('super-secret-mail-password', str(diagnostics))

    def test_mail_password_never_appears_in_logs(self):
        accessor = ConfigAccessor()
        with self.assertLogs('webcrm.config', level='DEBUG') as captured:
            with mock.patch.dict(
                os.environ,
                {'EMAIL_HOST_PASSWORD': 'super-secret-mail-password'},
                clear=True,
            ):
                accessor.get('EMAIL_HOST_PASSWORD', secret=True)
        joined = '\n'.join(captured.output)
        self.assertIn(SECRET_MASK, joined)
        self.assertNotIn('super-secret-mail-password', joined)

    def test_crm_identity_and_oauth_resolve_from_environment(self):
        settings = self._reload_settings(COMPLETE_MAIL_ENV)
        self.assertEqual(settings.CRM_IP, '127.0.0.1')
        self.assertEqual(settings.CRM_HOST, 'my_crm_host_name')
        self.assertEqual(settings.CLIENT_ID, 'placeholder-client-id')
        self.assertEqual(settings.CLIENT_SECRET, 'placeholder-client-secret')


class MailSettingsIntegrationTests(SimpleTestCase):
    def _reload_settings(self, env: dict[str, str]):
        with mock.patch.dict(os.environ, env, clear=True):
            with mock.patch.object(sys, 'argv', ['manage.py', 'runserver']):
                return importlib.reload(importlib.import_module('webcrm.settings'))

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    )
    def test_send_mail_uses_environment_from_and_admin_recipients(self):
        settings = self._reload_settings(LOC_MEM_MAIL_ENV)
        with self.settings(
            DEFAULT_FROM_EMAIL=settings.DEFAULT_FROM_EMAIL,
            ADMINS=settings.ADMINS,
            SERVER_EMAIL=settings.SERVER_EMAIL,
        ):
            send_mail(
                subject='Integration test',
                message='Body',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['external@example.com'],
            )
            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(mail.outbox[0].from_email, 'noreply@example.com')

            mail_admins('Admin alert', 'Something happened')
            self.assertEqual(len(mail.outbox), 2)
            self.assertEqual(
                sorted(mail.outbox[1].to),
                ['admin@example.com', 'ops@example.com'],
            )

    def test_partial_mail_configuration_surfaces_actionable_error(self):
        with self.assertRaises(ImproperlyConfigured) as ctx:
            self._reload_settings(INCOMPLETE_MAIL_ENV)
        message = str(ctx.exception)
        self.assertIn('EMAIL_HOST_USER', message)
        self.assertNotIn('placeholder-mail-password', message)

    def test_empty_admins_in_production_logs_warning(self):
        env = {**COMPLETE_MAIL_ENV}
        env.pop('DJANGO_ADMINS', None)
        with self.assertLogs('webcrm.mail_config', level='WARNING') as captured:
            with mock.patch.dict(os.environ, env, clear=True):
                with mock.patch.object(sys, 'argv', ['manage.py', 'runserver']):
                    importlib.reload(importlib.import_module('webcrm.settings'))
        self.assertTrue(any('DJANGO_ADMINS' in line for line in captured.output))
