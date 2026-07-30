"""Documentation contract tests for the Docker deployment runbook."""

from __future__ import annotations

import re
from pathlib import Path

from django.test import SimpleTestCase

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT_DOC = PROJECT_ROOT / 'docs' / 'site' / 'deployment-docker.md'
MKDOCS_FILE = PROJECT_ROOT / 'mkdocs.yml'

SECRET_LITERAL_PATTERN = re.compile(
    r'(password|secret|token|api[_-]?key)\s*[:=]\s*["\']?[A-Za-z0-9+/=_-]{12,}["\']?',
    re.IGNORECASE,
)

REQUIRED_HEADINGS = (
    '## Prerequisites',
    '## Environment preparation',
    '## First bring-up',
    '## Seeding reference data',
    '## Worker service',
    '## Static and media serving',
    '## Upgrade',
    '## Backup and restore',
    '## Rollback',
    '## Troubleshooting',
    '## Security checklist',
    '## Automated verification',
)


class DeploymentDocumentationTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.doc_text = DEPLOYMENT_DOC.read_text(encoding='utf-8')
        cls.mkdocs_text = MKDOCS_FILE.read_text(encoding='utf-8')

    def test_deployment_page_exists(self):
        self.assertTrue(DEPLOYMENT_DOC.is_file())

    def test_deployment_page_is_registered_in_mkdocs_navigation(self):
        self.assertIn('deployment-docker.md', self.mkdocs_text)

    def test_deployment_page_includes_required_sections(self):
        for heading in REQUIRED_HEADINGS:
            with self.subTest(heading=heading):
                self.assertIn(heading, self.doc_text)

    def test_deployment_page_documents_operational_invariants(self):
        self.assertIn('no published host port', self.doc_text.lower())
        self.assertIn('authenticated staff', self.doc_text.lower())
        self.assertIn('exactly one', self.doc_text.lower())

    def test_deployment_page_contains_no_credential_literals(self):
        for line in self.doc_text.splitlines():
            if line.strip().startswith('#'):
                continue
            if '<' in line and '>' in line:
                continue
            match = SECRET_LITERAL_PATTERN.search(line)
            self.assertIsNone(
                match,
                msg=f'Possible credential literal in deployment doc: {line.strip()}',
            )

    def test_compose_verify_script_exists(self):
        script = PROJECT_ROOT / 'scripts' / 'compose_verify.sh'
        self.assertTrue(script.is_file())
        self.assertIn('compose_verify.sh', self.doc_text)
