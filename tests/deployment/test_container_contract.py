"""Static contract tests for the container image definition."""

from __future__ import annotations

import re
from pathlib import Path

from django.test import SimpleTestCase

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOCKERFILE = PROJECT_ROOT / 'Dockerfile'
ENTRYPOINT = PROJECT_ROOT / 'docker' / 'entrypoint.sh'
DOCKERIGNORE = PROJECT_ROOT / '.dockerignore'

SECRET_LITERAL_PATTERN = re.compile(
    r'(password|secret|token)\s*=\s*["\'][^"\']{8,}["\']',
    re.IGNORECASE,
)


class ContainerContractTests(SimpleTestCase):
    def test_dockerfile_pins_python_base_by_digest(self):
        content = DOCKERFILE.read_text(encoding='utf-8')
        self.assertIn('python:3.12-slim-bookworm@sha256:', content)

    def test_dockerfile_runs_as_non_root_user(self):
        content = DOCKERFILE.read_text(encoding='utf-8')
        self.assertIn('USER 10001', content)
        self.assertIn('--uid 10001', content)

    def test_dockerfile_sets_python_runtime_flags(self):
        content = DOCKERFILE.read_text(encoding='utf-8')
        self.assertIn('PYTHONDONTWRITEBYTECODE=1', content)
        self.assertIn('PYTHONUNBUFFERED=1', content)

    def test_dockerfile_does_not_ship_build_toolchain_in_runtime(self):
        content = DOCKERFILE.read_text(encoding='utf-8')
        runtime_section = content.split('AS runtime', 1)[1]
        self.assertNotIn('build-essential', runtime_section)
        self.assertNotRegex(runtime_section, r'\b\w+-dev\b')

    def test_dockerfile_starts_gunicorn_on_port_8000(self):
        content = DOCKERFILE.read_text(encoding='utf-8')
        self.assertIn('gunicorn', content)
        self.assertIn('0.0.0.0:8000', content)
        self.assertIn('--access-logfile', content)

    def test_entrypoint_waits_migrates_collectstatic_and_execs(self):
        content = ENTRYPOINT.read_text(encoding='utf-8')
        wait_index = content.index('connection.ensure_connection()')
        migrate_index = content.index('migrate --noinput')
        collectstatic_index = content.index('collectstatic --noinput')
        exec_index = content.index('exec "$@"')
        self.assertLess(wait_index, migrate_index)
        self.assertLess(migrate_index, collectstatic_index)
        self.assertLess(collectstatic_index, exec_index)

    def test_entrypoint_uses_strict_shell_options(self):
        content = ENTRYPOINT.read_text(encoding='utf-8')
        self.assertIn('set -euo pipefail', content)

    def test_dockerignore_excludes_secrets_and_artifacts(self):
        content = DOCKERIGNORE.read_text(encoding='utf-8')
        for pattern in ('.git', '.env', 'media', 'static', '__pycache__'):
            self.assertIn(pattern, content)

    def test_container_files_contain_no_secret_literals(self):
        for path in (DOCKERFILE, ENTRYPOINT):
            content = path.read_text(encoding='utf-8')
            self.assertIsNone(
                SECRET_LITERAL_PATTERN.search(content),
                msg=f'Possible secret literal found in {path}',
            )
