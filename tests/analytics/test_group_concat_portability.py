"""
Portable GroupConcat aggregate tests (WO-018).

Covers SQL compilation per database vendor, aggregate semantics on seeded
fixture data, and the Income Stat admin changelist integration boundary.
"""
from django.contrib.auth.models import Group
from django.db import connection
from django.db.models import CharField
from django.db.utils import NotSupportedError
from django.test import tag
from django.urls import reverse

from analytics.utils.helpers import GroupConcat
from common.queries import get_department_id
from common.utils.helpers import USER_MODEL
from crm.models import Currency
from crm.models import Payment
from tests.base_test_classes import BaseTestCase
from tests.crm.test_deal import get_contact_request
from tests.crm.test_deal import get_test_deal
from tests.crm.test_request_methods import populate_db
from tests.fixtures.group_concat_data import GROUP_CONCAT_ORDER_NUMBERS
from tests.fixtures.group_concat_data import seed_group_concat_payments


# python manage.py test tests.analytics.test_group_concat_portability --keepdb


def _group_concat_query(**kwargs):
    return Payment.objects.values('deal_id').annotate(
        aggregated=GroupConcat('order_number', **kwargs)
    )


def _compiled_sql(**kwargs):
    query = _group_concat_query(**kwargs).query
    compiler = query.get_compiler(using=connection.alias)
    return compiler.as_sql()


def _normalize_concat(value, separator=', '):
    if value in (None, ''):
        return value
    parts = [part for part in value.split(separator) if part]
    return separator.join(sorted(parts))


@tag('Analytics')
class TestGroupConcatCompilation(BaseTestCase):
    """Assert vendor-appropriate SQL is emitted for GroupConcat."""

    def setUp(self):
        print(' Run Test Method:', self._testMethodName)

    def test_output_field_is_charfield(self):
        aggregate = GroupConcat('order_number')
        self.assertIsInstance(aggregate.output_field, CharField)

    def test_mysql_compilation(self):
        if connection.vendor != 'mysql':
            self.skipTest('MySQL-only SQL assertion')
        sql, params = _compiled_sql()
        self.assertIn('GROUP_CONCAT', sql)
        self.assertIn('SEPARATOR', sql)
        self.assertIn('%s', sql)
        self.assertIn(', ', params)

    def test_postgresql_compilation(self):
        if connection.vendor != 'postgresql':
            self.skipTest('PostgreSQL-only SQL assertion')
        sql, params = _compiled_sql()
        self.assertIn('STRING_AGG', sql)
        self.assertIn('CAST', sql.upper())
        self.assertNotIn('SEPARATOR', sql)
        self.assertIn(', ', params)

    def test_sqlite_compilation(self):
        if connection.vendor != 'sqlite':
            self.skipTest('SQLite-only SQL assertion')
        sql, params = _compiled_sql()
        self.assertIn('group_concat', sql.lower())
        self.assertNotIn('SEPARATOR', sql)
        self.assertIn(', ', params)

    def test_sqlite_distinct_custom_separator_not_supported(self):
        if connection.vendor != 'sqlite':
            self.skipTest('SQLite-only limitation assertion')
        aggregate = GroupConcat('order_number', distinct=True, separator='|')
        query = Payment.objects.values('deal_id').annotate(
            aggregated=aggregate
        ).query
        compiler = query.get_compiler(using=connection.alias)
        with self.assertRaises(NotSupportedError) as context:
            compiler.as_sql()
        self.assertIn('SQLite', str(context.exception))
        self.assertIn('DISTINCT', str(context.exception))


@tag('Analytics')
class TestGroupConcatSemantics(BaseTestCase):
    """Exercise aggregate results on deterministic fixture rows."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        populate_db(cls)
        cls.contact_request = get_contact_request()
        cls.co_owner = USER_MODEL.objects.get(
            username='Darian.Manager.Co-worker.Head.Global'
        )
        cls.department = Group.objects.get(id=get_department_id(cls.owner))
        cls.currency = Currency.objects.first()
        cls.deal = get_test_deal(cls)
        seed_group_concat_payments(cls.deal, cls.currency)

    def setUp(self):
        print(' Run Test Method:', self._testMethodName)

    def test_multiple_rows_concatenated(self):
        result = _group_concat_query().get(deal_id=self.deal.id)['aggregated']
        expected = _normalize_concat(', '.join(GROUP_CONCAT_ORDER_NUMBERS))
        self.assertEqual(_normalize_concat(result), expected)

    def test_single_row(self):
        Payment.objects.filter(deal=self.deal, order_number='ORD-100').delete()
        result = _group_concat_query().get(deal_id=self.deal.id)['aggregated']
        self.assertEqual(_normalize_concat(result), 'ORD-200, ORD-300')

    def test_empty_group_returns_null(self):
        Payment.objects.filter(deal=self.deal).delete()
        queryset = _group_concat_query().filter(deal_id=self.deal.id)
        self.assertFalse(queryset.exists())

    def test_distinct_values(self):
        Payment.objects.create(
            deal=self.deal,
            status=Payment.RECEIVED,
            amount=50,
            currency=self.currency,
            order_number='ORD-100',
        )
        if connection.vendor == 'sqlite':
            aggregate = GroupConcat('order_number', distinct=True, separator=',')
        else:
            aggregate = GroupConcat('order_number', distinct=True)
        result = Payment.objects.filter(deal=self.deal).values('deal_id').annotate(
            aggregated=aggregate
        ).get(deal_id=self.deal.id)['aggregated']
        self.assertEqual(
            set(part.strip() for part in _normalize_concat(result).split(',')),
            {'ORD-100', 'ORD-200', 'ORD-300'},
        )

    def test_non_text_source_column(self):
        result = Payment.objects.filter(deal=self.deal).values('deal_id').annotate(
            aggregated=GroupConcat('amount')
        ).get(deal_id=self.deal.id)['aggregated']
        amounts = sorted(part.strip() for part in result.split(',') if part.strip())
        self.assertEqual(amounts, ['100', '101', '102'])


@tag('Analytics')
class TestIncomeStatGroupConcatIntegration(BaseTestCase):
    """Income Stat changelist executes GroupConcat through the admin boundary."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        populate_db(cls)
        cls.contact_request = get_contact_request()
        cls.co_owner = USER_MODEL.objects.get(
            username='Darian.Manager.Co-worker.Head.Global'
        )
        cls.department = Group.objects.get(id=get_department_id(cls.owner))
        cls.currency = Currency.objects.first()
        cls.deal = get_test_deal(cls)
        seed_group_concat_payments(
            cls.deal,
            cls.currency,
            status=Payment.GUARANTEED,
        )
        cls.chief = USER_MODEL.objects.get(username='Garry.Chief')

    def setUp(self):
        print(' Run Test Method:', self._testMethodName)
        self.client.force_login(self.chief)

    def test_incomestat_changelist_renders_with_group_concat(self):
        url = reverse('site:analytics_incomestat_changelist')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        content = response.content.decode()
        for order_number in GROUP_CONCAT_ORDER_NUMBERS:
            self.assertIn(order_number, content)
