from random import random
from django.conf import settings
from django.test import tag
from django.urls import reverse

from common.utils.helpers import get_department_id
from common.utils.helpers import USER_MODEL
from massmail.models import EmlMessage
from tests.base_test_classes import BaseTestCase

# manage.py test tests.massmail.views.test_message_preview --keepdb


@tag('TestCase')
class TestMessagePreview(BaseTestCase):
    """Massmail text message preview test"""

    def setUp(self):
        print("Run Test Method:", self._testMethodName)

    def test_message_preview(self):
        file_name = "1x1image.pgm"
        file_in_media = settings.MEDIA_ROOT / file_name
        file_in_static = settings.STATIC_ROOT / file_name
        file_in_media.write_text('P5 1 1 1\n\0')
        file_in_static.write_text('P5 1 1 1\n\0')
        subject = f"Happy New Year {random()}"
        content = """
        <div>
        <p><img src="{% cid_media '1x1image.pgm' %}" style="width:100%"></p>
        <p><img src="{% cid_static '1x1image.pgm' %}" style="width:100%"></p>
        </div>
        """
        owner = USER_MODEL.objects.get(username="Andrew.Manager.Global")
        message = EmlMessage.objects.create(
            subject=subject,
            content=content,
            owner=owner,
            department_id=get_department_id(owner)
        )
        preview_url = reverse("message_preview", args=(message.id,))
        self.client.force_login(owner)
        response = self.client.get(preview_url, follow=True)
        file_in_media.unlink()
        file_in_static.unlink()
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertIn(subject.encode(), response.content)
        response_content = response.content.decode()
        self.assertRegex(response_content,
                         r'src=\"\S+media\S+1x1image\.pgm\"')
        self.assertRegex(response_content,
                         r'src=\"\S+static\S+1x1image\.pgm\"')
