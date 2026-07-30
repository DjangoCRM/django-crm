"""Unit tests for common.queries ORM helpers."""

from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.test import RequestFactory
from django.test import tag

from common.queries import add_chat_context
from common.queries import add_phone_q_params
from common.queries import annotate_chat
from common.queries import get_active_users
from common.queries import get_department_id
from common.queries import get_manager_departments
from common.utils.helpers import USER_MODEL
from crm.models import Contact
from tests.base_test_classes import BaseTestCase


@tag('TestCase')
class QueryHelperTests(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.users = {
            username: USER_MODEL.objects.get(username=username)
            for username in (
                'Adam.Admin',
                'Garry.Chief',
                'Andrew.Manager.Global',
                'Eve.Superoperator.Co-worker',
                'Sergey.Co-worker.Head.Bookkeeping',
            )
        }

    def test_add_phone_q_params_ignores_short_numbers(self):
        self.assertEqual(str(add_phone_q_params('1234')), str(Q()))

    def test_add_phone_q_params_builds_regex_for_long_numbers(self):
        query = add_phone_q_params('+1 (234) 567-8901')
        sql = str(query)
        self.assertIn('iregex', sql)
        self.assertIn('phone', sql)

    def test_get_active_users_excludes_inactive_and_non_staff(self):
        pks = set(get_active_users().values_list('pk', flat=True))
        inactive = USER_MODEL.objects.filter(is_active=False).values_list('pk', flat=True)
        non_staff = USER_MODEL.objects.filter(is_staff=False).values_list('pk', flat=True)
        self.assertFalse(pks.intersection(set(inactive)))
        self.assertFalse(pks.intersection(set(non_staff)))

    def test_get_department_id_for_fixture_roles(self):
        manager_department = get_department_id(self.users['Andrew.Manager.Global'])
        bookkeeper_department = get_department_id(
            self.users['Sergey.Co-worker.Head.Bookkeeping'],
        )
        self.assertIsNotNone(manager_department)
        self.assertIsNotNone(bookkeeper_department)
        self.assertNotEqual(manager_department, bookkeeper_department)
        self.assertIsNone(get_department_id(self.users['Adam.Admin']))

    def test_get_department_id_returns_none_for_anonymous_user(self):
        anonymous = AnonymousUser()
        self.assertIsNone(get_department_id(anonymous))

    def test_get_manager_departments_returns_departments_with_managers(self):
        department_pks = list(
            get_manager_departments().order_by('pk').values_list('pk', flat=True),
        )
        self.assertTrue(department_pks)

    def test_annotate_chat_adds_exists_annotations(self):
        request = RequestFactory().get('/')
        request.user = self.users['Andrew.Manager.Global']
        request.user.is_chief = False
        annotated = annotate_chat(request, Contact.objects.all())
        self.assertIn('is_chat', annotated.query.annotations)
        self.assertIn('is_unread_chat', annotated.query.annotations)

    def test_add_chat_context_defaults_to_no_chat(self):
        request = RequestFactory().get('/')
        request.user = self.users['Adam.Admin']
        content_type = ContentType.objects.get_for_model(Contact)
        context = {}
        add_chat_context(request, context, '424242', content_type)
        self.assertFalse(context['is_chat'])
        self.assertNotIn('is_unread_chat', context)
