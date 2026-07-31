"""Unit tests for sharedkernel.adminsites registry."""

from django.contrib.admin import AdminSite
from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from sharedkernel import adminsites


class AdminSiteRegistryTests(SimpleTestCase):
    def setUp(self):
        super().setUp()
        self._original_registry = dict(adminsites._registry)

    def tearDown(self):
        adminsites._registry.clear()
        adminsites._registry.update(self._original_registry)
        super().tearDown()

    def test_register_and_get_round_trip(self):
        site = AdminSite(name='test-site')
        adminsites.register_admin_site('test_site', site)
        self.assertIs(adminsites.get_admin_site('test_site'), site)

    def test_duplicate_registration_raises(self):
        site = AdminSite(name='duplicate-site')
        adminsites.register_admin_site('duplicate_site', site)
        with self.assertRaises(ImproperlyConfigured) as ctx:
            adminsites.register_admin_site('duplicate_site', AdminSite(name='other'))
        self.assertIn('duplicate_site', str(ctx.exception))

    def test_unknown_site_raises_with_helpful_message(self):
        with self.assertRaises(ImproperlyConfigured) as ctx:
            adminsites.get_admin_site('missing_site')
        message = str(ctx.exception)
        self.assertIn('missing_site', message)
        self.assertIn('register_admin_site', message)

    def test_crm_site_name_constant(self):
        self.assertEqual(adminsites.CRM_SITE_NAME, 'crm')
