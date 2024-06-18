from django.test import tag
from django.urls import reverse

from crm.models import Lead
from common.utils.helpers import get_department_id
from common.utils.helpers import USER_MODEL
from tests.base_test_classes import BaseTestCase
from tests.utils.helpers import get_country_instance
from tests.utils.helpers import get_adminform_initials

# python manage.py test tests.crm.test_lead --keepdb


@tag('TestCase')
class TestLead(BaseTestCase):
    """Test Lead"""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.country = get_country_instance()
        username_list = ("Adam.Admin",
                         "Darian.Manager.Co-worker.Head.Global")
        users = USER_MODEL.objects.filter(
            username__in=username_list)
        cls.user = users.get(
            username="Darian.Manager.Co-worker.Head.Global")
        cls.admin = users.get(username="Adam.Admin")
        department_id = get_department_id(cls.user)

        cls.lead_data = {
            'first_name': "John",
            'last_name': "Morgan",
            'email': "John@company.com",
            'company_name': 'Test Company LLC',
            'country': str(cls.country.id),
            'owner': str(cls.user.id),
            'department_id': department_id
        }
        cls.add_url = reverse("site:crm_lead_add")
        cls.changelist_url = reverse("site:crm_lead_changelist")

    def setUp(self):
        print("Run Test Method:", self._testMethodName)
        self.client.force_login(self.user)

    def test_add_lead(self):
        self.response = self.client.get(self.add_url, follow=True)
        self.assertEqual(self.response.status_code, 200,
                         self.response.reason_phrase)
        data = get_adminform_initials(self.response)
        data.update(self.lead_data)
        data['phone'] = "+0 (123) 345-67.89"
        response = self.client.post(self.add_url, data, follow=True)
        self.assertNoFormErrors(response)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertEqual(response.redirect_chain[0][0], self.changelist_url)
        # open lead changlist
        self.response = self.client.get(self.changelist_url, follow=True)
        self.assertEqual(self.response.status_code, 200,
                         self.response.reason_phrase)

    def test_change_lead(self):
        lead_data = self.lead_data.copy()
        lead_data['company_name'] = 'New Company LLC'
        lead_data['owner'] = self.user
        lead_data['country'] = self.country
        lead = Lead.objects.create(**lead_data)
        change_url = reverse("site:crm_lead_change", args=(lead.id,))
        response = self.client.get(change_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        data['description'] = 'description'
        data['city_name'] = "City name"
        response = self.client.post(change_url, data, follow=True)
        self.assertNoFormErrors(response)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertEqual(response.redirect_chain[0][0], self.changelist_url)

    def test_fix_lead_by_admin(self):
        lead_data = self.lead_data.copy()
        lead_data['company_name'] = 'New Company LLC'
        lead_data['owner'] = self.user
        lead_data['country'] = self.country
        lead = Lead.objects.create(**lead_data)

        self.client.force_login(self.admin)
        change_url = reverse("admin:crm_lead_change", args=(lead.id,))
        response = self.client.get(change_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        data['description'] = 'description'
        data['city_name'] = "City name"
        response = self.client.post(change_url, data, follow=True)
        self.assertNoFormErrors(response)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        changelist_url = reverse("admin:crm_lead_changelist")
        self.assertEqual(response.redirect_chain[0][0], changelist_url)
