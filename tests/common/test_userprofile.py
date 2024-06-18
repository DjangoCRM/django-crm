from random import random
from django.test import tag
from django.urls import reverse

from common.models import UserProfile
from common.utils.helpers import USER_MODEL
from tests.base_test_classes import BaseTestCase

# manage.py test tests.common.test_userprofile --keepdb


@tag('TestCase')
class TestUserProfile(BaseTestCase):
    """Test UserProfile"""

    def setUp(self):
        print("Run Test Method:", self._testMethodName)

    def test_userprofile(self):
        self.adam = USER_MODEL.objects.get(username="Adam.Admin")
        add_url = reverse('admin:auth_user_add')
        self.client.force_login(self.adam)
        username = f"TestUser{random()}"
        data = {
            'username': username,
            'password1': "12est34ser",
            'password2': "12est34ser"
        }
        response = self.client.post(add_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertNoFormErrors(response)
        try:
            user = USER_MODEL.objects.get(username=username)
            self.assertTrue(user.groups.filter(name='co-workers').exists())
            self.assertTrue(UserProfile.objects.filter(user=user).exists())
        except USER_MODEL.DoesNotExist as e:
            self.fail(e)
