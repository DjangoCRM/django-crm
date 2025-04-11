from django.urls import reverse
from django.contrib.messages import get_messages

from common.utils.helpers import USER_MODEL
from massmail.forms.radio_select_form import RadioSelectForm
from tests.base_test_classes import BaseTestCase


class SelectRecipientTypeTests(BaseTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.manager = USER_MODEL.objects.get(username="Andrew.Manager.Global")
        cls.view_url = reverse('select_recipient_type')

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)
        self.client.force_login(self.manager)

    def test_redirects_to_contact_massmail_when_choice_is_contact(self):
        response = self.client.get(self.view_url)
        self.assertEqual(response.status_code, 200, response.reason_phrase)

        response = self.client.post(self.view_url, {'choice': '1'})
        self.assertEqual(response.status_code, 302, response.reason_phrase)
        self.assertEqual(response.url, reverse('site:contact_make_massmail'))   # NOQA

    def test_redirects_to_company_massmail_when_choice_is_company(self):
        response = self.client.post(self.view_url, {'choice': '2'})
        self.assertEqual(response.status_code, 302, response.reason_phrase)
        self.assertEqual(response.url, reverse('site:company_make_massmail'))   # NOQA

    def test_shows_warning_and_redirects_to_lead_list_when_choice_is_lead(self):
        response = self.client.post(self.view_url, {'choice': '3'}, follow=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Use the 'Action' menu.")
        self.assertEqual(response.redirect_chain[-1][0], reverse('site:crm_lead_changelist'))

    def test_renders_form_when_request_is_get(self):
        response = self.client.get(self.view_url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], RadioSelectForm)
        self.assertContains(response, "Please select the type of recipients")
