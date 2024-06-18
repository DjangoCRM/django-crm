from django.contrib.contenttypes.models import ContentType
from django.test import tag

from common.models import Department
from common.models import TheFile
from crm.models import LeadSource
from crm.models import CrmEmail
from crm.models import Request
from crm.utils.create_email_request import create_email_request
from tests.base_test_classes import BaseTestCase
from tests.crm.test_request_methods import populate_db
from tests.utils.helpers import get_content_file

# manage.py test tests.crm.test_create_email_request --keepdb


@tag('TestCase')
class TestCreateEmailInquiry(BaseTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        populate_db(cls)
        cls.department = Department.objects.get(name='Global sales')
        cls.lead_source = LeadSource.objects.create(
            name='My company website',
            email='sale@crm.com',
            department=cls.department
        )

    def setUp(self):
        print("Run Test Method:", self._testMethodName)
        self.eml = CrmEmail(
            to='sale@crm.com',
            from_field='',
            subject='test inquiry',
            content='',
            incoming=True,
            inquiry=True,
            department=self.department,
            owner=self.owner,
            is_html=False
        )

    def test_create_contact_email_request_with_file(self):
        self.eml.from_field = '"Tom Smith" <Tom@testcompany.com>'
        self.eml.save()
        content_type = ContentType.objects.get_for_model(self.eml)
        file_name, content_file = get_content_file(self._testMethodName)
        file = TheFile.objects.create(
            file=content_file,
            content_type=content_type,
            object_id=self.eml.id
        )
        content_file.file.close()
        create_email_request(self.eml, self.eml.from_field)
        try:
            req = Request.objects.get(
                contact=self.contact
            )
            msg = "Wrong a lead source of request"
            self.assertEqual(req.lead_source, self.lead_source, msg)
        except Request.DoesNotExist:
            self.fail("Contact request not created")
        self.assertEqual(req.country_id, self.department.default_country_id)
        req_file = req.files.first()
        self.assertIn(file_name, req_file.file.name)
        file.file.delete()

    def test_create_lead_email_request(self):
        self.eml.from_field = '"Michael" <Michael@testcompany.com>'
        self.eml.save()
        create_email_request(self.eml, self.eml.from_field)
        self.assertTrue(
            Request.objects.filter(lead=self.lead).exists(),
            "Lead request not created"
        )

    def test_create_new_lead_email_request(self):
        self.eml.from_field = '"Bruno" <Bruno@example.com>'
        self.eml.save()
        create_email_request(self.eml, self.eml.from_field)
        self.assertTrue(
            Request.objects.filter(
                email__contains='Bruno@example.com'
            ).exists(),
            "New lead request not created"
        )

    def test_create_new_contact_email_request(self):
        self.eml.from_field = '"Rolf" <Rolf@testcompany.com>'
        self.eml.save()
        create_email_request(self.eml, self.eml.from_field)
        self.assertFalse(
            Request.objects.filter(
                email__contains='Rolf@testcompany.com',
                contact__first_name='Rolf'
            ).exists(),
            "New Contact request created"
        )
