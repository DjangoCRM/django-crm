"""Ensure workflow actions use immutable commit SHAs."""

import re
from pathlib import Path

from django.test import SimpleTestCase, tag

WORKFLOWS_DIR = Path(__file__).resolve().parents[1] / '.github' / 'workflows'
IMMUTABLE_SHA = re.compile(r'@[0-9a-f]{40}\b')
MUTABLE_TAG = re.compile(r'uses:\s*[\w./-]+@v[\w.-]+')


@tag('CI')
class TestWorkflowActionPins(SimpleTestCase):
    def test_workflows_do_not_use_mutable_action_tags(self):
        violations = []
        for workflow_path in sorted(WORKFLOWS_DIR.glob('*.yml')):
            for line_number, line in enumerate(
                workflow_path.read_text(encoding='utf-8').splitlines(),
                start=1,
            ):
                if 'uses:' not in line:
                    continue
                if MUTABLE_TAG.search(line):
                    violations.append(f'{workflow_path.name}:{line_number}: {line.strip()}')
                elif '@' in line and not IMMUTABLE_SHA.search(line):
                    violations.append(
                        f'{workflow_path.name}:{line_number}: missing immutable SHA in {line.strip()}'
                    )
        self.assertEqual(violations, [])
