"""Assemble Django DATABASES from environment variables or DATABASE_URL."""

from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import unquote, urlparse

from django.core.exceptions import ImproperlyConfigured

from webcrm.config import ENV_REMEDIATION, MISSING, SECRET_MASK, config

_ENGINE_BACKENDS = {
    'sqlite': 'django.db.backends.sqlite3',
    'sqlite3': 'django.db.backends.sqlite3',
    'postgresql': 'django.db.backends.postgresql',
    'postgres': 'django.db.backends.postgresql',
    'mysql': 'django.db.backends.mysql',
    'mariadb': 'django.db.backends.mysql',
}

_DEFAULT_PORTS = {
    'django.db.backends.postgresql': '5432',
    'django.db.backends.mysql': '3306',
}

_TEST_NAMES = {
    'django.db.backends.sqlite3': 'test_crm_db',
    'django.db.backends.postgresql': 'test_crm_db_pg',
    'django.db.backends.mysql': 'test_crm_db_mysql',
}


def mask_database_config(databases: dict) -> dict:
    """Return a copy of DATABASES with passwords redacted for diagnostics."""
    masked: dict = {}
    for alias, settings in databases.items():
        entry = dict(settings)
        if entry.get('PASSWORD'):
            entry['PASSWORD'] = SECRET_MASK
        masked[alias] = entry
    return masked


def _engine_backend(engine: str) -> str:
    normalized = engine.strip().lower()
    backend = _ENGINE_BACKENDS.get(normalized)
    if backend is None:
        raise ImproperlyConfigured(
            f"Unsupported DJANGO_DB_ENGINE value {engine!r}. "
            f"Use sqlite3, postgresql, or mysql. {ENV_REMEDIATION}"
        )
    return backend


def _sqlite_name(parsed_path: str, base_dir: Path) -> str:
    if parsed_path in ('', '/'):
        return str(base_dir / 'crm_db')
    decoded = unquote(parsed_path.lstrip('/'))
    if decoded == ':memory:':
        return ':memory:'
    return decoded


def _finalize_database(database: dict) -> dict:
    engine = database['ENGINE']
    if engine.endswith('sqlite3'):
        database.setdefault('TEST', {'NAME': _TEST_NAMES[engine]})
        return database

    if 'PORT' not in database:
        database['PORT'] = _DEFAULT_PORTS[engine]

    database['CONN_MAX_AGE'] = 0
    database.setdefault('TEST', {'NAME': _TEST_NAMES[engine]})

    if engine.endswith('mysql'):
        database['OPTIONS'] = {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    elif engine.endswith('postgresql'):
        database['OPTIONS'] = {
            'connect_timeout': 10,
        }

    return database


def _database_from_url(database_url: str, base_dir: Path) -> dict:
    parsed = urlparse(database_url)
    scheme = parsed.scheme.lower()
    if scheme not in _ENGINE_BACKENDS:
        raise ImproperlyConfigured(
            f"Unsupported DATABASE_URL scheme {scheme!r}. "
            f"Use sqlite, postgresql, or mysql. {ENV_REMEDIATION}"
        )

    engine = _ENGINE_BACKENDS[scheme]
    if engine.endswith('sqlite3'):
        sqlite_path = parsed.path
        if not sqlite_path and parsed.netloc == ':memory:':
            sqlite_path = '/:memory:'
        database = {'ENGINE': engine, 'NAME': _sqlite_name(sqlite_path, base_dir)}
        return {'default': _finalize_database(database)}

    if not parsed.path or parsed.path == '/':
        raise ImproperlyConfigured(
            f"DATABASE_URL for {scheme!r} must include a database name. {ENV_REMEDIATION}"
        )

    database: dict[str, str | int | dict] = {
        'ENGINE': engine,
        'NAME': unquote(parsed.path.lstrip('/')),
    }
    if parsed.username is not None:
        database['USER'] = unquote(parsed.username)
    if parsed.password is not None:
        database['PASSWORD'] = unquote(parsed.password)
    if parsed.hostname:
        database['HOST'] = parsed.hostname
    if parsed.port:
        database['PORT'] = str(parsed.port)

    return {'default': _finalize_database(database)}


def build_databases(base_dir: Path) -> dict:
    """Build DATABASES using DATABASE_URL or discrete DJANGO_DB_* variables."""
    if 'DATABASE_URL' in os.environ and os.environ['DATABASE_URL'].strip():
        return _database_from_url(os.environ['DATABASE_URL'].strip(), base_dir)

    engine = config.get('DJANGO_DB_ENGINE', default='sqlite3')
    backend = _engine_backend(engine)

    if backend.endswith('sqlite3'):
        name = config.get('DJANGO_DB_NAME', default=str(base_dir / 'crm_db'))
        database = {'ENGINE': backend, 'NAME': name}
        return {'default': _finalize_database(database)}

    database: dict[str, str | int | dict] = {
        'ENGINE': backend,
        'NAME': config.require('DJANGO_DB_NAME'),
    }
    database['USER'] = config.get('DJANGO_DB_USER', default='')
    database['PASSWORD'] = config.get('DJANGO_DB_PASSWORD', default='', secret=True)
    database['HOST'] = config.get('DJANGO_DB_HOST', default='localhost')

    port_default: object = MISSING
    if backend.endswith('mysql'):
        port_default = '3306'
    elif backend.endswith('postgresql'):
        port_default = '5432'
    database['PORT'] = config.get('DJANGO_DB_PORT', default=port_default)

    return {'default': _finalize_database(database)}
