from django.test import tag
from django.urls import reverse

from common.utils.helpers import get_department_id
from common.utils.helpers import USER_MODEL
from crm.models import CrmEmail
from crm.models import Request
from tests.base_test_classes import BaseTestCase

# manage.py test tests.crm.views.test_print_views --keepdb


@tag('TestCase')
class TestPrintViews(BaseTestCase):
    """The print views apply the same permission checks as the CRM site."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.owner = USER_MODEL.objects.get(username="Andrew.Manager.Global")
        cls.no_access_user = USER_MODEL.objects.get(username="Nadia.Storekeeper")
        department_id = get_department_id(cls.owner)
        cls.eml = CrmEmail.objects.create(
            to='sale@crm.com',
            from_field='customer@example.com',
            subject='Print test inquiry',
            content='Hello!',
            incoming=True,
            owner=cls.owner,
            department_id=department_id,
        )
        cls.req = Request.objects.create(
            request_for='Print test request',
            first_name='Tom',
            email='Tom@testcompany.com',
            owner=cls.owner,
            department_id=department_id,
        )
        cls.urls = (
            reverse('print_email', args=(cls.eml.id,)),
            reverse('print_request', args=(cls.req.id,)),
        )

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

    def test_owner_can_print(self):
        self.client.force_login(self.owner)
        for url in self.urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, url)

    def test_user_without_permission_cannot_print(self):
        self.client.force_login(self.no_access_user)
        for url in self.urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 403, url)

    def test_nonexistent_object_returns_404(self):
        self.client.force_login(self.owner)
        for name in ('print_email', 'print_request'):
            response = self.client.get(reverse(name, args=(2147483647,)))
            self.assertEqual(response.status_code, 404, name)
