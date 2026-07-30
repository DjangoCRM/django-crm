import os
from unittest import mock

from django.core.exceptions import ImproperlyConfigured
from django.test import Client, SimpleTestCase, override_settings

from tests.fixtures.voip_env import (
    CHARACTERIZATION_VOIP_ENV,
    CUSTOM_PREFIX_ENV,
    UNCONFIGURED_VOIP_ENV,
    VALID_VOIP_ENV,
    WEBHOOK_VOIP_ENV,
)
from webcrm.config import SECRET_MASK, ConfigAccessor
from webcrm.security_config import (
    build_recaptcha_settings,
    build_url_prefix_settings,
    normalize_url_prefix,
)
from webcrm.voip_config import build_voip_settings


class VoipSettingsCharacterizationTests(SimpleTestCase):
    def test_characterization_defaults_match_prior_literals(self):
        with mock.patch.dict(os.environ, CHARACTERIZATION_VOIP_ENV, clear=True):
            voip_settings = build_voip_settings()
            url_prefixes = build_url_prefix_settings()
        self.assertEqual(len(voip_settings['VOIP']), 1)
        self.assertEqual(voip_settings['VOIP'][0]['PROVIDER'], 'Zadarma')
        self.assertEqual(voip_settings['VOIP'][0]['ALLOWLIST'], ['185.45.152.42'])
        self.assertEqual(voip_settings['VOIP'][0]['OPTIONS']['key'], '123')
        self.assertEqual(voip_settings['VOIP'][0]['OPTIONS']['secret'], 'secret')
        self.assertEqual(url_prefixes['SECRET_CRM_PREFIX'], '123/')
        self.assertEqual(url_prefixes['SECRET_ADMIN_PREFIX'], '456-admin/')
        self.assertEqual(url_prefixes['SECRET_LOGIN_PREFIX'], '789-login/')


class NormalizeUrlPrefixTests(SimpleTestCase):
    def test_strips_leading_and_adds_trailing_slash(self):
        self.assertEqual(normalize_url_prefix('SECRET_CRM_PREFIX', '/custom-crm/'), 'custom-crm/')

    def test_adds_trailing_slash_when_missing(self):
        self.assertEqual(normalize_url_prefix('SECRET_ADMIN_PREFIX', 'custom-admin'), 'custom-admin/')

    def test_rejects_whitespace(self):
        with self.assertRaises(ImproperlyConfigured):
            normalize_url_prefix('SECRET_CRM_PREFIX', 'bad prefix/')

    def test_rejects_scheme(self):
        with self.assertRaises(ImproperlyConfigured):
            normalize_url_prefix('SECRET_CRM_PREFIX', 'https://example.com/')


class VoipConfigUnitTests(SimpleTestCase):
    def test_unconfigured_voip_returns_empty_list(self):
        with mock.patch.dict(os.environ, UNCONFIGURED_VOIP_ENV, clear=True):
            settings = build_voip_settings()
        self.assertEqual(settings['VOIP'], [])

    def test_half_configured_voip_raises(self):
        env = {**VALID_VOIP_ENV, 'ZADARMA_SECRET': ''}
        with mock.patch.dict(os.environ, env, clear=True):
            with self.assertRaises(ImproperlyConfigured) as ctx:
                build_voip_settings()
        self.assertIn('ZADARMA_SECRET', str(ctx.exception))

    def test_voip_assembly_includes_allowlist(self):
        with mock.patch.dict(os.environ, VALID_VOIP_ENV, clear=True):
            settings = build_voip_settings()
        self.assertEqual(
            settings['VOIP'][0]['ALLOWLIST'],
            ['185.45.152.42', '203.0.113.10'],
        )

    def test_recaptcha_secret_is_masked_in_diagnostics(self):
        accessor = ConfigAccessor()
        accessor.register_secret('GOOGLE_RECAPTCHA_SECRET_KEY')
        with mock.patch.dict(
            os.environ,
            {'GOOGLE_RECAPTCHA_SECRET_KEY': 'super-secret-recaptcha-key'},
            clear=True,
        ):
            accessor.get('GOOGLE_RECAPTCHA_SECRET_KEY', secret=True)
            diagnostics = accessor.diagnostics()
        self.assertEqual(diagnostics['GOOGLE_RECAPTCHA_SECRET_KEY'], SECRET_MASK)

    def test_recaptcha_secret_never_appears_in_logs(self):
        accessor = ConfigAccessor()
        with self.assertLogs('webcrm.config', level='DEBUG') as captured:
            with mock.patch.dict(
                os.environ,
                {'GOOGLE_RECAPTCHA_SECRET_KEY': 'super-secret-recaptcha-key'},
                clear=True,
            ):
                accessor.get('GOOGLE_RECAPTCHA_SECRET_KEY', secret=True)
        joined = '\n'.join(captured.output)
        self.assertIn(SECRET_MASK, joined)
        self.assertNotIn('super-secret-recaptcha-key', joined)

    def test_recaptcha_keys_resolve_from_environment(self):
        with mock.patch.dict(os.environ, VALID_VOIP_ENV, clear=True):
            recaptcha = build_recaptcha_settings()
        self.assertEqual(recaptcha['GOOGLE_RECAPTCHA_SITE_KEY'], 'placeholder-recaptcha-site-key')
        self.assertEqual(
            recaptcha['GOOGLE_RECAPTCHA_SECRET_KEY'],
            'placeholder-recaptcha-secret-key',
        )


class VoipSettingsIntegrationTests(SimpleTestCase):
    def test_custom_prefixes_resolve_for_urls(self):
        with mock.patch.dict(os.environ, CUSTOM_PREFIX_ENV, clear=True):
            prefixes = build_url_prefix_settings()
        self.assertEqual(prefixes['SECRET_CRM_PREFIX'], 'custom-crm/')
        self.assertEqual(prefixes['SECRET_ADMIN_PREFIX'], 'custom-admin/')
        self.assertEqual(prefixes['SECRET_LOGIN_PREFIX'], 'custom-login/')

    @override_settings(ROOT_URLCONF='webcrm.urls')
    def test_webhook_denies_non_allowlisted_ip(self):
        with mock.patch.dict(os.environ, WEBHOOK_VOIP_ENV, clear=True):
            voip_settings = build_voip_settings()
        client = Client(REMOTE_ADDR='198.51.100.25')
        with self.settings(
            VOIP=voip_settings['VOIP'],
            ZADARMA_PROVIDER_ALLOWLIST=voip_settings['ZADARMA_PROVIDER_ALLOWLIST'],
            VOIP_FORWARDING_IP=voip_settings['VOIP_FORWARDING_IP'],
        ):
            with self.assertLogs('voip.views.voipwebhook', level='WARNING') as captured:
                response = client.get('/voip/zd/?zd_echo=1')
        self.assertEqual(response.status_code, 403)
        self.assertTrue(any('ip_not_allowlisted' in line for line in captured.output))

    @override_settings(ROOT_URLCONF='webcrm.urls')
    def test_webhook_without_voip_configuration_returns_denial(self):
        client = Client(REMOTE_ADDR='185.45.152.42')
        with self.settings(VOIP=[], ZADARMA_PROVIDER_ALLOWLIST=[]):
            with self.assertLogs('voip.views.voipwebhook', level='WARNING') as captured:
                response = client.get('/voip/zd/?zd_echo=1')
        self.assertEqual(response.status_code, 403)
        self.assertTrue(any('voip_not_configured' in line for line in captured.output))
