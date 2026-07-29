"""Assemble Django DATABASES from environment variables or DATABASE_URL."""

from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import unquote, urlparse

from django.core.exceptions import ImproperlyConfigured

from webcrm.config import ENV_REMEDIATION, MISSING, config

_ENGINE_BACKENDS = {
    'sqlite': 'django.db.backends.sqlite3',
    'sqlite3': 'django.db.backends.sqlite3',
    'postgresql': 'django.db.backends.postgresql',
    'postgres': 'django.db.backends.postgresql',
    'mysql': 'django.db.backends.mysql',
    'mariadb': 'django.db.backends.mysql',
}


def _engine_backend(engine: str) -> str:
    normalized = engine.strip().lower()
    backend = _ENGINE_BACKENDS.get(normalized)
    if backend is None:
        raise ImproperlyConfigured(
            f"Unsupported DJANGO_DB_ENGINE value {engine!r}. "
            f"Use sqlite3, postgresql, or mysql. {ENV_REMEDIATION}"
        )
    return backend


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
        if parsed.path in ('', '/'):
            name = str(base_dir / 'crm_db')
        elif parsed.path == '/:memory:':
            name = ':memory:'
        else:
            name = unquote(parsed.path.lstrip('/'))
        return {'default': {'ENGINE': engine, 'NAME': name}}

    if not parsed.path or parsed.path == '/':
        raise ImproperlyConfigured(
            f"DATABASE_URL for {scheme!r} must include a database name. {ENV_REMEDIATION}"
        )

    database: dict[str, str | int] = {
        'ENGINE': engine,
        'NAME': unquote(parsed.path.lstrip('/')),
    }
    if parsed.username:
        database['USER'] = unquote(parsed.username)
    if parsed.password:
        database['PASSWORD'] = unquote(parsed.password)
    if parsed.hostname:
        database['HOST'] = parsed.hostname
    if parsed.port:
        database['PORT'] = str(parsed.port)
    return {'default': database}


def build_databases(base_dir: Path) -> dict:
    """Build DATABASES using DATABASE_URL or discrete DJANGO_DB_* variables."""
    if 'DATABASE_URL' in os.environ and os.environ['DATABASE_URL'].strip():
        return _database_from_url(os.environ['DATABASE_URL'].strip(), base_dir)

    engine = config.get('DJANGO_DB_ENGINE', default='sqlite3')
    backend = _engine_backend(engine)

    if backend.endswith('sqlite3'):
        name = config.get('DJANGO_DB_NAME', default=str(base_dir / 'crm_db'))
        return {'default': {'ENGINE': backend, 'NAME': name}}

    database: dict[str, str | int] = {
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

    return {'default': database}
