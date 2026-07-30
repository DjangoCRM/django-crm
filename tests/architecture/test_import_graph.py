"""Import-graph guardrail tests and graph-builder unit tests."""

from __future__ import annotations

import json
from pathlib import Path

from django.test import SimpleTestCase

from tests.architecture.import_graph import ImportEdge
from tests.architecture.import_graph import build_layering_violations
from tests.architecture.import_graph import helpers_fan_in
from tests.architecture.import_graph import parse_import_edges

BASELINE_FILE = Path(__file__).resolve().parent / 'import_graph_baseline.json'
FIXTURES_ROOT = Path(__file__).resolve().parent / 'fixtures' / 'import_graph'


class ImportGraphBuilderTests(SimpleTestCase):
    def test_parse_plain_and_from_imports(self):
        module_path = FIXTURES_ROOT / 'plain_imports' / 'sample.py'
        edges = parse_import_edges(module_path, source_app='common')
        keys = {(edge.imported_module, edge.source_app, edge.target_app) for edge in edges}
        self.assertIn(('crm.models', 'common', 'crm'), keys)
        self.assertIn(('tasks.models', 'common', 'tasks'), keys)

    def test_parse_relative_import_is_ignored_without_module(self):
        module_path = FIXTURES_ROOT / 'relative_imports' / 'sample.py'
        edges = parse_import_edges(module_path, source_app='common')
        self.assertEqual(edges, [])

    def test_parse_aliased_import(self):
        module_path = FIXTURES_ROOT / 'aliased_imports' / 'sample.py'
        edges = parse_import_edges(module_path, source_app='common')
        self.assertEqual(
            edges[0].imported_module,
            'analytics.models',
        )


class ImportGraphBaselineTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.baseline = json.loads(BASELINE_FILE.read_text(encoding='utf-8'))
        cls.baseline_keys = {
            (entry['importing_file'], entry['imported_module'])
            for entry in cls.baseline['violations']
        }

    def test_no_new_layering_violations(self):
        current = build_layering_violations()
        current_keys = {edge.as_key() for edge in current}
        new_violations = current_keys - self.baseline_keys
        self.assertEqual(
            new_violations,
            set(),
            msg='New layering violations detected: '
            + ', '.join(f'{file} -> {module}' for file, module in sorted(new_violations)),
        )

    def test_baseline_has_no_stale_violations(self):
        current = build_layering_violations()
        current_keys = {edge.as_key() for edge in current}
        stale = self.baseline_keys - current_keys
        self.assertEqual(
            stale,
            set(),
            msg='Remove stale baseline entries: '
            + ', '.join(f'{file} -> {module}' for file, module in sorted(stale)),
        )

    def test_helpers_fan_in_matches_baseline(self):
        self.assertEqual(len(helpers_fan_in()), self.baseline['helpers_fan_in_count'])
