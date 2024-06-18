from django.contrib.contenttypes.models import ContentType
from django.test import tag

from common.utils.helpers import USER_MODEL
from crm.models import Company
from crm.models import Contact
from crm.utils.change_massconts import change_massconts
from massmail.models import EmlAccountsQueue
from massmail.models.email_account import EmailAccount
from massmail.models.mass_contact import MassContact
from tests.base_test_classes import BaseTestCase

# manage.py test tests.crm.utils.test_change_massconts --keepdb


@tag('TestCase')
class TesttestChangeMassconts(BaseTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        username_list = ("Andrew.Manager.Global",
                         "Darian.Manager.Co-worker.Head.Global")
        users = USER_MODEL.objects.filter(
            username__in=username_list)
        cls.owner = users.get(username="Andrew.Manager.Global")
        cls.owner2 = users.get(username="Darian.Manager.Co-worker.Head.Global")
        cls.company = Company.objects.create(
            full_name="Test company",
            email='office@company.com',
            owner=cls.owner
        )
        cls.contact1 = Contact.objects.create(
            first_name='Ton',
            email='Tom@company.com',
            company=cls.company,
            owner=cls.owner
        )
        cls.contact2 = Contact.objects.create(
            first_name='Kim',
            email='Kim@company.com',
            company=cls.company,
            owner=cls.owner
        )

    def setUp(self):
        print("Run Test Method:", self._testMethodName)
        self.mc = MassContact.objects.create(
            content_type=ContentType.objects.get_for_model(self.company),
            object_id=self.company.id
        )
        self.mc1 = MassContact.objects.create(
            content_type=ContentType.objects.get_for_model(self.contact1),
            object_id=self.contact1.id
        )
        self.mc2 = MassContact.objects.create(
            content_type=ContentType.objects.get_for_model(self.contact2),
            object_id=self.contact2.id
        )

    def test_change_massconts(self):
        ea = EmailAccount.objects.create(
            name='Email Account',
            email_host='smtp.example.com',
            email_host_user='andrew@example.com',
            email_host_password='password',
            email_port=587,
            from_email='andrew@example.com',
            main=True,
            massmail=True,
            owner=self.owner,
        )
        EmlAccountsQueue.objects.create(
            owner=self.owner,
            queue=f'[{ea.id}]'
        )
        change_massconts(self.company)
        self.mc.refresh_from_db()
        self.assertEqual(ea, self.mc.email_account)
        self.mc1.refresh_from_db()
        self.assertEqual(ea, self.mc1.email_account)
        self.mc2.refresh_from_db()
        self.assertEqual(ea, self.mc2.email_account)

    def test_delete_massconts(self):
        change_massconts(self.company)
        self.assertFalse(
            MassContact.objects.filter(id=self.mc.id).exists(),
            "Company MassContact not deleted"
        )
        self.assertFalse(
            MassContact.objects.filter(id=self.mc1.id).exists(),
            "Contact MassContact not deleted"
        )
        self.assertFalse(
            MassContact.objects.filter(id=self.mc2.id).exists(),
            "Contact MassContact not deleted"
        )
