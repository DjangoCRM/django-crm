from django.conf import settings
from django.contrib.messages.storage import default_storage
from django.test import RequestFactory
from django.test import tag
from django.urls import reverse

from crm.models import Company
from crm.models import Contact
from crm.models import Lead
from crm.site.leadadmin import LeadAdmin
from crm.site.crmadminsite import crm_site
from common.utils.helpers import get_department_id
from common.utils.helpers import USER_MODEL
from tests.crm.test_request_methods import populate_db
from tests.base_test_classes import BaseTestCase
from tests.utils.helpers import get_adminform_initials

# manage.py test tests.crm.test_lead_conversion --keepdb

lead_admin = LeadAdmin(model=Lead, admin_site=crm_site)


@tag('TestCase')
class TestLeadConversion(BaseTestCase):
    """Test converting a lead into a company and its contact person"""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        populate_db(cls)
        cls.lead.owner = cls.owner
        cls.lead.save()
        cls.lead_change_url = reverse(
            "site:crm_lead_change", args=(cls.lead.id,))
        cls.user_qs = USER_MODEL.objects.filter(id=cls.owner.id)
        cls.department_id = get_department_id(cls.owner)
        cls.factory = RequestFactory()
        cls.request = cls.factory.post(cls.lead_change_url, {'_convert': ''})
        cls.request.user = cls.owner
        cls.request.user.is_superoperator = False
        cls.request.user.department_id = cls.department_id
        cls.form = lead_admin.get_form(cls.request, obj=cls.lead)
        cls.form_data = {
            'first_name': 'Michael',
            'last_name': 'Hammer',
            'email': '"Michael" <Michael@testcompany.com>',
            'phone': '8(43)123-45-67',
            'company_name': 'Test Company LLC',
            'company_email': 'office@testcompany.com',
        }
        cls.form_min_data = {'first_name': 'Michael'}

    def setUp(self):
        print("Run Test Method:", self._testMethodName)

    def test_lead_conversion_with_specified_company_and_contact(self):
        self.lead.contact = self.contact
        self.lead.company = self.company
        self.lead.save()
        id=self.lead.id
        contact_num = Contact.objects.count()
        company_num = Company.objects.count()
        with self.settings(
                MESSAGE_STORAGE='django.contrib.messages.storage.cookie.CookieStorage'
        ):
            self.request._messages = default_storage(self.request)        
            lead_admin.response_post_save_change(
                        self.request, self.lead)
            self.assertEqual(Contact.objects.count(), contact_num)
            self.assertEqual(Company.objects.count(), company_num)
            self.assertFalse(
                Lead.objects.filter(id=id),
                "The Lead is not deleted"
            )            
        
    def test_multiple_companies(self):
        """Getting error - Found several companies in the database."""
        Company.objects.create(
            full_name='Test Company LLC',
            email='office@testcompany.com',
            owner=self.owner
        )
        company_num = Company.objects.count()
        with self.settings(
                MESSAGE_STORAGE='django.contrib.messages.storage.cookie.CookieStorage'
        ):
            self.request._messages = default_storage(self.request)
            response = lead_admin.response_post_save_change(
                self.request, self.lead)
            msg = "New company created."
            self.assertEqual(Company.objects.count(), company_num, msg)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(
                Lead.objects.filter(id=self.lead.id).exists(),
                "The Lead is deleted"
            )

    def test_lead_conversion(self):
        """Converting a lead with the creation of a company and its contact person."""
        lead = Lead.objects.create(
            first_name='Bruno',
            email='Bruno@company.com',
            phone='+0182345678',
            company_name='Bruno Company LLC',
            region='west',
            district='district 9',
            country=self.country,
            department_id=self.department_id,
            owner=self.owner
        )
        self.client.force_login(self.owner)
        url = reverse("site:crm_lead_change", args=(lead.id,))
        # open lead in change view
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        # add missing data
        data['last_name'] = 'Hammer'
        data['company_email'] = 'office@company.com'
        # submit '_convert' button
        data['_convert'] = ''
        company_num = Company.objects.count()
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        msg = "No new company created."
        self.assertEqual(Company.objects.count(), company_num + 1, msg)
        self.assertFalse(
            Lead.objects.filter(id=lead.id).exists(),
            "The Lead not deleted"
        )
        # -- check that new company and contact created with correct data -- #
        company = Company.objects.get(full_name='Bruno Company LLC')
        self.assertEqual(company.region, 'west')
        self.assertEqual(company.district, 'district 9')

        contact = Contact.objects.get(first_name='Bruno')
        self.assertEqual(contact.region, 'west')
        self.assertEqual(contact.district, 'district 9')

    def test_lead_conversion_new_contact(self):
        """Converting a lead with the creation of a new contact for an existing company."""
        lead = Lead.objects.create(
            first_name='Bruno',
            email='Bruno@testcompany.com',
            phone='+0182345678',
            company_name='Test Company LLC',
            country=self.country,
        )
        company_num = Company.objects.count()
        with self.settings(
            MESSAGE_STORAGE='django.contrib.messages.storage.cookie.CookieStorage'
        ):
            self.request._messages = default_storage(self.request)
            response = lead_admin.response_post_save_change(self.request, lead)
            msg = "New company created."
            self.assertEqual(Company.objects.count(), company_num, msg)
            self.assertEqual(response.status_code, 302)
            self.assertFalse(
                Lead.objects.filter(id=lead.id).exists(),
                "The Lead not deleted"
            )

    def test_form_not_enough_data_to_convert(self):
        """Test for clearing a form with insufficient data to convert a Lead"""
        form = self.form(self.form_min_data, instance=self.lead)
        form.base_fields['owner'].initials = self.user_qs
        self.assertEqual(form.is_valid(), False)
        fields = set(settings.CONVERT_REQUIRED_FIELDS)
        fields = fields.difference(set(self.form_min_data.keys()))
        for f in fields:
            self.assertTrue(
                form.has_error(f),
                f"The field '{f}' must contain an error warning"
            )

    def test_form_with_enough_data_to_convert(self):
        """Test for clearing a form with full data to convert a Lead"""
        form = self.form(self.form_data, instance=self.lead)
        form.base_fields['owner'].initials = self.user_qs
        self.assertEqual(form.is_valid(), True)
        msg = 'The form must not have any errors'
        self.assertFalse(form.errors, msg)
