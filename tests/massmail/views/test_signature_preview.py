from random import random
from django.conf import settings
from django.test import tag
from django.urls import reverse

from common.utils.helpers import get_department_id
from common.utils.helpers import USER_MODEL
from massmail.models import Signature
from tests.base_test_classes import BaseTestCase

# manage.py test tests.massmail.views.test_signature_preview --keepdb


@tag('TestCase')
class TestSignaturePreview(BaseTestCase):
    """Message signature preview test"""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        file_name = "1x1image.pgm"
        cls.file_in_media = settings.MEDIA_ROOT / file_name
        cls.file_in_static = settings.STATIC_ROOT / file_name
        cls.file_in_media.write_text('P5 1 1 1\n\0')
        cls.file_in_static.write_text('P5 1 1 1\n\0')
        cls.owner = USER_MODEL.objects.get(username="Andrew.Manager.Global")
        cls.department_id = get_department_id(cls.owner)

    def setUp(self):
        print("Run Test Method:", self._testMethodName)
        self.client.force_login(self.owner)
        self.random_value = random()

    def test_html_signature_preview(self):
        content = """
        <div>
        <p>Kind regards,</p>
        <p>Global Sales Team</p>
        <p><img src="{% cid_media '1x1image.pgm' %}" style="width:100%"></p>
        <p><img src="{% cid_static '1x1image.pgm' %}" style="width:100%"></p>
        </div>
        """

        signature = Signature.objects.create(
            content=content,
            type=Signature.HTML,
            owner=self.owner,
            department_id=self.department_id
        )
        url = reverse("signature_preview")
        preview_url = f"{url}?signature={signature.id}"
        response = self.client.get(preview_url, follow=True)
        self.assertEqual(response.status_code, 200,
                         response.reason_phrase)
        response_content = response.content.decode()
        self.assertRegex(response_content,
                         r'src=\"\S+media\S+1x1image\.pgm\"')
        self.assertRegex(response_content,
                         r'src=\"\S+static\S+1x1image\.pgm\"')

    def test_txt_signature_preview(self):
        content = f"Kind regards\n{self.random_value}"

        signature = Signature.objects.create(
            content=content,
            type=Signature.PLAIN_TEXT,
            owner=self.owner,
            department_id=self.department_id
        )
        url = reverse("signature_preview")
        preview_url = f"{url}?signature={signature.id}"
        response = self.client.get(preview_url, follow=True)
        self.assertEqual(response.status_code, 200,
                         response.reason_phrase)
        response_content = response.content.decode()
        self.assertIn(str(self.random_value), response_content)

    @classmethod
    def tearDownClass(cls):
        cls.file_in_media.unlink()
        cls.file_in_static.unlink()
        super().tearDownClass()
