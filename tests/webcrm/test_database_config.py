import os
from pathlib import Path
from unittest import mock

from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from webcrm.config import ConfigAccessor
from webcrm.database_config import build_databases


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
        self.assertEqual(databases['default']['ENGINE'], 'django.db.backends.postgresql')
        self.assertEqual(databases['default']['NAME'], 'crm_db')
        self.assertEqual(databases['default']['USER'], 'crm_user')
        self.assertEqual(databases['default']['PASSWORD'], 'secret')
        self.assertEqual(databases['default']['HOST'], 'db.internal')
        self.assertEqual(databases['default']['PORT'], '5432')

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
        self.assertEqual(databases['default']['ENGINE'], 'django.db.backends.mysql')
        self.assertEqual(databases['default']['PORT'], '3306')

    def test_database_url_overrides_discrete_variables(self):
        accessor = ConfigAccessor()
        env = {
            'DATABASE_URL': 'postgresql://crm_user:secret@localhost:5432/crm_db',
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
