from django.test import tag
from django.urls import reverse

from common.utils.helpers import USER_MODEL
from crm.utils.helpers import PHONE_NUMBER_MSG
from tests.base_test_classes import BaseTestCase
from tests.utils.helpers import get_adminform_initials

# python manage.py test tests.crm.test_add_request --keepdb


@tag('TestCase')
class TestAddRequest(BaseTestCase):
    """Test add Request"""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.add_url = reverse("site:crm_request_add")
        cls.changelist_url = reverse("site:crm_request_changelist")
        cls.user = USER_MODEL.objects.get(username="Darian.Manager.Co-worker.Head.Global")
        cls.request_data = {
            'request_for': "Test request",
            'first_name': "John",
            'email': "John@company.com"
        }

    def setUp(self):
        print("Run Test Method:", self._testMethodName)
        self.client.force_login(self.user)
        self.response = self.client.get(self.add_url, follow=True)

    def test_add_request(self):
        self.assertEqual(self.response.status_code, 200, self.response.reason_phrase)
        data = get_adminform_initials(self.response)
        data.update(self.request_data)
        data['phone'] = "+0 (123) 345-67.89"
        response = self.client.post(self.add_url, data, follow=True)
        self.assertNoFormErrors(response)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertEqual(response.redirect_chain[0][0], self.changelist_url)
        # open request changlist
        self.response = self.client.get(self.changelist_url, follow=True)
        self.assertEqual(self.response.status_code, 200, self.response.reason_phrase)

    def test_add_invalid_phone(self):
        self.assertEqual(self.response.status_code, 200, self.response.reason_phrase)
        data = get_adminform_initials(self.response)
        data.update(self.request_data)
        data['phone'] = "unknown"
        response = self.client.post(self.add_url, data, follow=True)
        self.assertFormError(response.context['adminform'], 'phone', PHONE_NUMBER_MSG)
