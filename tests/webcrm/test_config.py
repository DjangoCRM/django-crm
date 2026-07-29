import logging
import os
import sys
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from tests.fixtures.env_helper import FIXTURES_ENV_DIR, temp_secrets_dir, write_secret_file
from webcrm.config import SECRET_MASK, ConfigAccessor, config


@contextmanager
def isolated_environ(values: dict[str, str] | None = None):
    values = values or {}
    with mock.patch.dict(os.environ, values, clear=True):
        yield


class ConfigAccessorTests(SimpleTestCase):
    def setUp(self):
        self.accessor = ConfigAccessor()

    def test_get_returns_string_from_environment(self):
        with isolated_environ({'TEST_STR': 'hello'}):
            self.assertEqual(self.accessor.get('TEST_STR'), 'hello')

    def test_require_raises_for_missing_mandatory_name(self):
        with temp_secrets_dir() as secrets_dir:
            accessor = ConfigAccessor(secrets_dir=secrets_dir)
            with isolated_environ():
                with self.assertRaises(ImproperlyConfigured) as ctx:
                    accessor.require('ZZZ_WO001_MISSING_MANDATORY')
        message = str(ctx.exception)
        self.assertIn('ZZZ_WO001_MISSING_MANDATORY', message)
        self.assertIn('.env.example', message)

    def test_resolution_order_env_over_file_over_default(self):
        with temp_secrets_dir() as secrets_dir:
            write_secret_file(secrets_dir, 'RESOLUTION_TEST', 'from-file')
            accessor = ConfigAccessor(secrets_dir=secrets_dir)

            with isolated_environ():
                self.assertEqual(
                    accessor.get('RESOLUTION_TEST', default='from-default'),
                    'from-file',
                )

            with isolated_environ({'RESOLUTION_TEST': 'from-env'}):
                self.assertEqual(accessor.get('RESOLUTION_TEST', default='from-default'), 'from-env')

    def test_secret_file_strips_trailing_newlines(self):
        with temp_secrets_dir() as secrets_dir:
            write_secret_file(secrets_dir, 'TRIMMED_SECRET', 'value\n\n')
            accessor = ConfigAccessor(secrets_dir=secrets_dir)
            with isolated_environ():
                self.assertEqual(accessor.get('TRIMMED_SECRET'), 'value')

    def test_empty_secret_file_is_treated_as_absent(self):
        with temp_secrets_dir() as secrets_dir:
            write_secret_file(secrets_dir, 'EMPTY_SECRET', '\n')
            accessor = ConfigAccessor(secrets_dir=secrets_dir)
            with isolated_environ():
                self.assertEqual(accessor.get('EMPTY_SECRET', default='fallback'), 'fallback')

    def test_bool_cast_true_values(self):
        for value in ('true', 'TRUE', '1', 'yes', 'on', 'On'):
            with self.subTest(value=value):
                with mock.patch.dict(os.environ, {'BOOL_TEST': value}, clear=False):
                    self.assertTrue(self.accessor.get_bool('BOOL_TEST'))

    def test_bool_cast_false_values(self):
        for value in ('false', '0', 'no', 'off', '', 'anything'):
            with self.subTest(value=value):
                with mock.patch.dict(os.environ, {'BOOL_TEST': value}, clear=False):
                    self.assertFalse(self.accessor.get_bool('BOOL_TEST'))

    def test_get_int_parses_integer(self):
        with mock.patch.dict(os.environ, {'PORT': '5432'}, clear=False):
            self.assertEqual(self.accessor.get_int('PORT'), 5432)

    def test_get_int_raises_improperly_configured_for_invalid_value(self):
        with mock.patch.dict(os.environ, {'PORT': 'not-a-number'}, clear=False):
            with self.assertRaises(ImproperlyConfigured) as ctx:
                self.accessor.get_int('PORT')
        message = str(ctx.exception)
        self.assertIn('PORT', message)
        self.assertIn('not-a-number', message)
        self.assertIs(type(ctx.exception), ImproperlyConfigured)

    def test_get_list_splits_and_trims(self):
        with mock.patch.dict(os.environ, {'HOSTS': ' localhost ,127.0.0.1,,'}, clear=False):
            self.assertEqual(self.accessor.get_list('HOSTS'), ['localhost', '127.0.0.1'])

    def test_get_list_empty_string_returns_empty_list(self):
        with mock.patch.dict(os.environ, {'HOSTS': '   '}, clear=False):
            self.assertEqual(self.accessor.get_list('HOSTS'), [])

    def test_secret_values_are_masked_in_diagnostics_and_repr(self):
        with mock.patch.dict(os.environ, {'API_SECRET': 'super-secret-value'}, clear=False):
            self.accessor.get('API_SECRET', secret=True)
        diagnostics = self.accessor.diagnostics()
        self.assertEqual(diagnostics['API_SECRET'], SECRET_MASK)
        self.assertNotIn('super-secret-value', repr(self.accessor))

    def test_secret_values_are_not_logged(self):
        with temp_secrets_dir() as secrets_dir:
            accessor = ConfigAccessor(secrets_dir=secrets_dir)
            with mock.patch.dict(os.environ, {'LOGGED_SECRET': 'hidden-token'}, clear=False):
                with self.assertLogs('webcrm.config', level='DEBUG') as logs:
                    accessor.get('LOGGED_SECRET', secret=True)
                log_output = '\n'.join(logs.output)
                self.assertIn(SECRET_MASK, log_output)
                self.assertNotIn('hidden-token', log_output)

    def test_unreadable_secret_file_raises_improperly_configured(self):
        with temp_secrets_dir() as secrets_dir:
            secret_path = write_secret_file(secrets_dir, 'UNREADABLE', 'value')
            accessor = ConfigAccessor(secrets_dir=secrets_dir)
            with isolated_environ():
                with mock.patch('builtins.open', side_effect=OSError('permission denied')):
                    with self.assertRaises(ImproperlyConfigured) as ctx:
                        accessor.get('UNREADABLE')
                self.assertIn('UNREADABLE', str(ctx.exception))
                self.assertIn(str(secret_path), str(ctx.exception))

    def test_missing_secrets_directory_skips_file_branch(self):
        accessor = ConfigAccessor(secrets_dir='/path/that/does/not/exist')
        with isolated_environ():
            self.assertEqual(accessor.get('ABSENT_VAR', default='ok'), 'ok')

    def test_fixture_secret_files_are_readable(self):
        accessor = ConfigAccessor(secrets_dir=str(FIXTURES_ENV_DIR))
        with isolated_environ():
            self.assertEqual(accessor.get('SECRET_KEY'), 'fixture-secret-key-value')
            self.assertEqual(accessor.get('DB_PASSWORD'), 'crmpass-from-secret-file')

    def test_is_testing_detects_test_runner(self):
        accessor = ConfigAccessor()
        original_argv = sys.argv[:]
        try:
            sys.argv = ['manage.py', 'test']
            self.assertTrue(accessor.is_testing())
            sys.argv = ['manage.py', 'runserver']
            self.assertFalse(accessor.is_testing())
        finally:
            sys.argv = original_argv

    def test_module_singleton_is_config_accessor(self):
        self.assertIsInstance(config, ConfigAccessor)

    def test_module_imports_only_stdlib_and_django_exceptions(self):
        import ast

        source_path = Path(__file__).resolve().parents[2] / 'webcrm' / 'config.py'
        tree = ast.parse(source_path.read_text(encoding='utf-8'))
        imported_roots: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_roots.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_roots.add(node.module.split('.')[0])
        self.assertEqual(imported_roots, {'__future__', 'logging', 'os', 'sys', 'typing', 'django'})


class ConfigAccessorIntegrationTests(SimpleTestCase):
    def test_webcrm_settings_imports_with_config_available(self):
        import webcrm.config  # noqa: F401
        import webcrm.settings  # noqa: F401

    def test_config_require_aborts_when_mandatory_value_missing(self):
        with temp_secrets_dir() as secrets_dir:
            accessor = ConfigAccessor(secrets_dir=secrets_dir)
            with isolated_environ():
                with self.assertRaises(ImproperlyConfigured):
                    accessor.require('ZZZ_WO001_INTEGRATION_REQUIRED')
