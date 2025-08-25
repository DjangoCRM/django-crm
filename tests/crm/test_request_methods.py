from django.core.exceptions import ValidationError
from django.core import mail
from django.test import tag

from common.utils.helpers import get_department_id
from common.utils.helpers import USER_MODEL
from crm.forms.admin_forms import COUNTRY_WARNING
from crm.models import Company
from crm.models import Country
from crm.models import Contact
from crm.models import Lead
from crm.models import Request
from tests.base_test_classes import BaseTestCase
from tests.utils.helpers import get_adminform_initials
from tests.utils.helpers import get_country_instance

# manage.py test tests.crm.test_request_methods --keepdb


@tag('TestCase')
class TestRequestMethods(BaseTestCase):
    """Test methods of Request model and deal creation."""
    
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        populate_db(cls)
    
    def setUp(self):
        print("Run Test Method:", self._testMethodName)
        self.contact_request = Request(
            request_for='test inquiry',
            first_name='Tom',
            email='Tom@testcompany.com',
            phone='+1234567890',
            company_name='Test Company LLC'
        )
        self.new_lead_request = Request(
            request_for='test inquiry',
            first_name='Bruno',
            email='Bruno@example.com',
            phone='+0182345678',
            company_name='Bruno Company LLC'
        ) 
        self.lead_request = Request(
            request_for='test inquiry',
            first_name='Michael',
            email='"Michael" <Michael@testcompany.com>',
            phone='8(43)123-45-67',
            company_name='Test Company LLC'
        )

    def test_deal_creation(self):
        self.contact_request.owner = self.owner
        self.contact_request.department_id = get_department_id(self.owner)
        self.contact_request.save()
        co_owner = self.owner.__class__.objects.get(
            username="Darian.Manager.Co-worker.Head.Global")
        self.client.force_login(self.owner)
        request_change_url = self.contact_request.get_absolute_url()
        response = self.client.get(request_change_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        data['co_owner'] = co_owner.id
        data['_create-deal'] = ''
        # submit form
        self.client.post(request_change_url, data, follow=True)
        self.assertRaisesMessage(ValueError, COUNTRY_WARNING)
        data['country'] = self.country.id
        response = self.client.post(request_change_url, data, follow=True)
        self.assertNoFormErrors(response)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.contact_request.refresh_from_db()
        self.assertTrue(self.contact_request.deal,
                        "New deal has not been created")
        self.assertEqual(len(mail.outbox), 1)  # NOQA
        mail.outbox = []

    def test_request_doesnt_exists(self):
        chief = USER_MODEL.objects.get(username="Garry.Chief")
        self.client.force_login(chief)
        self.obj_doesnt_exists(Request)

    # -- tests request methods -- #
        
    def test_no_contact_or_lead(self):
        self.new_lead_request.find_contact_or_lead()
        msg = "Found the wrong contact"
        self.assertFalse(self.new_lead_request.contact, msg)
        msg = "Found the wrong lead"
        self.assertFalse(self.new_lead_request.lead, msg)

    def test_find_company(self):
        # Test finding a company by name
        self.contact_request.find_company()
        self.assertEqual(self.contact_request.company, self.company)
        self.contact_request.company = None

        country = Country.objects.create(
            name='Sweden',
            url_name='Sweden'
        )
        Company.objects.create(
            full_name='Test Company LLC',
            email='office@testcompany.com',
            country=country
        )
        self.contact_request.find_company()
        self.assertEqual(self.contact_request.company, self.company)
        self.contact_request.company = None

        # Test finding a company by a slightly modified name
        request = Request(
            request_for='test inquiry',
            first_name='Tom',
            email='Tom@testcompany.com',
            phone='+1234567890',
            company_name='Test - Company LLC.'
        )
        request.find_company()
        self.assertEqual(request.company, self.company)
        self.contact_request.company = None

        # Test finding a company by an alternative name
        self.company.alternative_names = 'Test Co, TestCompany'
        self.company.save()
        request = Request(
            request_for='test inquiry',
            first_name='Tom',
            email='Tom@testcompany.com',
            phone='+1234567890',
            company_name='Test Co'
        )
        request.find_company()
        self.assertEqual(request.company, self.company)
        request.company = None
        
    def test_find_contact(self):
        self.contact_request.find_contact_or_lead()
        msg = "The contact not found"
        self.assertTrue(self.contact_request.contact, msg)

    def test_find_lead(self):
        self.lead_request.find_contact_or_lead()
        self.assertEqual(self.lead_request.lead, self.lead)

        self.lead_request.email = ''
        self.lead_request.lead = None
        self.lead_request.find_contact_or_lead()
        self.assertEqual(self.lead_request.lead, self.lead)

        self.lead_request.phone = ''
        self.lead_request.lead = None
        self.lead_request.find_contact_or_lead()
        self.assertIsNone(self.lead_request.lead)

        self.lead_request.last_name = 'Brut'
        self.lead_request.lead = None
        self.lead_request.find_contact_or_lead()
        self.assertIsNone(self.lead_request.lead)

        self.lead.last_name = 'Brut'
        self.lead.save()
        self.lead_request.lead = None
        self.lead_request.find_contact_or_lead()
        self.assertEqual(self.lead_request.lead, self.lead)

        Lead.objects.create(
            first_name='Michael',
            last_name='Brut',
            company_name='Another Test Company LLC',
            country=self.country,
        )
        self.lead_request.lead = None
        self.lead_request.find_contact_or_lead()
        self.assertEqual(self.lead_request.lead, self.lead)

    def test_creation_new_lead(self):
        self.new_lead_request.owner = self.owner
        self.new_lead_request.get_or_create_contact_or_lead()
        msg = "Found the wrong contact"
        self.assertFalse(self.new_lead_request.contact, msg)
        msg = "New lead has not been created"
        self.assertTrue(self.new_lead_request.lead, msg)         
        
    def test_creation_new_contact(self):
        new_contact_request = Request(
            request_for='test inquiry',
            first_name='Kate',
            last_name='Adams',
            email='Kate@testcompany.com',
            phone='+1-432-456-7890',
            company_name='Test Company LLC',
            owner=self.owner
        )
        new_contact_request.get_or_create_contact_or_lead()
        msg = "The new contact not found."
        self.assertTrue(new_contact_request.contact, msg)
        contact_num = Contact.objects.filter(company=self.company).count()
        msg = "Incorrect number of company contacts."
        self.assertEqual(contact_num, 2, msg)
        msg = "The lead should not be created."
        self.assertEqual(new_contact_request.lead, None, msg)
        
    def test_clean_method(self):
        # Test of company and contact person match.
        # Specified the Contact person only.
        # Company and contact person match.
        try:
            self.contact_request.clean()
        except Exception as e:
            self.fail(e)

        company = Company.objects.create(
            full_name='Another Test Company LLC',
            email='office@test.company.com',
        )
        self.contact_request.contact = self.contact
        self.contact_request.company = company
        msg = "Company and contact person matching failed."
        with self.assertRaises(ValidationError, msg=msg):
            self.contact_request.clean()

        # Test of specifying the Contact person or Lead        
        self.contact_request.lead = self.lead
        msg = """It is possible to specify the Contact person 
            and the Lead together."""        
        with self.assertRaises(ValidationError, msg=msg):
            self.contact_request.clean()
        self.contact_request.lead = None

    def test_case_field_default(self):
        """Test that the case field defaults to False."""
        request = Request(
            request_for='test inquiry',
            first_name='John',
            email='john@example.com'
        )
        self.assertFalse(request.case, "Case field should default to False")
        
    def test_case_field_assignment(self):
        """Test that the case field can be set to True."""
        request = Request(
            request_for='test case inquiry',
            first_name='Jane',
            email='jane@example.com',
            case=True
        )
        self.assertTrue(request.case, "Case field should be settable to True")


def populate_db(cls):
    cls.owner = USER_MODEL.objects.get(username="Andrew.Manager.Global")
    cls.country = get_country_instance()
    cls.lead = Lead.objects.create(
        first_name='Michael',
        email='Michael@testcompany.com',
        phone='843/123-4567',
        company_name='Test Company LLC',
        country=cls.country,
    )
    cls.company = Company.objects.create(
        full_name='Test Company LLC',
        email='office@testcompany.com',
        country=cls.country,
        owner=cls.owner
    )
    cls.contact = Contact.objects.create(
        first_name='Tom',
        last_name='Smith',
        email='Tom@testcompany.com',
        phone='+1234567890',
        company=cls.company
    )
