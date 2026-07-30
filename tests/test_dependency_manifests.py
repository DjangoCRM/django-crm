"""Guard tests for declared database drivers in dependency manifests."""

from __future__ import annotations

import configparser
import re
import unittest
from pathlib import Path

from django.test import SimpleTestCase, tag

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS_PATH = PROJECT_ROOT / 'requirements.txt'
SETUP_CFG_PATH = PROJECT_ROOT / 'setup.cfg'

SUPPORTED_ENGINES = {
    'mysql': re.compile(r'^mysqlclient==', re.IGNORECASE),
    'postgresql': re.compile(r'^psycopg(\[binary\])?==', re.IGNORECASE),
}


def _read_requirements() -> list[str]:
    return [
        line.strip()
        for line in REQUIREMENTS_PATH.read_text(encoding='utf-8').splitlines()
        if line.strip() and not line.strip().startswith('#')
    ]


def _read_install_requires() -> list[str]:
    parser = configparser.ConfigParser()
    parser.read(SETUP_CFG_PATH, encoding='utf-8')
    return [
        item.strip()
        for item in parser['options']['install_requires'].splitlines()
        if item.strip()
    ]


def _driver_lines(requirements: list[str]) -> dict[str, str]:
    drivers = {}
    for requirement in requirements:
        for engine, pattern in SUPPORTED_ENGINES.items():
            if pattern.match(requirement):
                drivers[engine] = requirement
    return drivers


def _missing_drivers(requirements: list[str]) -> list[str]:
    declared = _driver_lines(requirements)
    return [engine for engine in SUPPORTED_ENGINES if engine not in declared]


@tag('Dependencies')
class TestDependencyManifests(SimpleTestCase):
    """Ensure every supported database engine has a declared driver."""

    def test_requirements_declares_supported_drivers(self):
        missing = _missing_drivers(_read_requirements())
        self.assertEqual(
            missing,
            [],
            f"requirements.txt is missing drivers for: {', '.join(missing)}",
        )

    def test_setup_cfg_driver_versions_match_requirements(self):
        requirements = _driver_lines(_read_requirements())
        install_requires = _driver_lines(_read_install_requires())
        self.assertEqual(
            install_requires,
            requirements,
            'Database driver pins must match between requirements.txt and setup.cfg',
        )

    def test_setup_cfg_declares_supported_drivers(self):
        missing = _missing_drivers(_read_install_requires())
        self.assertEqual(
            missing,
            [],
            f"setup.cfg install_requires is missing drivers for: {', '.join(missing)}",
        )


def _postgres_test_dsn() -> str | None:
    import os

    explicit = os.environ.get('POSTGRES_TEST_DSN', '').strip()
    if explicit:
        return explicit
    database_url = os.environ.get('DATABASE_URL', '').strip()
    if database_url.lower().startswith(('postgres://', 'postgresql://')):
        return database_url
    return None


@tag('Dependencies')
class TestPostgreSQLConnectivity(SimpleTestCase):
    """Exercise the declared PostgreSQL driver when a DSN is available."""

    def test_postgresql_driver_importable(self):
        import psycopg

        self.assertTrue(callable(psycopg.connect))

    @unittest.skipUnless(
        _postgres_test_dsn() is not None,
        'Set POSTGRES_TEST_DSN or a postgres DATABASE_URL to run connectivity checks',
    )
    def test_postgresql_connection(self):
        import psycopg

        dsn = _postgres_test_dsn()
        assert dsn is not None
        with psycopg.connect(dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
                self.assertEqual(cursor.fetchone()[0], 1)
