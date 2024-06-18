from django.conf import settings
from django.test import tag
from django.urls import reverse

from crm.models import Company
from crm.models import Contact
from crm.models import Deal
from crm.models import Lead
from crm.models import Stage
from crm.models import CrmEmail
from common.utils.helpers import get_delta_date
from common.utils.helpers import get_department_id
from common.utils.helpers import USER_MODEL
from massmail.models.email_account import EmailAccount
from tests.crm.test_request_methods import populate_db
from tests.base_test_classes import BaseTestCase
from tests.utils.helpers import add_file_to_form
from tests.utils.helpers import get_adminform_initials

# manage.py test tests.crm.views.test_create_email_view --keepdb


@tag('TestCase')
class TestCreateEmailView(BaseTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.owner = USER_MODEL.objects.get(username="Andrew.Manager.Global")
        cls.department_id = get_department_id(cls.owner)
        cls.ea = EmailAccount.objects.create(
            name='CRM Email Account',
            email_host='smtp.example.com',
            email_port=587,
            email_host_user='andrew@example.com',
            email_host_password='password',
            from_email='andrew@example.com',
            main=True,
            email_use_tls=True,
            email_use_ssl=False,
            owner=cls.owner,
        )
        cls.company = Company.objects.create(
            full_name="Test Company",
            email="office@company.com"
        )
        populate_db(cls)
        stage = Stage.objects.filter(department=cls.department_id).first()
        cls.deal = Deal.objects.create(
            name="Mock deal for test email creation",
            department_id=get_department_id(cls.owner),
            ticket='123',
            description='description',
            next_step=settings.FIRST_STEP,
            next_step_date=get_delta_date(1),
            stage=stage,
            owner=cls.owner,
            stages_dates='{date} - {stage}\n',
            workflow='{date} - {msg}\n',
            contact=cls.contact,
            company=cls.contact.company,
            country=cls.contact.company.country
        )
        cls.deal_change_url = reverse(
            "site:crm_deal_change", args=(cls.deal.id,)
        )
        cls.create_email_url = reverse(
            'create_email', args=(cls.deal.id,)
        ) + "?object=deal&recipient=contact"

    def setUp(self):
        print("Run Test Method:", self._testMethodName)
        self.client.force_login(self.owner)

    def test_create_email_from_deal_page(self):   # to contact

        response = self.client.get(self.create_email_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        data["_continue"] = ''
        # submit form
        add_url = response.redirect_chain[0][0]
        response = self.client.post(add_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        try:
            eml = CrmEmail.objects.get(
                to=self.deal.contact.email,
                from_field=self.ea.email_host_user
            )
        except CrmEmail.DoesNotExist as e:
            self.fail(e)
        change_eml_url = reverse('site:crm_crmemail_change', args=(eml.id,))
        self.assertIn(change_eml_url, response.redirect_chain[-1][0])

    def test_create_email_from_deal_page_with_file(self):   # to contact
        response = self.client.get(self.deal_change_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        file_name = add_file_to_form(self._testMethodName, data)
        # submit form with file
        response = self.client.post(self.deal_change_url, data, follow=True)
        self.assertNoFormErrors(response)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertEqual(
            response.redirect_chain[-1][0],
            reverse("site:crm_deal_changelist")
        )
        data['common-thefile-content_type-object_id-0-file'].close()
        # create email
        response = self.client.get(self.create_email_url, follow=True)
        data = response.context['form'].initial.copy()
        data[file_name] = True
        data['csrfmiddlewaretoken'] = '123'
        response = self.client.post(self.create_email_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        file = self.deal.files.first()
        file.file.delete()
        try:
            eml = CrmEmail.objects.get(
                to=self.deal.contact.email,
                from_field=self.ea.email_host_user
            )
        except CrmEmail.DoesNotExist as e:
            self.fail(e)
        change_eml_url = reverse('site:crm_crmemail_change', args=(eml.id,))
        self.assertEqual(change_eml_url, response.redirect_chain[-1][0])

    def test_create_email_to_company(self):
        self.get_test(self.company)

    def test_create_email_to_contact(self):
        contact = Contact.objects.create(
            first_name='Sonya',
            last_name='Parker',
            email="Sonya.Parker@example.com",
            owner=self.owner,
            department_id=self.department_id,
            company=self.company
        )
        self.get_test(contact)

    def test_create_email_to_lead(self):
        lead = Lead.objects.create(
            first_name='Sonya',
            last_name='Parker',
            email="Sonya.Parker@example.com",
            owner=self.owner,
            department_id=self.department_id,
        )
        self.get_test(lead)

    def get_test(self, instance):
        model_name = instance._meta.model_name
        url = reverse(
            'create_email', args=(instance.id,)
        ) + f"?object={model_name}&recipient={model_name}"
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        data["_continue"] = ''
        data["content"] = 'content'
        data["subject"] = 'subject'
        # submit form
        add_url = response.redirect_chain[0][0]
        response = self.client.post(add_url, data, follow=True)
        self.assertNoFormErrors(response)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        try:
            eml = CrmEmail.objects.get(
                to=instance.email,
                from_field=self.ea.email_host_user
            )
        except CrmEmail.DoesNotExist as e:
            self.fail(e)
        change_eml_url = reverse(
            'site:crm_crmemail_change', args=(eml.id,)
        )
        self.assertIn(change_eml_url, response.redirect_chain[-1][0])
