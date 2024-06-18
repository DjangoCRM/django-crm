from django.test import RequestFactory
from django.test import tag
from django.urls import reverse
from common.utils.helpers import get_today
from common.utils.helpers import USER_MODEL
from crm.utils.make_massmail_form import get_massmail_form
from crm.utils.make_massmail_form import MassmailFormBase
from crm.models import Company
from crm.models import Contact
from crm.models import Country
from crm.models import ClientType
from crm.models import Industry
from tests.base_test_classes import BaseTestCase

# manage.py test tests.crm.utils.test_make_massmail_form --keepdb


@tag('TestCase')
class TestmakeMassmailForm(BaseTestCase):
    """Test make massmail form"""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.factory = RequestFactory()
        cls.owner = USER_MODEL.objects.get(username="Andrew.Manager.Global")

    def setUp(self):
        print("Run Test Method:", self._testMethodName)

    def test_account(self):
        url = reverse("site:crm_company_changelist")
        request = self.factory.get(url)
        request.user = self.owner
        form = get_massmail_form(request, Company)
        self.get_test(form)

    def test_contact(self):
        url = reverse("site:crm_contact_changelist")
        request = self.factory.get(url)
        request.user = self.owner
        form = get_massmail_form(request, Contact)
        self.get_test(form)

    def get_test(self, form):
        self.assertEqual(MassmailFormBase, form)
        self.assertEqual(Country, form.base_fields['countries'].queryset.model)
        self.assertEqual(Industry, form.base_fields['industries'].queryset.model)
        self.assertEqual(ClientType, form.base_fields['types'].queryset.model)
        self.assertEqual(get_today(), form.base_fields['before'].initial)
