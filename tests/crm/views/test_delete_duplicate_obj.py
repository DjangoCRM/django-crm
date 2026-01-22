from django.contrib.contenttypes.models import ContentType
from django.test import tag
from django.test import RequestFactory
from django.urls import reverse
from common.models import TheFile

from common.utils.helpers import get_department_id
from common.utils.helpers import USER_MODEL
from crm.models import CrmEmail, Industry
from crm.models import Lead
from crm.models import Company
from crm.models import Contact
from crm.models import Request
from crm.site.crmadminsite import crm_site
from crm.site.crmmodeladmin import CrmModelAdmin
from massmail.models import MailingOut
from tests.base_test_classes import BaseTestCase
from tests.utils.helpers import get_content_file

# manage.py test tests.crm.views.test_delete_duplicate_obj --keepdb


@tag('TestCase')
class TestDeleteDuplicateObj(BaseTestCase):
    """Test for correctly deleting an object as a duplicate."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.owner = USER_MODEL.objects.get(username="Andrew.Manager.Global")
        cls.department_id = get_department_id(cls.owner)

    def setUp(self):
        print("Run Test Method:", self._testMethodName)
        self.client.force_login(self.owner)

    def test_delete_duplicate_company(self):
        mailing_out = self.get_mailing_out(Company)
        phone = "12345678"
        industry1 = Industry.objects.create(
            name="industry1",
            department_id=self.department_id
        )
        industry2 = Industry.objects.create(
            name="industry2",
            department_id=self.department_id
        )
        duplicate_company = Company.objects.create(
            id=6003,
            full_name="Duplicate company",
            owner=self.owner,
            department_id=self.department_id,
            phone=phone
        )
        duplicate_company.industry.add(industry2)
        original_company = Company.objects.create(
            id=6000,
            full_name="Original company",
            owner=self.owner,
            department_id=self.department_id
        )
        original_company.industry.add(industry1)
        contact = Contact.objects.create(
            company=duplicate_company,
            owner=self.owner,
            department_id=self.department_id
        )
        email = CrmEmail.objects.create(
            company=duplicate_company,
            owner=self.owner,
            department_id=self.department_id
        )
        request = Request.objects.create(
            company=duplicate_company,
            owner=self.owner,
            department_id=self.department_id
        )
        url = reverse('site:crm_company_change', args=(duplicate_company.id,))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        model_admin = CrmModelAdmin(model=Company, admin_site=crm_site)
        factory = RequestFactory()
        test_request = factory.get(url)
        del_dup_url = model_admin.del_dup_url(test_request, duplicate_company.id)
        self.assertIn(del_dup_url, response.rendered_content)

        response = self.client.get(del_dup_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = {'company': original_company.id}
        response = self.client.post(del_dup_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        original_company.refresh_from_db()
        self.assertEqual(original_company.phone, phone)
        self.assertEqual(set(original_company.industry.all()), {industry1, industry2})
        contact.refresh_from_db()
        self.assertEqual(contact.company_id, original_company.id)
        email.refresh_from_db()
        self.assertEqual(email.company_id, original_company.id)
        request.refresh_from_db()
        self.assertEqual(request.company_id, original_company.id)
        mailing_out.refresh_from_db()
        self.assertNotIn(f"{duplicate_company.id},", mailing_out.recipient_ids)
        self.assertIn(f"{original_company.id},", mailing_out.recipient_ids)
        self.assertFalse(
            Company.objects.filter(id=duplicate_company.id).exists(),
            "The duplicate object has not been deleted."
        )

    def test_delete_duplicate_contact(self):
        mailing_out = self.get_mailing_out(Contact)
        company = Company.objects.create(
            owner=self.owner,
            department_id=self.department_id
        )
        other_phone = "87654321"
        duplicate_contact = Contact.objects.create(
            id=7143,
            first_name="Duplicate Contact",
            owner=self.owner,
            department_id=self.department_id,
            company=company,
            other_phone=other_phone
        )
        file_name, content_file = get_content_file(self._testMethodName)
        file = TheFile.objects.create(
            file=content_file,
            content_object=duplicate_contact,
        )
        content_file.file.close()
        phone = "12345678"
        original_contact = Contact.objects.create(
            id=7000,
            first_name="Original Contact",
            owner=self.owner,
            department_id=self.department_id,
            company=company,
            phone=phone
        )
        email = CrmEmail.objects.create(
            contact=duplicate_contact,
            owner=self.owner,
            department_id=self.department_id
        )
        request = Request.objects.create(
            contact=duplicate_contact,
            owner=self.owner,
            department_id=self.department_id
        )
        url = reverse('site:crm_contact_change', args=(duplicate_contact.id,))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        model_admin = CrmModelAdmin(model=Contact, admin_site=crm_site)
        factory = RequestFactory()
        test_request = factory.get(url)
        del_dup_url = model_admin.del_dup_url(test_request, duplicate_contact.id)
        self.assertIn(del_dup_url, response.rendered_content)

        response = self.client.get(del_dup_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = {'contact': original_contact.id}
        response = self.client.post(del_dup_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        original_contact.refresh_from_db()
        self.assertEqual(original_contact.phone, phone)
        email.refresh_from_db()
        self.assertEqual(email.contact_id, original_contact.id)
        request.refresh_from_db()
        self.assertEqual(request.contact_id, original_contact.id)
        mailing_out.refresh_from_db()
        self.assertNotIn(f",{duplicate_contact.id},", mailing_out.recipient_ids)
        self.assertIn(f",{original_contact.id},", mailing_out.recipient_ids)
        
        file.refresh_from_db()
        self.assertEqual(file.content_object, original_contact)
        self.assertFalse(
            Contact.objects.filter(id=duplicate_contact.id).exists(),
            "The duplicate object has not been deleted."
        )
        file.file.delete()

    def test_delete_duplicate_lead(self):
        mailing_out = self.get_mailing_out(Lead)
        duplicate_lead = Lead.objects.create(
            id=7156,
            first_name="Duplicate Lead",
            owner=self.owner,
            department_id=self.department_id,
        )
        original_lead = Lead.objects.create(
            id=4000,
            first_name="Original Lead",
            owner=self.owner,
            department_id=self.department_id,
        )
        email = CrmEmail.objects.create(
            lead=duplicate_lead,
            owner=self.owner,
            department_id=self.department_id
        )
        request = Request.objects.create(
            lead=duplicate_lead,
            owner=self.owner,
            department_id=self.department_id
        )
        url = reverse('site:crm_lead_change', args=(duplicate_lead.id,))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        model_admin = CrmModelAdmin(model=Lead, admin_site=crm_site)
        factory = RequestFactory()
        test_request = factory.get(url)
        del_dup_url = model_admin.del_dup_url(test_request, duplicate_lead.id)
        self.assertIn(del_dup_url, response.rendered_content)

        response = self.client.get(del_dup_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = {'lead': original_lead.id}
        response = self.client.post(del_dup_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        email.refresh_from_db()
        self.assertEqual(email.lead_id, original_lead.id)
        request.refresh_from_db()
        self.assertEqual(request.lead_id, original_lead.id)
        mailing_out.refresh_from_db()
        self.assertNotIn(f",{duplicate_lead.id}", mailing_out.recipient_ids)
        self.assertIn(f",{original_lead.id}", mailing_out.recipient_ids)
        self.assertFalse(
            Lead.objects.filter(id=duplicate_lead.id).exists(),
            "The duplicate object has not been deleted."
        )

    def get_mailing_out(self, model) -> MailingOut:
        content_type = ContentType.objects.get_for_model(model)
        return MailingOut.objects.create(
            name="Test MailingOut",
            content_type=content_type,
            recipient_ids="6003,7155,6005,6871,7141,7143,7146,7153,7156",
            recipients_number=9,
            owner=self.owner,
            department_id=self.department_id
        )
