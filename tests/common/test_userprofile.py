from random import random
from django.contrib.auth.models import User
from django.test import tag
from django.urls import reverse

from common.models import UserProfile
from tests.base_test_classes import BaseTestCase
from tests.utils.helpers import get_adminform_initials

# manage.py test tests.common.test_userprofile --keepdb


@tag('TestCase')
class TestUserProfile(BaseTestCase):
    """Test UserProfile"""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.adam = User.objects.get(username="Adam.Admin")

    def setUp(self):
        print(" Run Test Method:", self._testMethodName)

    def test_changing_activity_status_in_userprofile_by_superuser(self):
        """
        Testing the ability of a superuser to change a user's activity status in their profile
        """
        self.tanya = User.objects.get(username="Tanya.Co-worker.Bookkeeping")
        profile = UserProfile.objects.get(user=self.tanya)
        change_url = reverse(
            'admin:common_userprofile_change', args=[profile.pk])
        self.client.force_login(self.adam)

        # Get the current is_active status
        response = self.client.get(change_url)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertContains(response, 'is_active')

        # Toggle the is_active status
        data = get_adminform_initials(response)
        current_status = self.tanya.is_active
        data['is_active'] = not current_status
        response = self.client.post(change_url, data, follow=True)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertNoFormErrors(response)

        # Refresh from database and check the status
        self.tanya.refresh_from_db()
        self.assertEqual(self.tanya.is_active, not current_status)

    def test_userprofile_creation_when_adding_user(self):
        """Test that UserProfile is created when adding a new user via admin."""
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
            user = User.objects.get(username=username)
            self.assertTrue(user.groups.filter(name='co-workers').exists())
            self.assertTrue(UserProfile.objects.filter(user=user).exists())
        except User.DoesNotExist as e:
            self.fail(e)
