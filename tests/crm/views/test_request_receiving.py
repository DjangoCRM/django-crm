import uuid
from django.contrib.auth.models import AnonymousUser
from django.contrib.gis.geoip2 import GeoIP2
from django.contrib.gis.geoip2 import GeoIP2Exception
from django.contrib.sites.models import Site
from django.core import mail
from django.test import RequestFactory
from django.test import tag
from django.urls import reverse
from django.utils.translation import gettext as _

from common.models import Department
from common.utils.helpers import USER_MODEL
from crm.models.others import LeadSource
from crm.models import City
from crm.models import CrmEmail
from crm.models import Company
from crm.models import Country
from crm.models import Request
from crm.site.requestadmin import DEAL_OWNER_NOTICE
from crm.site.requestadmin import REQUEST_CO_OWNER_NOTICE
from crm.site.requestadmin import REQUEST_OWNER_NOTICE
from crm.views.add_request import add_request
from crm.views.contact_form import contact_form
from crm.views.contact_form import get_country_and_city
from tests.base_test_classes import BaseTestCase
from tests.utils.helpers import get_adminform_initials


# manage.py test tests.crm.views.test_request_receiving --keepdb


@tag('TestCase')
class TestRequestReceiving(BaseTestCase):
    """Test a request receiving  from a website by POST method"""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.add_request_url = reverse(add_request)
        department = Department.objects.get(name='Global sales')
        cls.ls = LeadSource.objects.create(name='', department=department)
        cls.request_data = {
            'name': 'Tom',
            'email': 'Tom@example.com',
            'subject': 'test inquiry',
            'phone': '+1234567890',
            'message': 'test message',
            'country': 'United States',
            'city': 'Houston',
            'company': 'My Company LLC',
            'leadsource_token': cls.ls.uuid
        }
        username_list = ("Darian.Manager.Co-worker.Head.Global",
                         "Valeria.Operator.Global")
        users = USER_MODEL.objects.filter(
            username__in=username_list)
        cls.manager = users.get(
            username="Darian.Manager.Co-worker.Head.Global")
        cls.operator = users.get(
            username="Valeria.Operator.Global")
        country_id = Country.objects.get(name='United States').id
        City.objects.create(
            country_id=country_id,
            name='Houston'
        )

    def setUp(self):
        print("Run Test Method:", self._testMethodName)
        self.data = self.request_data.copy()
        self.client.force_login(self.operator)

    def test_get_request(self):
        response = self.client.get(self.add_request_url)
        msg = 'Method Not Allowed'
        self.assertEqual(response.status_code, 405, msg)

    def test_invalid_form_data(self):
        self.data['email'] = 'Tom2example.com'  # wrong email format
        response = self.client.post(self.add_request_url, self.data)
        msg = 'Invalid form data from the site.'
        self.assertEqual(response.status_code, 409, msg)
    
    def test_invalid_form_leadsource_token(self):
        self.data['leadsource_token'] = uuid.uuid4()  # arbitrary uuid
        response = self.client.post(self.add_request_url, self.data)
        msg = 'Unauthorized request from site form'
        self.assertEqual(response.status_code, 401, msg)

    def test_the_request(self):
        response = self.client.post(self.add_request_url, self.data)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        try:
            req = Request.objects.get(
                request_for=self.data['subject'],
                first_name=self.data['name'],
                email=self.data['email'],
                phone=self.data['phone'],
                country__name=self.data['country'],
                city__name=self.data['city'],
                city_name=self.data['city']
            )
        except Request.DoesNotExist:
            self.fail('The Request does not exist in db')
        change_request_url = reverse("site:crm_request_change", args=(req.id,))

        response = self.client.get(change_request_url)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        data = get_adminform_initials(response)
        data['owner'] = str(self.manager.id)
        data['co_owner'] = str(self.manager.id)
        response = self.client.post(change_request_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertNoFormErrors(response)
        # Test that two messages has been sent.
        self.assertEqual(len(mail.outbox), 2)
        msg = "The subject of the notifying message is not correct."
        self.assertIn(
            str(REQUEST_OWNER_NOTICE),
            mail.outbox[0].subject,
            msg
        )
        self.assertIn(
            str(REQUEST_CO_OWNER_NOTICE),
            mail.outbox[1].subject,
            msg
        )
        mail.outbox = []

    def test_alternative_country_name(self):
        self.data['country'] = 'Turkey'  # old country name
        response = self.client.post(self.add_request_url, self.data)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertTrue(Request.objects.filter(
                request_for=self.data['subject'],
                first_name=self.data['name'],
                email=self.data['email'],
                phone=self.data['phone'],
                country__name='Turkiye',
                city__name=self.data['city'],
                city_name=self.data['city']
            ).exists())
        mail.outbox = []
 
    def test_wrong_country_name(self):
        self.data['country'] = 'New country name'
        response = self.client.post(self.add_request_url, self.data)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertEqual(len(mail.outbox), 1)
        msg = "Country name error but no warning email was sent."
        self.assertIn(
            "Country name error.",
            mail.outbox[0].subject,
            msg
        )
        mail.outbox = []
 
    def test_the_request_email(self):
        self.client.post(self.add_request_url, self.data)
        self.assertTrue(
            CrmEmail.objects.filter(
                subject=self.data['subject'],
                incoming=True,
                from_field=self.data['email'],
            ).exists(),
            'The Email does not exist in db'
        )

    def test_the_lead(self):
        self.client.post(self.add_request_url, self.data)
        req = Request.objects.get(
            request_for=self.data['subject'],
            first_name=self.data['name'],
            email=self.data['email'],
            phone=self.data['phone']
        )

        self.common_part_of_the_code(req)

        lead = req.lead
        msg = "The lead was not created"
        self.assertTrue(lead, msg)
        msg = "Wrong lead first name"
        self.assertEqual(lead.first_name, self.request_data['name'], msg)
        msg = "Wrong lead email"
        self.assertEqual(lead.email, self.request_data['email'], msg)
        msg = "Wrong lead company name"
        self.assertEqual(lead.company_name, self.request_data['company'], msg)
        msg = "Wrong lead company phone"
        self.assertEqual(lead.phone, self.request_data['phone'], msg)

        deal = req.deal
        msg = "The deal was not created"
        self.assertTrue(deal, msg)
        msg = "Wrong deal name"
        self.assertEqual(deal.name, self.request_data['subject'], msg)
        msg = "The Deal is not active"
        self.assertTrue(deal.active, msg)

        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)
        msg = "The subject of the notifying message is not correct."
        self.assertIn(
            str(DEAL_OWNER_NOTICE),
            mail.outbox[0].subject,
            msg
        )
        msg = "The email address of the notifying message is not correct."
        self.assertEqual(
            mail.outbox[0].to[0],
            self.manager.email,
            msg
        )
        mail.outbox = []

    def test_create_company_contact(self):
        Company.objects.create(
            full_name='My Company LLC',
            email="office@example.com>",
            owner=self.manager
        )
        self.data['name'] = "Bill Anderson"
        self.client.post(self.add_request_url, self.data)

        req = Request.objects.get(
            request_for=self.data['subject'],
            first_name=self.data['name'].partition(' ')[0],
            email=self.data['email'],
            phone=self.data['phone']
        )
        self.common_part_of_the_code(req)
        msg = "The contact was not created"
        self.assertTrue(req.contact, msg)
        mail.outbox = []

    def test_iframe_request(self):
        lead_sources = LeadSource.objects.filter(name="website form (iframe)").first()
        site = Site.objects.get_current()
        uri = reverse('contact_form', args=(lead_sources.uuid,))
        request_url = f"https://{site.domain}{uri}"
        factory = RequestFactory()
        request = factory.get(request_url)
        request.user = AnonymousUser()
        self.run_iframe_request(request, factory, request_url, lead_sources)
        with self.settings(GOOGLE_RECAPTCHA_SITE_KEY='',
                           GOOGLE_RECAPTCHA_SECRET_KEY=''):
            self.run_iframe_request(request, factory, request_url, lead_sources)
        try:
            GeoIP2()
            self.run_get_country_and_city_test(request)
        except GeoIP2Exception as err:
            print(f"Geo test skipped - {err}")

    def run_get_country_and_city_test(self, request):
        data = {}
        request.META['REMOTE_ADDR'] = '92.249.66.247'
        get_country_and_city(request, data)
        self.assertEqual(data['country'], 'Ukraine')
        self.assertEqual(data['city'], 'Kyiv')
        request.META['REMOTE_ADDR'] = "127.0.0.1"
        err = get_country_and_city(request, data)
        if not err:
            self.fail(str(err))

    def run_iframe_request(self, request, factory, request_url, lead_sources):
        response = contact_form(request, lead_sources.uuid)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        content = response.content
        self.assertIn(str(lead_sources.uuid).encode(), content,
                      "The uuid token not found in response.")
        self.data['leadsource_token'] = lead_sources.uuid
        request = factory.post(request_url, self.data)
        response = contact_form(request, lead_sources.uuid)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        content = response.content
        thanks_message = _("Dear {}, thanks for your request!").format(self.data['name'])
        self.assertIn(thanks_message, content.decode(),
                      "The 'thanks' message not found in response.")
        self.assertTrue(
            Request.objects.filter(
                request_for=self.data['subject'],
                first_name=self.data['name'],
                email=self.data['email'],
                phone=self.data['phone'],
                # country__name=self.data['country'],
                # city__name=self.data['city'],
                # city_name=self.data['city']
            ).exists(),
            "The Request does not exist in db"
        )

    def common_part_of_the_code(self, req):
        req_url = reverse("site:crm_request_change", args=(req.id,))
        response = self.client.get(req_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertContains(response, 'My Company LLC')
        self.assertNotEqual(response.context['adminform'].form.initial, {
        }, "User has no change permission")
        data = get_adminform_initials(response)
        data['_create-deal'] = ''
        data['owner'] = str(self.manager.id)
        response = self.client.post(req_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertNoFormErrors(response)
        req.refresh_from_db()
