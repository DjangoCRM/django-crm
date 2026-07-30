from io import StringIO
from pathlib import Path
from unittest import mock

from django.core.management import call_command
from django.test import SimpleTestCase

from webcrm.secret_literal_scanner import (
    ENV_EXAMPLE_PATH,
    SETTINGS_SCAN_TARGETS,
    scan_env_example,
    scan_python_file,
    scan_repository,
)

FIXTURES_DIR = Path(__file__).resolve().parents[1] / 'fixtures' / 'security'
COMPLIANT_SAMPLE = FIXTURES_DIR / 'compliant_settings_sample.py'
NONCOMPLIANT_SAMPLE = FIXTURES_DIR / 'noncompliant_settings_sample.py'


class SecretLiteralScannerUnitTests(SimpleTestCase):
    def test_detects_top_level_secret_literal(self):
        findings = scan_python_file(NONCOMPLIANT_SAMPLE)
        names = {finding.name for finding in findings}
        self.assertIn('API_SECRET', names)

    def test_detects_dictionary_nested_secret_literals(self):
        findings = scan_python_file(NONCOMPLIANT_SAMPLE)
        names = {finding.name for finding in findings}
        self.assertIn('key', names)
        self.assertIn('secret', names)

    def test_reports_file_and_line_number(self):
        findings = scan_python_file(NONCOMPLIANT_SAMPLE)
        api_secret = next(f for f in findings if f.name == 'API_SECRET')
        self.assertEqual(api_secret.lineno, 3)
        self.assertIn('noncompliant_settings_sample.py', api_secret.path)

    def test_compliant_sample_has_zero_findings(self):
        self.assertEqual(scan_python_file(COMPLIANT_SAMPLE), [])

    def test_allowlist_suppresses_public_mask_token(self):
        config_path = next(
            path for path in SETTINGS_SCAN_TARGETS if path.name == 'config.py'
        )
        findings = scan_python_file(config_path)
        self.assertFalse(any(f.name == 'SECRET_MASK' for f in findings))

    def test_empty_string_assignment_is_not_a_violation(self):
        self.assertEqual(scan_python_file(COMPLIANT_SAMPLE), [])


class NoSecretLiteralsRepositoryTests(SimpleTestCase):
    def test_settings_modules_have_zero_secret_literal_findings(self):
        findings = scan_repository()
        self.assertEqual(
            findings,
            [],
            '\n'.join(
                f'{finding.path}:{finding.lineno} {finding.name}'
                for finding in findings
            ),
        )

    def test_seeded_fixture_is_detected(self):
        findings = scan_repository(
            extra_python_files=[NONCOMPLIANT_SAMPLE],
            include_env_example=False,
        )
        self.assertTrue(findings)

    def test_env_example_uses_placeholder_shape(self):
        self.assertEqual(scan_env_example(ENV_EXAMPLE_PATH), [])

    def test_check_secrets_command_passes_on_clean_tree(self):
        stdout = StringIO()
        call_command('check_secrets', stdout=stdout)
        self.assertIn('No secret literal violations found.', stdout.getvalue())

    def test_check_secrets_command_fails_on_seeded_violation(self):
        with mock.patch(
            'webcrm.secret_literal_scanner.SETTINGS_SCAN_TARGETS',
            SETTINGS_SCAN_TARGETS + [NONCOMPLIANT_SAMPLE],
        ):
            with self.assertRaises(SystemExit):
                call_command('check_secrets')
