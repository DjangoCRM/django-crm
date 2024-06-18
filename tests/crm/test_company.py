from django.test import tag
from django.urls import reverse

from crm.models import Company
from common.utils.helpers import get_department_id
from common.utils.helpers import USER_MODEL
from tests.base_test_classes import BaseTestCase
from tests.utils.helpers import get_adminform_initials, get_country_instance

# python manage.py test tests.crm.test_company --keepdb


@tag('TestCase')
class TestCompany(BaseTestCase):
    """Test add Company"""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.add_url = reverse("site:crm_company_add")
        cls.changelist_url = reverse("site:crm_company_changelist")
        cls.country = get_country_instance()
        username_list = ("Adam.Admin",
                         "Darian.Manager.Co-worker.Head.Global")
        users = USER_MODEL.objects.filter(
            username__in=username_list)
        cls.user = users.get(
            username="Darian.Manager.Co-worker.Head.Global")
        cls.admin = users.get(username="Adam.Admin")
        cls.company_data = {
            'full_name': "Test company",
            'email': "John@company.com",
        }

    def setUp(self):
        print("Run Test Method:", self._testMethodName)
        self.client.force_login(self.user)
        self.response = self.client.get(self.add_url, follow=True)

    def test_add_company(self):
        self.assertEqual(self.response.status_code, 200,
                         self.response.reason_phrase)
        data = get_adminform_initials(self.response)
        data.update(self.company_data)
        data['phone'] = "+0 (123) 345-67.89"
        response = self.client.post(self.add_url, data, follow=True)
        self.assertNoFormErrors(response)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertEqual(response.redirect_chain[0][0], self.changelist_url)
        # open company changlist
        self.response = self.client.get(self.changelist_url, follow=True)
        self.assertEqual(self.response.status_code, 200,
                         self.response.reason_phrase)

    def test_change_company(self):
        company = Company(**self.company_data)
        company.department_id = get_department_id(self.user)
        company.owner = self.user
        company.country = self.country
        company.save()
        change_url = reverse("site:crm_company_change", args=(company.id,))
        response = self.client.get(change_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertEqual(response.redirect_chain, [])
        data = get_adminform_initials(response)
        data['description'] = 'description'
        data['city_name'] = "City name"
        response = self.client.post(change_url, data, follow=True)
        self.assertNoFormErrors(response)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertEqual(response.redirect_chain[0][0], self.changelist_url)

    def test_fix_company_by_admin(self):
        company = Company(**self.company_data)
        company.department_id = get_department_id(self.user)
        company.owner = self.user
        company.country = self.country
        company.save()

        self.client.force_login(self.admin)
        change_url = reverse("admin:crm_company_change", args=(company.id,))
        response = self.client.get(change_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertEqual(response.redirect_chain, [])
        data = get_adminform_initials(response)
        data['description'] = 'description'
        data['city_name'] = "City name"
        response = self.client.post(change_url, data, follow=True)
        self.assertNoFormErrors(response)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        changelist_url = reverse("admin:crm_company_changelist")
        self.assertEqual(response.redirect_chain[0][0], changelist_url)
