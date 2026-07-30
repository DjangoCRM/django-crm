"""Tests for benchmark_audit_search management command."""

from __future__ import annotations

import io
import json
import time

from django.contrib import admin
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connection
from django.test import RequestFactory
from django.test.utils import CaptureQueriesContext
from django.test import tag

from common.admin import LogEntryAdmin
from tests.base_test_classes import BaseTestCase
from tests.common.log_entry_parity_seed import seed_benchmark_log_entries


@tag('TestCase')
class BenchmarkAuditSearchCommandTests(BaseTestCase):
    def test_command_emits_well_formed_json_report(self):
        stdout = io.StringIO()
        call_command(
            'benchmark_audit_search',
            rows=50,
            iterations=2,
            terms='Email,xyzzy',
            stdout=stdout,
        )
        report = json.loads(stdout.getvalue())
        self.assertEqual(report['seeded_rows'], 50)
        self.assertIn('database_vendor', report)
        self.assertEqual(len(report['terms']), 2)
        for term in report['terms']:
            self.assertIn('latency_ms', term)
            self.assertGreaterEqual(term['latency_ms']['p50'], 0)
            self.assertIn('query_count', term)
            self.assertIn('explain', term)

    def test_command_refuses_large_existing_tables_without_force(self):
        seed_benchmark_log_entries(10_001, start_pk=200_000)
        with self.assertRaises(CommandError) as ctx:
            call_command('benchmark_audit_search', rows=10)
        self.assertIn('--force', str(ctx.exception))


@tag('TestCase')
class AuditSearchScalingAssertionTests(BaseTestCase):
    def test_query_count_is_stable_across_corpus_sizes(self):
        model_admin = LogEntryAdmin(admin.models.LogEntry, admin.site)
        request = RequestFactory().get('/')

        seed_benchmark_log_entries(1_000, start_pk=300_000)
        small_queryset = admin.models.LogEntry.objects.filter(pk__gte=300_000)
        with CaptureQueriesContext(connection) as small_queries:
            list(model_admin.get_search_results(request, small_queryset, 'Email')[0])
        small_count = len(small_queries)

        seed_benchmark_log_entries(9_000, start_pk=301_000)
        large_queryset = admin.models.LogEntry.objects.filter(pk__gte=300_000)
        with CaptureQueriesContext(connection) as large_queries:
            list(model_admin.get_search_results(request, large_queryset, 'Email')[0])
        large_count = len(large_queries)

        self.assertEqual(small_count, large_count)

    def test_latency_does_not_scale_linearly_with_row_count(self):
        model_admin = LogEntryAdmin(admin.models.LogEntry, admin.site)
        request = RequestFactory().get('/')

        seed_benchmark_log_entries(1_000, start_pk=400_000)
        small_queryset = admin.models.LogEntry.objects.filter(pk__gte=400_000)
        start = time.perf_counter()
        list(model_admin.get_search_results(request, small_queryset, 'Email')[0])
        small_ms = time.perf_counter() - start

        seed_benchmark_log_entries(9_000, start_pk=401_000)
        large_queryset = admin.models.LogEntry.objects.filter(pk__gte=400_000)
        start = time.perf_counter()
        list(model_admin.get_search_results(request, large_queryset, 'Email')[0])
        large_ms = time.perf_counter() - start

        self.assertLess(large_ms, small_ms * 20)
