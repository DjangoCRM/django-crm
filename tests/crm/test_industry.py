from random import random
from django.conf import settings
from django.contrib.auth.models import Group
from django.test import tag
from django.urls import reverse

from common.utils.for_translation import STR_FOR_TRANS
from common.utils.helpers import USER_MODEL
from tests.base_test_classes import BaseTestCase
from tests.utils.helpers import get_adminform_initials

# python manage.py test tests.crm.test_industry --keepdb

TO_TRANSLATE_FILE_PATH = settings.BASE_DIR / 'crm' / 'models' / 'to_translate.txt'


@tag('TestCase')
class TestIndustry(BaseTestCase):
    """Test Industry"""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = USER_MODEL.objects.get(
            username="Adam.Admin")
        cls.department = Group.objects.get(name="Global sales")
        cls.add_url = reverse("admin:crm_industry_add")
        cls.changelist_url = reverse("admin:crm_industry_changelist")

    def setUp(self):
        print("Run Test Method:", self._testMethodName)
        self.client.force_login(self.user)

    def test_add_industry(self):
        f = open(TO_TRANSLATE_FILE_PATH, 'r')
        file_content = f.read()
        f.close()
        self.response = self.client.get(self.add_url, follow=True)
        self.assertEqual(self.response.status_code, 200,
                         self.response.reason_phrase)
        data = get_adminform_initials(self.response)
        random_name = f"Industy_{random()}"
        data['name'] = random_name
        data['department'] = self.department.id
        response = self.client.post(self.add_url, data, follow=True)
        self.assertNoFormErrors(response)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertEqual(response.redirect_chain[0][0], self.changelist_url)
        # open Industy changlist
        self.response = self.client.get(self.changelist_url, follow=True)
        self.assertEqual(self.response.status_code, 200,
                         self.response.reason_phrase)
        # checking the addition of the name of the industry translation.
        f = open(TO_TRANSLATE_FILE_PATH, 'r')
        txt = f.read()
        if txt.find(STR_FOR_TRANS.format(random_name)) == -1:
            self.fail("The industry name has not been added for translation.")        
        f.close()
        f = open(TO_TRANSLATE_FILE_PATH, 'w')
        f.write(file_content)
        f.close()
