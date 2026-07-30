import os
from pathlib import Path
from unittest import mock

from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django.test import SimpleTestCase, override_settings

from webcrm.config import ConfigAccessor
from webcrm.config_catalog import MANDATORY_ENV_VARIABLES

REPO_ROOT = Path(__file__).resolve().parents[2]
FILLED_ENV_PATH = REPO_ROOT / 'tests' / 'fixtures' / 'env_example_filled.env'


def _parse_env_values(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith('#') or '=' not in stripped:
            continue
        key, _, raw_value = stripped.partition('=')
        value = raw_value.strip()
        if value.startswith('<') and value.endswith('>'):
            value = value[1:-1]
        values[key.strip()] = value
    return values


class StartupSmokeTests(SimpleTestCase):
    def test_complete_environment_passes_system_checks(self):
        env = _parse_env_values(FILLED_ENV_PATH)
        env['DJANGO_DEBUG'] = 'true'
        with mock.patch.dict(os.environ, env, clear=True):
            call_command('check')

    def test_missing_mandatory_variable_raises_improperly_configured(self):
        env = _parse_env_values(FILLED_ENV_PATH)
        env['DJANGO_DEBUG'] = 'true'
        for mandatory in sorted(MANDATORY_ENV_VARIABLES):
            with self.subTest(mandatory=mandatory):
                case_env = dict(env)
                case_env.pop(mandatory, None)
                accessor = ConfigAccessor()
                with mock.patch.dict(os.environ, case_env, clear=True):
                    with self.assertRaises(ImproperlyConfigured) as ctx:
                        accessor.require(mandatory)
                    self.assertIn(mandatory, str(ctx.exception))

    @override_settings(DEBUG=False)
    def test_debug_defaults_to_false_when_unset(self):
        self.assertFalse(__import__('django.conf', fromlist=['settings']).settings.DEBUG)

    def test_debug_defaults_to_false_for_non_affirmative_values(self):
        accessor = ConfigAccessor()
        env = _parse_env_values(FILLED_ENV_PATH)
        for value in ('false', 'False', '0', 'no', 'off', ''):
            with self.subTest(value=value):
                case_env = dict(env)
                case_env['DJANGO_DEBUG'] = value
                with mock.patch.dict(os.environ, case_env, clear=True):
                    self.assertFalse(accessor.get_bool('DJANGO_DEBUG', default=False))
