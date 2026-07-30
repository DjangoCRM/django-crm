"""Validate the CI workflow configuration."""

from pathlib import Path

from django.test import SimpleTestCase, tag

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CI_WORKFLOW_PATH = PROJECT_ROOT / '.github' / 'workflows' / 'ci.yml'


@tag('CI')
class TestCIWorkflow(SimpleTestCase):
    def test_ci_workflow_declares_three_database_legs(self):
        workflow = CI_WORKFLOW_PATH.read_text(encoding='utf-8')
        self.assertIn("permissions:\n  contents: read", workflow)
        self.assertIn('cancel-in-progress: true', workflow)
        self.assertIn('test-sqlite:', workflow)
        self.assertIn('test-postgres:', workflow)
        self.assertIn('test-mysql:', workflow)
        self.assertIn('image: postgres:16', workflow)
        self.assertIn('image: mysql:8', workflow)
        self.assertIn('pg_isready', workflow)
        self.assertIn('mysqladmin ping', workflow)
        self.assertIn('python manage.py check', workflow)
        self.assertIn('coverage run manage.py test tests/ --noinput', workflow)
        self.assertIn('write_leg_summary.sh', workflow)
        self.assertIn('write_coverage_summary.py', workflow)
        self.assertIn('requirements-dev.txt', workflow)
        sqlite_section = workflow.split('test-sqlite:', 1)[1].split('test-postgres:', 1)[0]
        self.assertNotIn('services:', sqlite_section)
