"""Import-graph guardrail tests and graph-builder unit tests."""

from __future__ import annotations

import json
from pathlib import Path

from django.test import SimpleTestCase

from tests.architecture.allowed_exceptions import AllowedException
from tests.architecture.import_graph import HELPERS_RELOCATED_SYMBOLS
from tests.architecture.import_graph import SHARED_MODULE_FAN_IN_CEILING
from tests.architecture.import_graph import build_layering_violations
from tests.architecture.import_graph import helpers_fan_in
from tests.architecture.import_graph import load_allowed_exceptions
from tests.architecture.import_graph import parse_import_edges
from tests.architecture.import_graph import relocated_helpers_symbol_importers
from tests.architecture.import_graph import shared_module_fan_in
from tests.architecture.layering_rules import CORE_LAYERING_RULES
from tests.architecture.layering_rules import core_rule_violations

FIXTURES_ROOT = Path(__file__).resolve().parent / 'fixtures' / 'import_graph'
METRICS_FILE = Path(__file__).resolve().parents[2] / 'docs' / 'layering-metrics.json'


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


class LayeringRuleFixtureTests(SimpleTestCase):
    def test_common_feature_rule_flags_fixture_violation(self):
        module_path = FIXTURES_ROOT / 'plain_imports' / 'sample.py'
        edges = parse_import_edges(module_path, source_app='common')
        violations = core_rule_violations(edges)
        self.assertTrue(violations['common_feature_isolation'])

    def test_compliant_fixture_has_no_core_violations(self):
        module_path = FIXTURES_ROOT / 'compliant' / 'sample.py'
        edges = parse_import_edges(module_path, source_app='common')
        violations = core_rule_violations(edges)
        self.assertEqual(
            {rule_id: edges for rule_id, edges in violations.items() if edges},
            {},
        )


class LayeringGateTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.current_edges = build_layering_violations()
        cls.current_keys = {edge.as_key() for edge in cls.current_edges}
        cls.allowed = load_allowed_exceptions()
        cls.allowed_keys = {entry.as_key() for entry in cls.allowed}

    def test_core_layering_rules_have_zero_violations(self):
        violations = core_rule_violations(self.current_edges)
        failures = {
            rule_id: edges
            for rule_id, edges in violations.items()
            if edges
        }
        messages = []
        for rule_id, edges in failures.items():
            rule = next(item for item in CORE_LAYERING_RULES if item.rule_id == rule_id)
            messages.append(
                f'{rule.description}: '
                + ', '.join(f'{edge.importing_file} -> {edge.imported_module}' for edge in edges),
            )
        self.assertEqual(failures, {}, msg='; '.join(messages))

    def test_every_cross_app_edge_is_explicitly_allowed(self):
        unexpected = self.current_keys - self.allowed_keys
        self.assertEqual(
            unexpected,
            set(),
            msg='Unjustified cross-app imports: '
            + ', '.join(f'{file} -> {module}' for file, module in sorted(unexpected)),
        )

    def test_allowed_exceptions_have_no_stale_entries(self):
        stale = self.allowed_keys - self.current_keys
        self.assertEqual(
            stale,
            set(),
            msg='Remove stale allow-list entries: '
            + ', '.join(f'{file} -> {module}' for file, module in sorted(stale)),
        )

    def test_relocated_helpers_symbols_have_zero_direct_importers(self):
        importers = relocated_helpers_symbol_importers()
        self.assertEqual(
            importers,
            [],
            msg='Direct imports of relocated helpers symbols remain: '
            + ', '.join(f'{file} -> {symbol}' for file, symbol in importers),
        )

    def test_shared_module_fan_in_respects_documented_ceiling(self):
        over_limit = {
            module: importers
            for module, importers in shared_module_fan_in().items()
            if len(importers) > SHARED_MODULE_FAN_IN_CEILING
        }
        self.assertEqual(
            over_limit,
            {},
            msg='Shared modules above fan-in ceiling: '
            + ', '.join(
                f'{module} ({len(importers)} importers)'
                for module, importers in sorted(over_limit.items())
            ),
        )

    def test_metrics_summary_matches_current_graph(self):
        metrics = json.loads(METRICS_FILE.read_text(encoding='utf-8'))
        self.assertEqual(metrics['after']['cross_app_violation_count'], len(self.current_edges))
        self.assertEqual(
            metrics['after']['helpers_module_fan_in_count'],
            len(helpers_fan_in()),
        )
        self.assertEqual(
            metrics['after']['relocated_helpers_symbol_importers'],
            len(relocated_helpers_symbol_importers()),
        )
        self.assertEqual(
            metrics['after']['helpers_relocated_symbol_count'],
            len(HELPERS_RELOCATED_SYMBOLS),
        )
