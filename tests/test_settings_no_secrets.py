"""Settings modules must not contain secret literals."""

from django.test import SimpleTestCase, tag

from tests.security.test_no_secret_literals import COMPLIANT_SAMPLE
from tests.security.test_no_secret_literals import NONCOMPLIANT_SAMPLE
from webcrm.secret_literal_scanner import REPO_ROOT
from webcrm.secret_literal_scanner import SETTINGS_SCAN_TARGETS
from webcrm.secret_literal_scanner import scan_python_file

SETTINGS_MODULES = {
    'webcrm/settings.py',
    'voip/settings.py',
    'common/settings.py',
    'crm/settings.py',
    'tasks/settings.py',
}


@tag('Security')
class TestSettingsNoSecrets(SimpleTestCase):
    def test_tracked_settings_modules_have_no_secret_literals(self):
        findings = []
        for target in SETTINGS_SCAN_TARGETS:
            relative = target.relative_to(REPO_ROOT).as_posix()
            if relative not in SETTINGS_MODULES:
                continue
            findings.extend(scan_python_file(target))
        self.assertEqual(
            findings,
            [],
            '\n'.join(
                f'{finding.path}:{finding.lineno} {finding.name}'
                for finding in findings
            ),
        )

    def test_fixture_literal_is_detected(self):
        findings = scan_python_file(NONCOMPLIANT_SAMPLE)
        self.assertTrue(findings)
        self.assertIn('noncompliant_settings_sample.py', findings[0].path)

    def test_fixture_accessor_resolution_is_allowed(self):
        self.assertEqual(scan_python_file(COMPLIANT_SAMPLE), [])
