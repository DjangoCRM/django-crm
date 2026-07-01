from pathlib import Path
from tempfile import TemporaryDirectory

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings, tag
from django.urls import reverse

from common.utils.helpers import USER_MODEL
from massmail.views.file_upload import UploadFileForm
from tests.base_test_classes import BaseTestCase


@tag("TestCase")
class TestFileUpload(BaseTestCase):
    """Tests for the staff-only image upload view."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.admin = USER_MODEL.objects.get(username="Adam.Admin")
        cls.view_url = reverse("pic_upload")

    def setUp(self):
        

        self.client.force_login(self.admin)
        self.temp_media_dir = TemporaryDirectory()
        self.addCleanup(self.temp_media_dir.cleanup)

    def test_get_renders_upload_form(self):
        response = self.client.get(self.view_url)

        self.assertEqual(response.status_code, 200, response.reason_phrase)
        self.assertTemplateUsed(response, "massmail/pic_upload.html")
        self.assertIsInstance(response.context["form"], UploadFileForm)

    def test_valid_image_file_is_uploaded(self):
        with override_settings(MEDIA_ROOT=Path(self.temp_media_dir.name)):
            upload_directory = settings.MEDIA_ROOT / "pics"
            upload_directory.mkdir()

            image_file = SimpleUploadedFile(
                "company_logo.png",
                b"test image content",
                content_type="image/png",
            )

            response = self.client.post(
                self.view_url,
                {"file": image_file},
            )

            uploaded_file = upload_directory / "company_logo.png"

            self.assertEqual(response.status_code, 200, response.reason_phrase)
            self.assertIn(b"window.close()", response.content)
            self.assertTrue(uploaded_file.exists())
            self.assertEqual(uploaded_file.read_bytes(), b"test image content")

    def test_invalid_file_extension_is_rejected(self):
        with override_settings(MEDIA_ROOT=Path(self.temp_media_dir.name)):
            upload_directory = settings.MEDIA_ROOT / "pics"
            upload_directory.mkdir()

            invalid_file = SimpleUploadedFile(
                "document.pdf",
                b"not an image",
                content_type="application/pdf",
            )

            response = self.client.post(
                self.view_url,
                {"file": invalid_file},
            )

            uploaded_file = upload_directory / "document.pdf"

            self.assertEqual(response.status_code, 200, response.reason_phrase)
            self.assertIsInstance(response.context["form"], UploadFileForm)
            self.assertIn("file", response.context["form"].errors)
            self.assertFalse(uploaded_file.exists())

    def test_non_staff_user_is_redirected(self):
        user = USER_MODEL.objects.create_user(
            username="regular_user",
            password="test-password",
            is_staff=False,
        )
        self.client.force_login(user)

        response = self.client.get(self.view_url)

        self.assertEqual(response.status_code, 302, response.reason_phrase)