from django.test import tag
from django.urls import reverse

from common.utils.helpers import USER_MODEL
from crm.models import CrmEmail
from crm.models import Request
from tests.base_test_classes import BaseTestCase

# manage.py test tests.crm.views.test_print_object --keepdb


@tag('TestCase')
class TestPrintObjectView(BaseTestCase):
    """The print previews must enforce the same permissions as the admin."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        username_list = (
            "Andrew.Manager.Global",        # manager, Global sales
            "Marina.Co-worker.Global",      # co-worker: no view permissions
            "Masha.Co-worker.Bookkeeping",  # co-worker, Bookkeeping
        )
        users = USER_MODEL.objects.filter(username__in=username_list)
        cls.manager = users.get(username="Andrew.Manager.Global")
        cls.co_worker = users.get(username="Marina.Co-worker.Global")
        cls.bookkeeper = users.get(username="Masha.Co-worker.Bookkeeping")
        cls.bookkeeping_dept = cls.bookkeeper.groups.get(name='Bookkeeping')

        cls.request = Request.objects.create(
            request_for='print permission test',
            first_name='Tom',
            email='tom@example.com',
            owner=cls.manager,
            department_id=cls.manager.groups.filter(
                department__isnull=False).first().id
        )
        cls.email = CrmEmail.objects.create(
            subject='print permission test',
            content='test content',
            to='tom@example.com',
            owner=cls.manager,
            department_id=cls.request.department_id
        )
        # a request that belongs to another department
        cls.foreign_request = Request.objects.create(
            request_for='foreign department request',
            first_name='Jerry',
            email='jerry@example.com',
            owner=cls.co_worker,
            department_id=cls.bookkeeping_dept.id
        )

    def setUp(self):
        print("Run Test Method:", self._testMethodName)

    def test_print_request_allowed_for_authorized_user(self):
        self.client.force_login(self.manager)
        url = reverse('print_request', args=(self.request.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_print_email_allowed_for_authorized_user(self):
        self.client.force_login(self.manager)
        url = reverse('print_email', args=(self.email.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_print_request_denied_without_view_permission(self):
        # a co-worker has no crm.view_request permission
        self.client.force_login(self.co_worker)
        url = reverse('print_request', args=(self.request.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_print_email_denied_without_view_permission(self):
        # a co-worker has no crm.view_crmemail permission
        self.client.force_login(self.co_worker)
        url = reverse('print_email', args=(self.email.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_print_request_from_another_department_not_found(self):
        # a manager of Global sales must not see Bookkeeping objects
        self.client.force_login(self.manager)
        url = reverse('print_request', args=(self.foreign_request.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
