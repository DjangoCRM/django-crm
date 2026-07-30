"""Unit and integration tests for sharedkernel audit search."""

from __future__ import annotations

from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory
from django.test import SimpleTestCase
from django.test import tag

from sharedkernel.search import AuditSearchService
from sharedkernel.search import ID_PREFIX_PATTERN
from sharedkernel.search import SearchSpecKind
from sharedkernel.search import SearchTermParser
from tests.base_test_classes import BaseTestCase
from tests.common.log_entry_parity import capture_search_pks
from tests.common.log_entry_parity import parity_queryset
from tests.common.log_entry_parity_seed import PARITY_LOG_ENTRY_PKS
from common.admin import LogEntryAdmin


class SearchTermParserTests(SimpleTestCase):
    def test_parse_empty_term(self):
        spec = SearchTermParser.parse('')
        self.assertEqual(spec.kind, SearchSpecKind.EMPTY)

    def test_parse_whitespace_only_term(self):
        spec = SearchTermParser.parse('   \n  ')
        self.assertEqual(spec.kind, SearchSpecKind.EMPTY)

    def test_parse_id_prefix_variants(self):
        for term in ('ID42', 'id42', 'Id9009'):
            with self.subTest(term=term):
                self.assertTrue(ID_PREFIX_PATTERN.match(term))
                spec = SearchTermParser.parse(term)
                self.assertEqual(spec.kind, SearchSpecKind.ID_LOOKUP)
                self.assertEqual(spec.id_suffix, term[2:])

    def test_parse_id_prefix_with_whitespace(self):
        spec = SearchTermParser.parse('id 9009')
        self.assertEqual(spec.kind, SearchSpecKind.ID_LOOKUP)
        self.assertEqual(spec.id_suffix, ' 9009')

    def test_parse_free_text_tokens(self):
        spec = SearchTermParser.parse('North Region')
        self.assertEqual(spec.kind, SearchSpecKind.FREE_TEXT)
        self.assertEqual(spec.tokens, ('North', 'Region'))


@tag('TestCase')
class AuditSearchServiceTests(BaseTestCase):
    fixtures = BaseTestCase.fixtures + ('log_entries_parity.json',)

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        admin.models.LogEntry.objects.exclude(
            pk__in=PARITY_LOG_ENTRY_PKS,
        ).delete()

    def test_empty_term_returns_queryset_unchanged(self):
        queryset = parity_queryset()
        filtered, may_have_duplicates = AuditSearchService.search(queryset, '   ')
        self.assertEqual(
            list(filtered.order_by('pk').values_list('pk', flat=True)),
            list(queryset.order_by('pk').values_list('pk', flat=True)),
        )
        self.assertFalse(may_have_duplicates)

    def test_sql_shape_uses_portable_predicates_only(self):
        queryset = parity_queryset()
        filtered, _ = AuditSearchService.search(queryset, 'Email')
        sql = str(filtered.query).upper()
        self.assertNotIn('GROUP_CONCAT', sql)
        self.assertNotIn('STRING_AGG', sql)
        self.assertNotIn('MATCH', sql)
        self.assertNotIn('SEPARATOR', sql)
        self.assertTrue('LIKE' in sql or 'CONTAIN' in sql or '=' in sql)


@tag('TestCase')
class AuditSearchServiceParityTests(BaseTestCase):
    fixtures = BaseTestCase.fixtures + ('log_entries_parity.json',)

    SEARCH_CASES = (
        ('Acme', []),
        ('Email', [9002]),
        ('phone', [9003]),
        ('ID9009', [9009]),
        ('North Region', [9008]),
        ('', sorted(PARITY_LOG_ENTRY_PKS)),
        ('xyzzy_nonexistent', []),
        ('100%', [9006]),
        ('field_name', [9007]),
        ('café', [9005, 9012]),
        ('billing address', [9011]),
        ('naïve', [9005, 9012]),
    )

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        admin.models.LogEntry.objects.exclude(
            pk__in=PARITY_LOG_ENTRY_PKS,
        ).delete()
        cls.request = RequestFactory().get('/')

    def setUp(self):
        self.model_admin = LogEntryAdmin(admin.models.LogEntry, AdminSite())

    def test_service_matches_admin_parity_contract(self):
        queryset = parity_queryset()
        for term, expected_admin_pks in self.SEARCH_CASES:
            with self.subTest(term=term):
                admin_pks, admin_distinct = capture_search_pks(
                    self.model_admin,
                    self.request,
                    term,
                    queryset,
                )
                service_pks, service_distinct = AuditSearchService.search(
                    queryset,
                    term,
                )
                service_pks = sorted(service_pks.values_list('pk', flat=True))
                if term == '':
                    self.assertFalse(service_distinct)
                else:
                    self.assertTrue(service_distinct)
                self.assertEqual(service_pks, admin_pks)
                self.assertEqual(service_pks, expected_admin_pks)
