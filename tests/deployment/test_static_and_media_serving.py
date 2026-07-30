"""Tests for static and media serving in container runtimes."""

from __future__ import annotations

import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from django.conf import settings
from django.core.management import call_command
from django.test import Client, SimpleTestCase, override_settings, tag

from common.utils.helpers import USER_MODEL
from tests.base_test_classes import BaseTestCase

FIXTURE_MEDIA = Path(__file__).resolve().parents[1] / 'fixtures' / 'sample_upload.txt'
ADMIN_STATIC = 'admin/css/base.css'


class WhiteNoiseMiddlewareOrderingTests(SimpleTestCase):
    def test_whitenoise_follows_security_middleware(self):
        middleware = settings.MIDDLEWARE
        security_index = middleware.index('django.middleware.security.SecurityMiddleware')
        whitenoise_index = middleware.index('whitenoise.middleware.WhiteNoiseMiddleware')
        self.assertEqual(whitenoise_index, security_index + 1)


@tag('TestCase')
class ProtectedMediaViewTests(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.staff_user = USER_MODEL.objects.get(username='Adam.Admin')

    def setUp(self):
        self.client = Client()
        self.temp_media_dir = TemporaryDirectory()
        self.addCleanup(self.temp_media_dir.cleanup)
        media_root = Path(self.temp_media_dir.name)
        sample_path = media_root / 'sample_upload.txt'
        shutil.copy(FIXTURE_MEDIA, sample_path)
        self.media_settings = override_settings(
            DEBUG=False,
            SERVE_MEDIA_FILES=True,
            MEDIA_ROOT=media_root,
        )
        self.media_settings.enable()
        self.addCleanup(self.media_settings.disable)

    def test_anonymous_request_redirects_to_login(self):
        response = self.client.get('/media/sample_upload.txt')

        self.assertEqual(response.status_code, 302)
        self.assertIn(settings.LOGIN_URL, response['Location'])

    def test_authenticated_non_staff_receives_forbidden(self):
        user = USER_MODEL.objects.create_user(
            username='media_non_staff',
            password='test-password',
            is_staff=False,
        )
        self.client.force_login(user)

        response = self.client.get('/media/sample_upload.txt')

        self.assertEqual(response.status_code, 403)

    def test_staff_user_receives_media_file(self):
        self.client.force_login(self.staff_user)

        response = self.client.get('/media/sample_upload.txt')

        self.assertEqual(response.status_code, 200)
        body = b''.join(response.streaming_content)
        self.assertIn(b'sample media fixture', body)

    def test_path_traversal_attempt_returns_not_found(self):
        self.client.force_login(self.staff_user)

        response = self.client.get('/media/../manage.py')

        self.assertEqual(response.status_code, 404)


@tag('TestCase')
class StaticAndMediaIntegrationTests(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.staff_user = USER_MODEL.objects.get(username='Adam.Admin')

    def test_debug_false_serves_collected_admin_static_and_staff_media(self):
        with TemporaryDirectory() as static_root, TemporaryDirectory() as media_root:
            sample_path = Path(media_root) / 'sample_upload.txt'
            shutil.copy(FIXTURE_MEDIA, sample_path)

            with override_settings(
                DEBUG=False,
                SERVE_MEDIA_FILES=True,
                STATIC_ROOT=static_root,
                MEDIA_ROOT=media_root,
                STORAGES={
                    'default': {
                        'BACKEND': 'django.core.files.storage.FileSystemStorage',
                    },
                    'staticfiles': {
                        'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
                    },
                },
            ):
                call_command('collectstatic', interactive=False, verbosity=0)
                client = Client()

                static_response = client.get(f'{settings.STATIC_URL}{ADMIN_STATIC}')
                self.assertEqual(static_response.status_code, 200)
                self.assertTrue(static_response['Content-Type'].startswith('text/css'))
                cache_control = static_response.get('Cache-Control', '')
                self.assertIn('max-age', cache_control)

                client.force_login(self.staff_user)
                media_response = client.get('/media/sample_upload.txt')
                self.assertEqual(media_response.status_code, 200)
                media_body = b''.join(media_response.streaming_content)
                self.assertIn(b'sample media fixture', media_body)

                client.logout()
                anonymous_response = client.get('/media/sample_upload.txt')
                self.assertEqual(anonymous_response.status_code, 302)

    def test_serve_media_files_false_returns_not_found(self):
        self.client.force_login(self.staff_user)
        with override_settings(DEBUG=False, SERVE_MEDIA_FILES=False):
            response = self.client.get('/media/sample_upload.txt')

        self.assertEqual(response.status_code, 404)
