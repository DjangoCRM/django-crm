"""Validate coverage measurement configuration."""

from pathlib import Path

from django.test import SimpleTestCase, tag

from tests.fixtures.manifest_parser import parse_requirements_file
from tests.fixtures.manifest_parser import parse_setup_cfg_install_requires

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYPROJECT_PATH = PROJECT_ROOT / 'pyproject.toml'
DEV_REQUIREMENTS_PATH = PROJECT_ROOT / 'requirements-dev.txt'
APPLICATIONS = (
    'common',
    'crm',
    'analytics',
    'tasks',
    'massmail',
    'chat',
    'voip',
    'quality',
    'help',
    'settings',
    'webcrm',
)


@tag('CI')
class TestCoverageConfig(SimpleTestCase):
    def test_dev_requirements_pin_coverage_only(self):
        dev_requirements = parse_requirements_file(DEV_REQUIREMENTS_PATH)
        runtime_requirements = parse_requirements_file(PROJECT_ROOT / 'requirements.txt')
        install_requires = parse_setup_cfg_install_requires(PROJECT_ROOT / 'setup.cfg')
        self.assertIn('coverage[toml]', dev_requirements)
        self.assertNotIn('coverage[toml]', runtime_requirements)
        self.assertNotIn('coverage', runtime_requirements)
        self.assertTrue(
            all('coverage' not in name for name in install_requires),
            'coverage must not appear in setup.cfg install_requires',
        )

    def test_pyproject_declares_application_sources(self):
        pyproject = PYPROJECT_PATH.read_text(encoding='utf-8')
        self.assertIn('branch = true', pyproject)
        self.assertIn('# fail_under = 90', pyproject)
        for app in APPLICATIONS:
            self.assertIn(f'"{app}"', pyproject)
        self.assertIn('*/migrations/*', pyproject)
        self.assertIn('*/tests/*', pyproject)
