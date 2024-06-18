from django.test import tag
from django.urls import reverse

from common.utils.helpers import USER_MODEL
from crm.forms.admin_forms import STATE_EXISTS_STR
from crm.forms.admin_forms import WRONG_CODE_WARNING
from crm.models import Currency
from tests.base_test_classes import BaseTestCase
from tests.utils.helpers import get_adminform_initials

# python manage.py test tests.crm.test_currency --keepdb


@tag('TestCase')
class TestCurrency(BaseTestCase):
    """Test add Currency"""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.add_url = reverse("site:crm_currency_add")
        cls.changelist_url = reverse("site:crm_currency_changelist")
        cls.user = USER_MODEL.objects.get(username="Adam.Admin")
        cls.currency_data = {
            'name': "GBP",
            'rate_to_state_currency': 1,
            'rate_to_marketing_currency': 1
        }

    def setUp(self):
        print("Run Test Method:", self._testMethodName)
        self.client.force_login(self.user)
        self.response = self.client.get(self.add_url, follow=True)

    def test_add_currency(self):
        self.assertEqual(self.response.status_code, 200, self.response.reason_phrase)
        data = get_adminform_initials(self.response)
        data.update(self.currency_data)
        # data['phone'] = "+0 (123) 345-67.89"
        response = self.client.post(self.add_url, data, follow=True)
        self.assertNoFormErrors(response)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertEqual(response.redirect_chain[0][0], self.changelist_url)
        # open currency changlist
        self.response = self.client.get(self.changelist_url, follow=True)
        self.assertEqual(self.response.status_code, 200, self.response.reason_phrase)

    def test_add_wrong_currency(self):
        """Add wrong currencies alphabetic code"""
        self.assertEqual(self.response.status_code, 200, self.response.reason_phrase)
        data = get_adminform_initials(self.response)
        data.update(self.currency_data)
        data['name'] = "GBz"
        response = self.client.post(self.add_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertFormError(response.context['adminform'], 'name', [WRONG_CODE_WARNING])

    def test_change_currency(self):
        currency = Currency.objects.create(**self.currency_data)
        change_url = reverse("site:crm_currency_change", args=(currency.id,))
        response = self.client.get(change_url, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertEqual(response.redirect_chain, [])
        data = get_adminform_initials(response)
        data['is_state_currency'] = True
        response = self.client.post(change_url, data, follow=True)
        self.assertFormError(response.context['adminform'], 'is_state_currency', errors=[STATE_EXISTS_STR])
        del data['is_state_currency']
        data['rate_to_marketing_currency'] = 1.1
        response = self.client.post(change_url, data, follow=True)
        self.assertNoFormErrors(response)   
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertEqual(response.redirect_chain[0][0], self.changelist_url)
