"""Guard tests for declared database drivers and manifest consistency."""

from __future__ import annotations

import configparser
import json
import re
import unittest
from pathlib import Path

from django.test import SimpleTestCase, tag

from tests.fixtures.manifest_parser import compare_manifests
from tests.fixtures.manifest_parser import parse_requirements_file
from tests.fixtures.manifest_parser import parse_setup_cfg_install_requires

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS_PATH = PROJECT_ROOT / 'requirements.txt'
SETUP_CFG_PATH = PROJECT_ROOT / 'setup.cfg'
DOCS_REQUIREMENTS_PATH = PROJECT_ROOT / 'docs' / 'site' / 'requirements.txt'
MANIFEST_SAMPLES_DIR = PROJECT_ROOT / 'tests' / 'fixtures' / 'manifest_samples'

SUPPORTED_ENGINES = {
    'mysql': re.compile(r'^mysqlclient==', re.IGNORECASE),
    'postgresql': re.compile(r'^psycopg(\[binary\])?==', re.IGNORECASE),
}


def _read_requirement_lines() -> list[str]:
    return [
        line.strip()
        for line in REQUIREMENTS_PATH.read_text(encoding='utf-8').splitlines()
        if line.strip() and not line.strip().startswith('#')
    ]


def _read_install_require_lines() -> list[str]:
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
class TestManifestParser(SimpleTestCase):
    """Unit-test manifest parsing against committed sample fixtures."""

    def test_compare_manifests_reports_drift(self):
        left = parse_requirements_file(MANIFEST_SAMPLES_DIR / 'requirements_left.txt')
        right = parse_requirements_file(MANIFEST_SAMPLES_DIR / 'requirements_right.txt')
        diffs = compare_manifests(
            left,
            right,
            'requirements_left.txt',
            'requirements_right.txt',
        )
        expected = json.loads(
            (MANIFEST_SAMPLES_DIR / 'drift_expectations.json').read_text(encoding='utf-8')
        )['expected_diffs']
        self.assertEqual(sorted(diffs), sorted(expected))


@tag('Dependencies')
class TestDependencyManifests(SimpleTestCase):
    """Ensure runtime manifests stay aligned and declare database drivers."""

    def test_requirements_declares_supported_drivers(self):
        missing = _missing_drivers(_read_requirement_lines())
        self.assertEqual(
            missing,
            [],
            f"requirements.txt is missing drivers for: {', '.join(missing)}",
        )

    def test_setup_cfg_driver_versions_match_requirements(self):
        requirements = _driver_lines(_read_requirement_lines())
        install_requires = _driver_lines(_read_install_require_lines())
        self.assertEqual(
            install_requires,
            requirements,
            'Database driver pins must match between requirements.txt and setup.cfg',
        )

    def test_setup_cfg_declares_supported_drivers(self):
        missing = _missing_drivers(_read_install_require_lines())
        self.assertEqual(
            missing,
            [],
            f"setup.cfg install_requires is missing drivers for: {', '.join(missing)}",
        )

    def test_runtime_manifests_are_identical(self):
        requirements = parse_requirements_file(REQUIREMENTS_PATH)
        install_requires = parse_setup_cfg_install_requires(SETUP_CFG_PATH)
        diffs = compare_manifests(
            requirements,
            install_requires,
            'requirements.txt',
            'setup.cfg install_requires',
        )
        self.assertEqual(
            diffs,
            [],
            'Runtime manifest drift detected:\n' + '\n'.join(diffs),
        )

    def test_documentation_requirements_are_pinned(self):
        documentation = parse_requirements_file(DOCS_REQUIREMENTS_PATH)
        self.assertTrue(documentation)
        for name, specifier in documentation.items():
            self.assertNotEqual(
                specifier,
                'unspecified',
                f'{name} in docs/site/requirements.txt must pin an explicit version',
            )

    def test_python_requires_matches_classifiers(self):
        parser = configparser.ConfigParser()
        parser.read(SETUP_CFG_PATH, encoding='utf-8')
        python_requires = parser['options']['python_requires']
        classifiers = parser['metadata']['classifiers']
        self.assertEqual(python_requires, '>=3.12')
        self.assertIn('Programming Language :: Python :: 3.12', classifiers)


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
