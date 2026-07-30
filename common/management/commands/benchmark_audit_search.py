"""Benchmark audit-log admin search latency and query shape."""

from __future__ import annotations

import json
import time
from pathlib import Path

from django.contrib import admin
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.db import connection
from django.test import RequestFactory
from django.test.utils import CaptureQueriesContext

from common.admin import LogEntryAdmin
from tests.common.log_entry_parity_seed import seed_benchmark_log_entries

DEFAULT_TERMS = (
    'Email',
    'ID100001',
    'North Region',
    '',
    'xyzzy_nonexistent',
)
SAFETY_ROW_THRESHOLD = 10_000


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int(round((pct / 100) * (len(ordered) - 1)))))
    return ordered[index]


class Command(BaseCommand):
    help = 'Benchmark LogEntry audit search latency and emit a JSON report.'

    def add_arguments(self, parser):
        parser.add_argument('--rows', type=int, default=500)
        parser.add_argument('--iterations', type=int, default=5)
        parser.add_argument(
            '--terms',
            default=','.join(DEFAULT_TERMS),
            help='Comma-separated search terms to benchmark.',
        )
        parser.add_argument('--output', default='-')
        parser.add_argument(
            '--force',
            action='store_true',
            help=(
                f'Allow seeding when django_admin_log already has more than '
                f'{SAFETY_ROW_THRESHOLD} rows.'
            ),
        )

    def handle(self, *args, **options):
        row_count = options['rows']
        iterations = options['iterations']
        terms = tuple(
            term
            for raw in options['terms'].split(',')
            if (term := raw.strip()) or raw == ''
        )
        output_path = options['output']

        existing_rows = admin.models.LogEntry.objects.count()
        if existing_rows > SAFETY_ROW_THRESHOLD and not options['force']:
            raise CommandError(
                f'Refusing to seed: django_admin_log has {existing_rows} rows '
                f'(threshold {SAFETY_ROW_THRESHOLD}). Re-run with --force.'
            )

        if row_count:
            seed_benchmark_log_entries(row_count)

        queryset = admin.models.LogEntry.objects.all()
        model_admin = LogEntryAdmin(admin.models.LogEntry, admin.site)
        request = RequestFactory().get('/')

        term_reports = []
        for term in terms:
            latencies_ms = []
            matched_rows = 0
            query_count = 0
            explain_output = ''
            for _ in range(iterations):
                start = time.perf_counter()
                with CaptureQueriesContext(connection) as queries:
                    filtered, _ = model_admin.get_search_results(
                        request,
                        queryset,
                        term,
                    )
                    matched_rows = filtered.count()
                    explain_output = filtered.explain()
                    query_count = len(queries)
                latencies_ms.append((time.perf_counter() - start) * 1000)

            term_reports.append(
                {
                    'term_length': len(term),
                    'matched_rows': matched_rows,
                    'query_count': query_count,
                    'latency_ms': {
                        'p50': round(_percentile(latencies_ms, 50), 3),
                        'p95': round(_percentile(latencies_ms, 95), 3),
                        'p99': round(_percentile(latencies_ms, 99), 3),
                    },
                    'explain': explain_output,
                },
            )

        try:
            database_version = connection.get_server_version()
        except (NotImplementedError, AttributeError):
            database_version = connection.vendor

        report = {
            'database_vendor': connection.vendor,
            'database_version': database_version,
            'seeded_rows': row_count,
            'table_rows_after_seed': admin.models.LogEntry.objects.count(),
            'iterations': iterations,
            'terms': term_reports,
        }

        payload = json.dumps(report, indent=2, sort_keys=True)
        if output_path == '-':
            self.stdout.write(payload)
        else:
            Path(output_path).write_text(payload + '\n', encoding='utf-8')
