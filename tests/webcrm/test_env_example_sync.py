import importlib
import os
import re
import sys
from io import StringIO
from pathlib import Path
from unittest import mock

from django.core.management import call_command
from django.test import SimpleTestCase

from webcrm.config import SECRET_MASK, ConfigAccessor, config
from webcrm.config_catalog import (
    DOCUMENTED_ENV_VARIABLES,
    FORBIDDEN_ENV_EXAMPLE_VALUES,
    MANDATORY_ENV_VARIABLES,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
ENV_EXAMPLE_PATH = REPO_ROOT / '.env.example'
FILLED_ENV_PATH = REPO_ROOT / 'tests' / 'fixtures' / 'env_example_filled.env'
ENV_KEY_RE = re.compile(r'^(?:#\s*)?([A-Z][A-Z0-9_]+)\s*=')


def _parse_env_keys(path: Path) -> set[str]:
    keys: set[str] = set()
    for line in path.read_text(encoding='utf-8').splitlines():
        match = ENV_KEY_RE.match(line.strip())
        if match:
            keys.add(match.group(1))
    return keys


def _parse_env_values(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        key, _, raw_value = stripped.partition('=')
        value = raw_value.strip()
        if value.startswith('<') and value.endswith('>'):
            value = value[1:-1]
        values[key.strip()] = value
    return values


class EnvExampleTemplateTests(SimpleTestCase):
    def test_mandatory_variables_documented_in_env_example(self):
        documented = _parse_env_keys(ENV_EXAMPLE_PATH)
        missing = sorted(MANDATORY_ENV_VARIABLES - documented)
        self.assertEqual(missing, [], f'Missing mandatory keys in .env.example: {missing}')

    def test_documented_variables_present_in_env_example(self):
        documented = _parse_env_keys(ENV_EXAMPLE_PATH)
        missing = sorted(DOCUMENTED_ENV_VARIABLES - documented)
        self.assertEqual(missing, [], f'Missing documented keys in .env.example: {missing}')

    def test_env_example_uses_placeholder_values_only(self):
        contents = ENV_EXAMPLE_PATH.read_text(encoding='utf-8')
        for line in contents.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith('#') or '=' not in stripped:
                continue
            _, _, raw_value = stripped.partition('=')
            value = raw_value.strip()
            if value.startswith('<') and value.endswith('>'):
                continue
            self.fail(f'.env.example value must use angle-bracket placeholders: {stripped}')

    def test_env_example_contains_no_legacy_literal_values(self):
        values = _parse_env_values(FILLED_ENV_PATH)
        for name, value in values.items():
            self.assertNotIn(
                value,
                FORBIDDEN_ENV_EXAMPLE_VALUES,
                f'{name} uses a forbidden legacy literal value',
            )


class ShowConfigCommandTests(SimpleTestCase):
    def test_show_config_masks_secrets_and_sorts_output(self):
        accessor = ConfigAccessor()
        with mock.patch.dict(
            os.environ,
            {
                'MASK_TEST_PUBLIC': 'visible-value',
                'MASK_TEST_SECRET': 'super-secret-value',
            },
            clear=True,
        ):
            accessor.get('MASK_TEST_PUBLIC')
            accessor.get('MASK_TEST_SECRET', secret=True)
            with mock.patch('webcrm.config.config', accessor):
                stdout = StringIO()
                call_command('show_config', stdout=stdout)
        output = stdout.getvalue()
        self.assertIn('MASK_TEST_PUBLIC\tenvironment\tvisible-value', output)
        self.assertIn(f'MASK_TEST_SECRET\tenvironment\t{SECRET_MASK}', output)
        self.assertNotIn('super-secret-value', output)
        lines = [line for line in output.splitlines() if line.strip()]
        self.assertEqual(lines, sorted(lines))

    def test_generate_secret_key_prints_non_empty_value(self):
        stdout = StringIO()
        call_command('generate_secret_key', stdout=stdout)
        self.assertTrue(stdout.getvalue().strip())


class EnvExampleIntegrationTests(SimpleTestCase):
    def test_filled_template_loads_settings_successfully(self):
        env = _parse_env_values(FILLED_ENV_PATH)
        env['DJANGO_DEBUG'] = 'true'
        with mock.patch.dict(os.environ, env, clear=True):
            with mock.patch.object(sys, 'argv', ['manage.py', 'runserver']):
                settings = importlib.reload(importlib.import_module('webcrm.settings'))
        self.assertTrue(settings.SECRET_KEY)
        self.assertIn('DJANGO_SECRET_KEY', config.diagnostics())
