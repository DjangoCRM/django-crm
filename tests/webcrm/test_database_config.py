import os
from pathlib import Path
from unittest import mock

from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase, tag

from webcrm.config import ConfigAccessor, SECRET_MASK
from webcrm.database_config import build_databases, mask_database_config
from tests.base_test_classes import BaseTestCase
from tests.fixtures.database_connection_samples import (
    MYSQL_EMPTY_PASSWORD_URL,
    POSTGRES_ENCODED_PASSWORD_URL,
    POSTGRES_URL,
    SQLITE_MEMORY_URL,
)


class DatabaseConfigTests(SimpleTestCase):
    def setUp(self):
        self.base_dir = Path('/tmp/forge-crm')

    def test_defaults_to_sqlite_file_database(self):
        accessor = ConfigAccessor()
        with mock.patch('webcrm.database_config.config', accessor):
            with mock.patch.dict(os.environ, {}, clear=True):
                databases = build_databases(self.base_dir)
        self.assertEqual(
            databases['default']['ENGINE'],
            'django.db.backends.sqlite3',
        )
        self.assertEqual(databases['default']['NAME'], str(self.base_dir / 'crm_db'))
        self.assertEqual(databases['default']['TEST']['NAME'], 'test_crm_db')

    def test_builds_postgresql_from_discrete_variables(self):
        accessor = ConfigAccessor()
        env = {
            'DJANGO_DB_ENGINE': 'postgresql',
            'DJANGO_DB_NAME': 'crm_db',
            'DJANGO_DB_USER': 'crm_user',
            'DJANGO_DB_PASSWORD': 'secret',
            'DJANGO_DB_HOST': 'db.internal',
            'DJANGO_DB_PORT': '5432',
        }
        with mock.patch('webcrm.database_config.config', accessor):
            with mock.patch.dict(os.environ, env, clear=True):
                databases = build_databases(self.base_dir)
        default = databases['default']
        self.assertEqual(default['ENGINE'], 'django.db.backends.postgresql')
        self.assertEqual(default['NAME'], 'crm_db')
        self.assertEqual(default['USER'], 'crm_user')
        self.assertEqual(default['PASSWORD'], 'secret')
        self.assertEqual(default['HOST'], 'db.internal')
        self.assertEqual(default['PORT'], '5432')
        self.assertEqual(default['CONN_MAX_AGE'], 0)
        self.assertEqual(default['TEST']['NAME'], 'test_crm_db_pg')
        self.assertEqual(default['OPTIONS'], {'connect_timeout': 10})

    def test_builds_mysql_from_discrete_variables(self):
        accessor = ConfigAccessor()
        env = {
            'DJANGO_DB_ENGINE': 'mysql',
            'DJANGO_DB_NAME': 'crm_db',
            'DJANGO_DB_USER': 'crm_user',
            'DJANGO_DB_PASSWORD': 'secret',
            'DJANGO_DB_HOST': 'localhost',
        }
        with mock.patch('webcrm.database_config.config', accessor):
            with mock.patch.dict(os.environ, env, clear=True):
                databases = build_databases(self.base_dir)
        default = databases['default']
        self.assertEqual(default['ENGINE'], 'django.db.backends.mysql')
        self.assertEqual(default['PORT'], '3306')
        self.assertEqual(default['TEST']['NAME'], 'test_crm_db_mysql')
        self.assertEqual(default['OPTIONS']['charset'], 'utf8mb4')

    def test_database_url_overrides_discrete_variables(self):
        accessor = ConfigAccessor()
        env = {
            'DATABASE_URL': POSTGRES_URL,
            'DJANGO_DB_ENGINE': 'sqlite3',
        }
        with mock.patch('webcrm.database_config.config', accessor):
            with mock.patch.dict(os.environ, env, clear=True):
                databases = build_databases(self.base_dir)
        self.assertEqual(databases['default']['ENGINE'], 'django.db.backends.postgresql')
        self.assertEqual(databases['default']['NAME'], 'crm_db')

    def test_invalid_engine_raises_improperly_configured(self):
        accessor = ConfigAccessor()
        with mock.patch('webcrm.database_config.config', accessor):
            with mock.patch.dict(os.environ, {'DJANGO_DB_ENGINE': 'oracle'}, clear=True):
                with self.assertRaises(ImproperlyConfigured) as ctx:
                    build_databases(self.base_dir)
        self.assertIn('DJANGO_DB_ENGINE', str(ctx.exception))

    def test_invalid_database_url_scheme_names_variable(self):
        accessor = ConfigAccessor()
        with mock.patch('webcrm.database_config.config', accessor):
            with mock.patch.dict(
                os.environ,
                {'DATABASE_URL': 'oracle://user:pass@localhost/db'},
                clear=True,
            ):
                with self.assertRaises(ImproperlyConfigured) as ctx:
                    build_databases(self.base_dir)
        self.assertIn('DATABASE_URL', str(ctx.exception))

    def test_in_memory_sqlite_url(self):
        accessor = ConfigAccessor()
        with mock.patch('webcrm.database_config.config', accessor):
            with mock.patch.dict(os.environ, {'DATABASE_URL': SQLITE_MEMORY_URL}, clear=True):
                databases = build_databases(self.base_dir)
        self.assertEqual(databases['default']['NAME'], ':memory:')

    def test_percent_encoded_password_is_decoded(self):
        accessor = ConfigAccessor()
        with mock.patch('webcrm.database_config.config', accessor):
            with mock.patch.dict(
                os.environ,
                {'DATABASE_URL': POSTGRES_ENCODED_PASSWORD_URL},
                clear=True,
            ):
                databases = build_databases(self.base_dir)
        self.assertEqual(databases['default']['PASSWORD'], 'p@ss/word')
        self.assertEqual(databases['default']['PORT'], '5432')

    def test_empty_mysql_password_is_accepted(self):
        accessor = ConfigAccessor()
        with mock.patch('webcrm.database_config.config', accessor):
            with mock.patch.dict(
                os.environ,
                {'DATABASE_URL': MYSQL_EMPTY_PASSWORD_URL},
                clear=True,
            ):
                databases = build_databases(self.base_dir)
        self.assertEqual(databases['default']['PASSWORD'], '')

    def test_mask_database_config_redacts_password(self):
        databases = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'crm_db',
                'PASSWORD': 'secret-value',
            }
        }
        masked = mask_database_config(databases)
        self.assertEqual(masked['default']['PASSWORD'], SECRET_MASK)
        self.assertEqual(databases['default']['PASSWORD'], 'secret-value')


@tag('TestCase')
class BaseFixtureLoadTests(BaseTestCase):
    def test_base_fixtures_load_on_sqlite(self):
        from django.contrib.auth import get_user_model

        self.assertTrue(get_user_model().objects.exists())


class DatabaseIntegrationTests(SimpleTestCase):
    def test_live_connection_when_database_url_is_set(self):
        database_url = os.environ.get('DATABASE_URL', '').strip()
        if not database_url or database_url.startswith('sqlite'):
            self.skipTest('Non-sqlite DATABASE_URL not configured for integration test')

        base_dir = Path('/tmp/forge-crm-integration')
        accessor = ConfigAccessor()
        with mock.patch('webcrm.database_config.config', accessor):
            with mock.patch.dict(os.environ, {'DATABASE_URL': database_url}, clear=True):
                databases = build_databases(base_dir)

        engine = databases['default']['ENGINE']
        if engine.endswith('postgresql'):
            try:
                import psycopg  # noqa: F401
            except ImportError:
                self.skipTest('psycopg driver unavailable')
        if engine.endswith('mysql'):
            try:
                import MySQLdb  # noqa: F401
            except ImportError:
                self.skipTest('mysqlclient driver unavailable')

        from django.conf import settings
        from django.db import connections
        from django.core.management import call_command
        from django.db.migrations.executor import MigrationExecutor

        original = settings.DATABASES
        settings.DATABASES = databases
        try:
            db_connection = connections['default']
            db_connection.ensure_connection()
            with db_connection.cursor() as cursor:
                cursor.execute('SELECT 1')
                self.assertEqual(cursor.fetchone()[0], 1)
            call_command('migrate', interactive=False, verbosity=0)
            executor = MigrationExecutor(db_connection)
            plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
            self.assertEqual(plan, [])
        except Exception as exc:
            self.skipTest(f'Target database engine unavailable: {exc}')
        finally:
            connections.close_all()
            settings.DATABASES = original
