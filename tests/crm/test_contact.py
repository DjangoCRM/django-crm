from django.test import tag
from django.urls import reverse

from crm.models import Company
from crm.models import Contact
from common.utils.helpers import get_department_id
from common.utils.helpers import USER_MODEL
from tests.base_test_classes import BaseTestCase
from tests.utils.helpers import get_adminform_initials

# python manage.py test tests.crm.test_contact --keepdb


@tag('TestCase')
class TestContact(BaseTestCase):
    """Test Contact"""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        username_list = ("Adam.Admin",
                         "Darian.Manager.Co-worker.Head.Global")
        users = USER_MODEL.objects.filter(
            username__in=username_list)
        cls.user = users.get(
            username="Darian.Manager.Co-worker.Head.Global")
        cls.admin = users.get(username="Adam.Admin")
        department_id = get_department_id(cls.user)
        cls.company = Company.objects.create(
            full_name="Test company",
            email="John@company.com",
            owner=cls.user,
            department_id=department_id
        )
        cls.contact_data = {
            'first_name': "John",
            'last_name': "Morgan",
            'email': "John@company.com",
            'company': str(cls.company.id),
            'owner': cls.user,
            'department_id': department_id
        }
        cls.add_url = reverse("site:crm_contact_add") + \
            f"?company={cls.company.id}"
        cls.changelist_url = reverse("site:crm_contact_changelist")

    def setUp(self):
        print("Run Test Method:", self._testMethodName)
        self.client.force_login(self.user)

    def test_add_contact(self):
        self.response = self.client.get(self.add_url, follow=True)
        self.assertEqual(self.response.status_code, 200,
                         self.response.reason_phrase)
        data = get_adminform_initials(self.response)
        data.update(self.contact_data)
        data['phone'] = "+0 (123) 345-67.89"
        response = self.client.post(self.add_url, data, follow=True)
        self.assertNoFormErrors(response)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertEqual(response.redirect_chain[0][0], self.changelist_url)
        # open contact changlist
        self.response = self.client.get(self.changelist_url, follow=True)
        self.assertEqual(self.response.status_code, 200,
                         self.response.reason_phrase)

    def test_change_contact(self):
        contact_data = self.contact_data.copy()
        contact_data['company'] = self.company
        contact = Contact.objects.create(**contact_data)
        change_url = reverse("site:crm_contact_change", args=(contact.id,))
        response = self.client.get(change_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        data['description'] = 'description'
        response = self.client.post(change_url, data, follow=True)
        self.assertNoFormErrors(response)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertEqual(response.redirect_chain[0][0], self.changelist_url)

    def test_fix_contact_by_admin(self):
        contact_data = self.contact_data.copy()
        contact_data['company'] = self.company
        contact = Contact.objects.create(**contact_data)
        self.client.force_login(self.admin)
        change_url = reverse("admin:crm_contact_change", args=(contact.id,))
        response = self.client.get(change_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        data['description'] = 'description'
        response = self.client.post(change_url, data, follow=True)
        self.assertNoFormErrors(response)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        changelist_url = reverse("admin:crm_contact_changelist")
        self.assertEqual(response.redirect_chain[0][0], changelist_url)
