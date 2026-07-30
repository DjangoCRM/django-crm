"""Characterization tests for query helpers re-exported from helpers.

Existing JSON fixtures from ``tests/base_test_classes.py`` are reused.
"""

from django.test import tag

from common import queries
from common.utils import helpers
from tests.base_test_classes import BaseTestCase


@tag('TestCase')
class HelpersQueriesCharacterizationTests(BaseTestCase):
    def test_add_phone_q_params_matches_queries_module(self):
        phone = '+0 (123) 345-67.89'
        self.assertEqual(
            str(helpers.add_phone_q_params(phone)),
            str(queries.add_phone_q_params(phone)),
        )
        self.assertEqual(
            str(helpers.add_phone_q_params('1234')),
            str(queries.add_phone_q_params('1234')),
        )

    def test_get_active_users_matches_queries_module(self):
        helper_pks = list(helpers.get_active_users().order_by('pk').values_list('pk', flat=True))
        query_pks = list(queries.get_active_users().order_by('pk').values_list('pk', flat=True))
        self.assertEqual(helper_pks, query_pks)

    def test_get_manager_departments_matches_queries_module(self):
        helper_pks = list(
            helpers.get_manager_departments().order_by('pk').values_list('pk', flat=True),
        )
        query_pks = list(
            queries.get_manager_departments().order_by('pk').values_list('pk', flat=True),
        )
        self.assertEqual(helper_pks, query_pks)

    def test_get_department_id_matches_queries_module_for_fixture_users(self):
        usernames = (
            'Adam.Admin',
            'Garry.Chief',
            'Andrew.Manager.Global',
            'Eve.Superoperator.Co-worker',
            'Sergey.Co-worker.Head.Bookkeeping',
        )
        for username in usernames:
            user = helpers.USER_MODEL.objects.get(username=username)
            with self.subTest(username=username):
                self.assertEqual(
                    helpers.get_department_id(user),
                    queries.get_department_id(user),
                )

    def test_annotate_chat_sql_shape_matches_queries_module(self):
        from django.contrib.auth.models import AnonymousUser
        from django.test import RequestFactory
        from crm.models import Contact

        user = helpers.USER_MODEL.objects.get(username='Andrew.Manager.Global')
        request = RequestFactory().get('/')
        request.user = user
        request.user.is_chief = False
        queryset = Contact.objects.all()
        helper_sql = str(helpers.annotate_chat(request, queryset).query)
        query_sql = str(queries.annotate_chat(request, queryset).query)
        self.assertEqual(helper_sql, query_sql)
        self.assertIn('EXISTS', helper_sql.upper())

    def test_add_chat_context_mutates_extra_context_identically(self):
        from django.contrib.contenttypes.models import ContentType
        from django.test import RequestFactory
        from crm.models import Contact

        user = helpers.USER_MODEL.objects.get(username='Adam.Admin')
        request = RequestFactory().get('/')
        request.user = user
        content_type = ContentType.objects.get_for_model(Contact)
        helper_context = {}
        query_context = {}
        helpers.add_chat_context(request, helper_context, '999999', content_type)
        queries.add_chat_context(request, query_context, '999999', content_type)
        self.assertEqual(helper_context, query_context)
