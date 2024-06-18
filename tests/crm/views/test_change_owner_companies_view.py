from random import random
from django.test import tag
from django.urls import reverse
from crm.models import Company
from crm.models import Contact
from crm.models import Country
from tests.base_test_classes import BaseTestCase
from common.utils.helpers import get_department_id
from common.utils.helpers import USER_MODEL
from common.utils.helpers import get_today

# manage.py test tests.crm.views.test_change_owner_companies_view --keepdb
# manage.py test --tag=TestCase --keepdb


@tag('TestCase')
class TestChangeOwnerView(BaseTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.country = Country.objects.first()
        username_list = ("Andrew.Manager.Global",
                         "Darian.Manager.Co-worker.Head.Global", "Adam.Admin")
        users = USER_MODEL.objects.filter(
            username__in=username_list)
        cls.owner = users.get(username="Andrew.Manager.Global")
        cls.new_owner = users.get(
            username="Darian.Manager.Co-worker.Head.Global")
        cls.admin = users.get(username="Adam.Admin")
        cls.department_id = get_department_id(cls.owner)
        cls.description = str(int(random() * 1E5))

    def setUp(self):
        print("Run Test Method:", self._testMethodName)
        self.client.force_login(self.admin)

        self.company1 = Company.objects.create(
            full_name="Test Company 1",
            email="office@company1.com",
            website="www.company1.com",
            active=True,
            phone="+1(23) 456-78-90",
            city_name="city1",
            address='address 1',
            registration_number='1-12345',
            description=self.description,
            lead_source=None,
            was_in_touch=get_today(),
            country=self.country,
            type=None,
            owner=self.owner,
            department_id=self.department_id
        )
        self.company2 = Company.objects.create(
            full_name="Test Company 2",
            email="office@company2.com",
            website="www.company2.com",
            active=True,
            phone="+0(12) 345-67-89",
            city_name="city2",
            address='address 2',
            registration_number='2-12345',
            description=self.description,
            lead_source=None,
            was_in_touch=get_today(),
            country=self.country,
            type=None,
            owner=self.owner,
            department_id=self.department_id
        )
        self.contact1 = Contact.objects.create(
            first_name="John",
            last_name="Morgan",
            email="John@company1.com",
            description=self.description,
            company=self.company1,
            country=self.country,
            owner=self.owner,
            department_id=self.department_id
        )
        self.contact2 = Contact.objects.create(
            first_name="Lee",
            last_name="Trump",
            email="Lee@company2.com",
            description=self.description,
            company=self.company2,
            country=self.country,
            owner=self.owner,
            department_id=self.department_id
        )
        self.client.force_login(self.admin)

    def test_change_owner_view(self):
        url = reverse('site:crm_company_changelist')
        ids = ','.join(str(pk) for pk in (self.company1.id, self.company2.id))
        change_owner_url = reverse(
            'change_owner_companies') + f'?next={url}&ids={ids}'
        response = self.client.get(change_owner_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = {'owner': str(self.new_owner.id)}
        response = self.client.post(change_owner_url, data, follow=True)
        self.assertNoFormErrors(response)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertEqual(response.redirect_chain[0][0], url)
        self.company1.refresh_from_db()
        self.assertEqual(self.new_owner, self.company1.owner)
        self.company2.refresh_from_db()
        self.assertEqual(self.new_owner, self.company2.owner)
        self.contact1.refresh_from_db()
        self.assertEqual(self.new_owner, self.contact1.owner)
        self.contact2.refresh_from_db()
        self.assertEqual(self.new_owner, self.contact2.owner)
