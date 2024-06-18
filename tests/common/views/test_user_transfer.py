from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.test import tag
from django.urls import reverse
from common.views.copy_department import MODELS
from crm.models import Company
from crm.models import Contact
from crm.models import Deal
from crm.models import Lead
from crm.models import Product
from crm.models import ClosingReason
from crm.models import Request
from crm.models import Tag
from common.utils.helpers import get_department_id
from common.utils.helpers import USER_MODEL
from tests.crm.test_deal import get_contact_request
from tests.crm.test_deal import get_test_deal
from tests.crm.test_request_methods import populate_db
from tests.base_test_classes import BaseTestCase

# python manage.py test tests.common.views.test_user_transfer --keepdb


@tag('TestCase')
class TestUserTransfer(BaseTestCase):
    """Test user transfer"""
    # TODO: complete with CrmEmail, EmailAccount,
    # MailingOut, Signature, EmlMessage

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.department = Group.objects.get(name="Global sales")
        populate_db(cls)

        cls.lead.owner = cls.owner
        cls.lead.save(update_fields=['owner'])
        test_tag = Tag.objects.create(
            name="Test tag",
            department=cls.department
        )
        cls.company.tags.add(test_tag)
        cls.contact.owner = cls.owner
        cls.contact.department = cls.department
        cls.contact.save(update_fields=['department', 'owner'])
        cls.admin = USER_MODEL.objects.get(username="Adam.Admin")

    def setUp(self):
        print("Run Test Method:", self._testMethodName)
        self.client.force_login(self.admin)
        self.product = Product.objects.create(
            name="Test product",
            department=self.department
        )
        self.contact_request = get_contact_request()
        self.contact_request.department = self.department
        self.contact_request.owner = self.owner
        self.contact_request.save(update_fields=['department', 'owner'])
        self.contact_request.products.add(self.product)

        self.co_owner = None
        self.deal = get_test_deal(self)
        closing_reason = ClosingReason.objects.first()
        self.deal.closing_reason = closing_reason
        self.deal.save(update_fields=['closing_reason'])

    def test_user_transfer(self):
        url = reverse('copy_department')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = {"department": str(self.department.id)}
        response = self.client.post(url, data, follow=True)
        self.assertNoFormErrors(response)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        changelist_url = reverse("admin:auth_group_changelist")
        self.assertEqual(response.redirect_chain[0][0], changelist_url)
        try:
            new_department = Group.objects.get(
                name="Global sales (copy)")
        except Group.DoesNotExist:
            self.fail("Fail department copy")

        url = reverse('user_transfer')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = {
            "owner": str(self.owner.id),
            "department": str(new_department.id)
        }
        response = self.client.post(url, data, follow=True)
        self.assertNoFormErrors(response)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        manager_department_id = get_department_id(self.owner)
        self.assertEqual(
            new_department.id, manager_department_id,
            "The manager is not transferred to another department."
        )
        for model in (Request, Deal, Lead, Company, Contact):
            self.assertEqual(
                True,
                model.objects.filter(
                    owner=self.owner,
                    department=new_department
                ).exists(),
                f"The {model.__name__} is not transferred to another department."
            )
        MODELS.append(Tag)
        for model in MODELS:
            self.assertEqual(
                True,
                model.objects.filter(department=new_department).exists(),
                f"The {model.__name__} is not copied to another department."
            )
