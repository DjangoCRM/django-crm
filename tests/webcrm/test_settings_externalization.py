import importlib
import os
import sys
from unittest import mock

from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from tests.fixtures.settings_env import (
    DEBUG_ENV,
    INCOMPLETE_ENV,
    PRODUCTION_STARTUP_ENV,
    VALID_PRODUCTION_ENV,
)
from webcrm.config import ConfigAccessor


class SettingsExternalizationTests(SimpleTestCase):
    def _reload_settings(self, env: dict[str, str], *, testing: bool = False):
        argv = ['manage.py', 'test'] if testing else ['manage.py', 'runserver']
        with mock.patch.dict(os.environ, env, clear=True):
            with mock.patch.object(sys, 'argv', argv):
                return importlib.reload(importlib.import_module('webcrm.settings'))

    def test_debug_defaults_to_false_when_unset(self):
        settings = self._reload_settings(PRODUCTION_STARTUP_ENV)
        self.assertFalse(settings.DEBUG)

    def test_debug_casts_affirmative_values(self):
        for value in ('true', 'TRUE', '1', 'yes', 'on'):
            with self.subTest(value=value):
                env = {
                    **DEBUG_ENV,
                    'DJANGO_DEBUG': value,
                }
                settings = self._reload_settings(env)
                self.assertTrue(settings.DEBUG)

    def test_debug_casts_rejected_values_to_false(self):
        for value in ('false', 'False', '0', 'no', 'off', ''):
            with self.subTest(value=value):
                env = {
                    **PRODUCTION_STARTUP_ENV,
                    'DJANGO_DEBUG': value,
                }
                settings = self._reload_settings(env)
                self.assertFalse(settings.DEBUG)

    def test_missing_secret_key_aborts_outside_test_runner(self):
        with self.assertRaises(ImproperlyConfigured) as ctx:
            self._reload_settings(INCOMPLETE_ENV, testing=False)
        self.assertIn('DJANGO_SECRET_KEY', str(ctx.exception))

    def test_test_runner_uses_ephemeral_secret_key(self):
        settings = self._reload_settings({}, testing=True)
        self.assertTrue(settings.SECRET_KEY)

    def test_allowed_hosts_parses_comma_separated_values(self):
        env = {
            **PRODUCTION_STARTUP_ENV,
            'DJANGO_ALLOWED_HOSTS': ' localhost ,127.0.0.1, ,crm.example.com',
        }
        settings = self._reload_settings(env)
        self.assertEqual(
            settings.ALLOWED_HOSTS,
            ['localhost', '127.0.0.1', 'crm.example.com'],
        )

    def test_production_like_environment_hardens_security_flags(self):
        settings = self._reload_settings(VALID_PRODUCTION_ENV)
        self.assertFalse(settings.DEBUG)
        self.assertTrue(settings.SECURE_SSL_REDIRECT)
        self.assertTrue(settings.SESSION_COOKIE_SECURE)
        self.assertTrue(settings.CSRF_COOKIE_SECURE)
        self.assertEqual(settings.SECURE_HSTS_SECONDS, 31536000)

    def test_debug_environment_relaxes_security_flags(self):
        settings = self._reload_settings(DEBUG_ENV)
        self.assertTrue(settings.DEBUG)
        self.assertFalse(settings.SECURE_SSL_REDIRECT)
        self.assertFalse(settings.SESSION_COOKIE_SECURE)
        self.assertFalse(settings.CSRF_COOKIE_SECURE)
        self.assertEqual(settings.SECURE_HSTS_SECONDS, 0)

    def test_config_accessor_casts_for_host_lists(self):
        accessor = ConfigAccessor()
        with mock.patch.dict(
            os.environ,
            {'DJANGO_ALLOWED_HOSTS': 'one.example.com,two.example.com'},
            clear=True,
        ):
            self.assertEqual(
                accessor.get_list('DJANGO_ALLOWED_HOSTS'),
                ['one.example.com', 'two.example.com'],
            )


class SettingsIntegrationTests(SimpleTestCase):
    def test_settings_import_succeeds_under_test_runner(self):
        import webcrm.settings  # noqa: F401

    def test_manage_check_succeeds_under_test_runner(self):
        from django.core.management import call_command

        call_command('check')
