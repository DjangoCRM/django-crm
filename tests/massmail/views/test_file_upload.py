import tempfile
import shutil
from django.test import TestCase, override_settings, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.conf import settings
from .forms import UploadFileForm  # Adjust import based on your app name

# Create a temporary directory for media files during tests
TEMP_MEDIA_ROOT = tempfile.mkdtemp()

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ImageUploadTests(TestCase):
    
    @classmethod
    def tearDownClass(cls):
        # Clean up the temporary directory after tests finish
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    ## --- Form & Validator Tests ---

    def test_form_validation_with_valid_extension(self):
        """Form should be valid for jpg, png, or gif."""
        file_data = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        form = UploadFileForm(files={'file': file_data})
        self.assertTrue(form.is_valid())

    def test_form_validation_with_invalid_extension(self):
        """Form should be invalid for forbidden extensions like .pdf or .exe."""
        file_data = SimpleUploadedFile("test_file.pdf", b"file_content", content_type="application/pdf")
        form = UploadFileForm(files={'file': file_data})
        self.assertFalse(form.is_valid())
        self.assertIn('file', form.errors)

    ## --- View Tests ---

    def test_file_upload_view_get(self):
        """GET request should return the upload form."""
        # Note: Ensure 'file_upload' is named in your urls.py or use the path directly
        response = self.client.get('/upload-path/') # Replace with reverse('your_url_name')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "massmail/pic_upload.html")
        self.assertIsInstance(response.context['form'], UploadFileForm)

    def test_file_upload_success_post(self):
        """Valid POST should save the file and return the close-window script."""
        image = SimpleUploadedFile("vacation.png", b"fake_png_data", content_type="image/png")
        
        response = self.client.post('/upload-path/', {'file': image})
        
        # Check response content
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'window.close()')

        # Verify file was actually written to the filesystem
        expected_path = settings.MEDIA_ROOT / 'pics' / 'vacation.png'
        self.assertTrue(expected_path.exists())
