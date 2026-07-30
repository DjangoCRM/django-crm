"""Static contract tests for the docker-compose stack definition."""

from __future__ import annotations

import re
from pathlib import Path

import yaml
from django.test import SimpleTestCase

PROJECT_ROOT = Path(__file__).resolve().parents[2]
COMPOSE_FILE = PROJECT_ROOT / 'docker-compose.yml'
COMPOSE_OVERRIDE = PROJECT_ROOT / 'docker-compose.override.yml'

SECRET_LITERAL_PATTERN = re.compile(
    r'(password|secret|token)\s*[:=]\s*["\']?[^"\']{8,}["\']?',
    re.IGNORECASE,
)


def _load_compose(path: Path) -> dict:
    with path.open(encoding='utf-8') as handle:
        return yaml.safe_load(handle)


class ComposeContractTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.compose = _load_compose(COMPOSE_FILE)
        cls.override = _load_compose(COMPOSE_OVERRIDE)

    def test_compose_defines_app_db_and_worker_services(self):
        services = self.compose['services']
        self.assertEqual(set(services.keys()), {'app', 'db', 'worker'})

    def test_db_service_has_no_published_ports(self):
        db_service = self.compose['services']['db']
        self.assertNotIn('ports', db_service)

    def test_db_service_uses_pinned_postgres_image(self):
        image = self.compose['services']['db']['image']
        self.assertIn('postgres:16-bookworm@sha256:', image)

    def test_db_service_declares_pg_isready_health_check(self):
        healthcheck = self.compose['services']['db']['healthcheck']
        self.assertIn('pg_isready', healthcheck['test'][1])
        self.assertEqual(healthcheck['interval'], '10s')
        self.assertEqual(healthcheck['timeout'], '5s')
        self.assertEqual(healthcheck['retries'], 5)

    def test_app_service_waits_for_healthy_database(self):
        depends_on = self.compose['services']['app']['depends_on']
        self.assertEqual(depends_on['db']['condition'], 'service_healthy')

    def test_named_internal_network_is_declared(self):
        network = self.compose['networks']['crm_internal']
        self.assertEqual(network['driver'], 'bridge')
        self.assertEqual(network['name'], 'crm_internal')
        for service in self.compose['services'].values():
            self.assertIn('crm_internal', service['networks'])

    def test_worker_service_waits_for_healthy_database(self):
        depends_on = self.compose['services']['worker']['depends_on']
        self.assertEqual(depends_on['db']['condition'], 'service_healthy')

    def test_worker_service_disables_migrations_and_collectstatic(self):
        environment = self.compose['services']['worker']['environment']
        self.assertEqual(environment['RUN_MIGRATIONS'], '0')
        self.assertEqual(environment['RUN_COLLECTSTATIC'], '0')
        self.assertEqual(environment['RUN_BACKGROUND_WORKERS'], 'false')

    def test_app_service_disables_background_workers_and_inline_import(self):
        environment = self.compose['services']['app']['environment']
        self.assertEqual(environment['RUN_BACKGROUND_WORKERS'], 'false')
        self.assertEqual(environment['RUN_INLINE_EMAIL_IMPORT'], 'false')

    def test_worker_service_mounts_shared_media_volume(self):
        volumes = self.compose['services']['worker']['volumes']
        self.assertIn('media:/app/media', volumes)

    def test_named_volumes_include_pgdata_media_and_staticfiles(self):
        volumes = set(self.compose['volumes'].keys())
        self.assertEqual(volumes, {'pgdata', 'media', 'staticfiles'})
        app_volumes = self.compose['services']['app']['volumes']
        self.assertIn('media:/app/media', app_volumes)
        self.assertIn('staticfiles:/app/static', app_volumes)

    def test_compose_files_contain_no_secret_literals(self):
        for path in (COMPOSE_FILE, COMPOSE_OVERRIDE):
            content = path.read_text(encoding='utf-8')
            self.assertIsNone(
                SECRET_LITERAL_PATTERN.search(content),
                msg=f'Possible secret literal found in {path}',
            )

    def test_override_provides_development_bind_mount_and_debug_toggle(self):
        override_app = self.override['services']['app']
        self.assertIn('.:/app', override_app['volumes'])
        self.assertIn('DJANGO_DEBUG', override_app['environment'])
