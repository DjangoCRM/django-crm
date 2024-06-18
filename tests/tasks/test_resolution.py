import os
from random import random
from django.conf import settings
from django.test import tag
from django.urls import reverse

from common.utils.for_translation import STR_FOR_TRANS
from common.utils.helpers import USER_MODEL
from tests.base_test_classes import BaseTestCase
from tests.utils.helpers import get_adminform_initials

# python manage.py test tests.tasks.test_resolution --keepdb

TO_TRANSLATE_FILE_PATH = os.path.join(settings.BASE_DIR,
                                      'tasks', 'models', 'to_translate.txt')


@tag('TestCase')
class TestResolution(BaseTestCase):
    """Test Resolution"""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = USER_MODEL.objects.get(
            username="Adam.Admin")
        cls.add_url = reverse("admin:tasks_resolution_add")
        cls.changelist_url = reverse("admin:tasks_resolution_changelist")

    def setUp(self):
        print("Run Test Method:", self._testMethodName)
        self.client.force_login(self.user)

    def test_add_resolution(self):
        f = open(TO_TRANSLATE_FILE_PATH, 'r')
        file_content = f.read()
        f.close()
        self.response = self.client.get(self.add_url, follow=True)
        self.assertEqual(self.response.status_code, 200,
                         self.response.reason_phrase)
        data = get_adminform_initials(self.response)
        random_name = f"Resolution_{random()}"
        data['name'] = random_name
        data['index_number'] = 1
        response = self.client.post(self.add_url, data, follow=True)
        self.assertNoFormErrors(response)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertEqual(response.redirect_chain[0][0], self.changelist_url)
        # open Resolution chang list
        self.response = self.client.get(self.changelist_url, follow=True)
        self.assertEqual(self.response.status_code, 200,
                         self.response.reason_phrase)
        # checking the addition of the name of the resolution translation.
        f = open(TO_TRANSLATE_FILE_PATH, 'r')
        txt = f.read()
        f.close()
        f = open(TO_TRANSLATE_FILE_PATH, 'w')
        f.write(file_content)
        f.close()
        if txt.find(STR_FOR_TRANS.format(random_name)) == -1:
            self.fail("The Resolution name has not been added for translation.")
