from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import tag
from django.urls import reverse

from common.utils.helpers import USER_MODEL
from tests.base_test_classes import BaseTestCase

# manage.py test tests.massmail.views.test_file_upload --keepdb


@tag('TestCase')
class TestFileUpload(BaseTestCase):
    """file_upload view tests"""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.staff_user = USER_MODEL.objects.get(username="Andrew.Manager.Global")
        cls.non_staff_user = USER_MODEL.objects.create_user(
            username="Test.NonStaff",
            email="nonstaff@example.com",
            password="testpass123",
            is_staff=False,
            is_active=True,
        )

    def setUp(self):
        print("Run Test Method:", self._testMethodName)
        self.url = reverse("pic_upload")
        self.pics_dir = settings.MEDIA_ROOT / 'pics'
        self.pics_dir.mkdir(parents=True, exist_ok=True)

    def test_anonymous_user_redirected(self):
        """Anonymous users should be redirected to admin login."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302, response.reason_phrase)

    def test_non_staff_user_redirected(self):
        """Non-staff users should be redirected to admin login."""
        self.client.force_login(self.non_staff_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302, response.reason_phrase)

    def test_staff_user_get_upload_form(self):
        """Staff users should see the upload form on GET request."""
        self.client.force_login(self.staff_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertContains(response, 'enctype="multipart/form-data"')
        self.assertContains(response, 'id_file')

    def test_successful_image_upload(self):
        """Valid image file should be saved and return close script."""
        self.client.force_login(self.staff_user)
        upload_file = SimpleUploadedFile(
            'test_upload.png',
            b'\x89PNG\r\n\x1a\n',
            content_type='image/png'
        )
        response = self.client.post(self.url, {'file': upload_file})
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertIn(
            'window.close()',
            response.content.decode()
        )
        saved_path = self.pics_dir / 'test_upload.png'
        self.assertTrue(saved_path.exists())
        saved_path.unlink()

    def test_invalid_file_extension(self):
        """Files with disallowed extensions should be rejected."""
        self.client.force_login(self.staff_user)
        upload_file = SimpleUploadedFile(
            'test_file.txt',
            b'not an image',
            content_type='text/plain'
        )
        response = self.client.post(self.url, {'file': upload_file})
        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertContains(response, 'is not allowed')