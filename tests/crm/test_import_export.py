import os
import queue
from random import random
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.test import TransactionTestCase
from django.urls import reverse

from crm.models import Company
from crm.models import Contact
from common.views.export_objects import get_file_path
from common.utils.helpers import get_department_id
from common.utils.helpers import get_today
from tests.utils.helpers import get_user

# manage.py test tests.crm.test_import_export --keepdb

company_queue = queue.Queue()
contact_queue = queue.Queue()
description = str(int(random() * 1E5))


class TestImportExport(TransactionTestCase):
    """
    Test import/export Companies and Contacts from excel file.
    """
    # Inherit TransactionTestCase since creating and saving objects
    # happens in a separate thread.
    fixtures = ('groups.json',)

    def setUp(self):
        print("Run Test Method:", self._testMethodName)
        super().setUp()
        # self.owner = USER_MODEL.objects.get(username="Andrew.Manager.Global")
        self.owner = get_user()
        self.department_id = get_department_id(self.owner)
        self.company1 = Company.objects.create(
            full_name="Test Company 1",
            email="office@company1.com",
            website="www.company1.com",
            active=True,
            phone="+1(23) 456-78-90",
            city_name="city1",
            address='address 1',
            registration_number='1-12345',
            description=description,
            lead_source=None,
            was_in_touch=get_today(),
            country=None,
            type=None,
            # 'industry': None,
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
            description=description,
            lead_source=None,
            was_in_touch=get_today(),
            country=None,
            type=None,
            # industry': None,
            owner=self.owner,
            department_id=self.department_id
        )
        self.client.force_login(self.owner)

    def test_export_import_company(self):
        changelist_url = reverse("site:crm_company_changelist")
        import_url = reverse('site:import_companies')
        sender = Company
        msg = "The company is not imported"
        content_type_id = ContentType.objects.get_for_model(Company).id
        self.run_test(changelist_url, import_url, sender, msg, content_type_id, self.company1, self.company2)

    def test_export_import_contacts(self):
        obj1 = Contact.objects.create(
            first_name="John",
            last_name="Morgan",
            email="John@company1.com",
            description=description,
            company=self.company1,
            owner=self.owner,
            department_id=self.department_id
        )
        obj2 = Contact.objects.create(
            first_name="Lee",
            last_name="Trump",
            email="Lee@company2.com",
            description=description,
            company=self.company2,
            owner=self.owner,
            department_id=self.department_id
        )
        changelist_url = reverse("site:crm_contact_changelist")
        import_url = reverse('site:import_contacts')
        sender = Contact
        msg = "The contact is not imported"
        content_type_id = ContentType.objects.get_for_model(Contact).id
        self.run_test(changelist_url, import_url, sender, msg, content_type_id, obj1, obj2)

    def run_test(self, changelist_url, import_url, sender, msg, content_type_id, obj1, obj2):
        export_url = reverse('export_objects') + \
            f"?content_type={content_type_id}"
        response = self.client.get(export_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        obj1.delete()
        obj2.delete()

        @receiver(post_save, sender=sender)
        def get_saved_instance(sender, instance, created, **kwargs):
            if created:
                if description == instance.description:
                    contact_queue.put(instance)

        file_path = get_file_path(self.owner.username, model=sender)
        response = self.client.get(import_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertEqual(response.redirect_chain, [])
        with open(file_path, 'rb') as fp:
            response = self.client.post(
                import_url,
                {'name': os.path.basename(file_path), 'file': fp},
                follow=True
            )
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertEqual(response.redirect_chain[0][0], changelist_url)
        os.remove(file_path)
        for _ in range(2):
            try:
                contact_queue.get(timeout=4)
            except queue.Empty:
                self.fail("The contact is not imported")
