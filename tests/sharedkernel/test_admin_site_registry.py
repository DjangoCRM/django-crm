"""Characterization tests for admin-site registry wiring."""

from __future__ import annotations

import json
from pathlib import Path

from django.contrib import admin
from django.test import tag

from sharedkernel.adminsites import CRM_SITE_NAME
from sharedkernel.adminsites import get_admin_site
from tests.base_test_classes import BaseTestCase

BASELINE_FILE = Path(__file__).resolve().parent / 'fixtures' / 'admin_site_registry_baseline.json'


def _admin_class_path(admin_class) -> str:
    if isinstance(admin_class, type):
        klass = admin_class
    else:
        klass = admin_class.__class__
    return f'{klass.__module__}.{klass.__qualname__}'


def _registry_snapshot(site) -> dict[str, str]:
    return {
        model._meta.label: _admin_class_path(admin_class)
        for model, admin_class in sorted(
            site._registry.items(),
            key=lambda item: item[0]._meta.label,
        )
    }


def _url_names(site) -> list[str]:
    names: list[str] = []

    def walk(patterns):
        for pattern in patterns:
            nested = getattr(pattern, 'url_patterns', None)
            if nested is not None:
                walk(nested)
                continue
            if pattern.name:
                names.append(pattern.name)

    walk(site.get_urls())
    return sorted(names)


@tag('TestCase')
class AdminSiteRegistryCharacterizationTests(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        if not BASELINE_FILE.exists():
            raise FileNotFoundError(
                f'Missing {BASELINE_FILE}. Run '
                'tests.sharedkernel.test_admin_site_registry.'
                'AdminSiteRegistryBaselineGenerator.test_write_baseline first.',
            )
        cls.baseline = json.loads(BASELINE_FILE.read_text(encoding='utf-8'))

    def test_default_admin_registry_matches_baseline(self):
        self.assertEqual(
            _registry_snapshot(admin.site),
            self.baseline['default_admin_registry'],
        )

    def test_crm_admin_registry_matches_baseline(self):
        self.assertEqual(
            _registry_snapshot(get_admin_site(CRM_SITE_NAME)),
            self.baseline['crm_admin_registry'],
        )

    def test_crm_site_disables_delete_selected(self):
        crm_site = get_admin_site(CRM_SITE_NAME)
        self.assertNotIn('delete_selected', crm_site.actions)

    def test_crm_site_url_names_match_baseline(self):
        self.assertEqual(
            _url_names(get_admin_site(CRM_SITE_NAME)),
            self.baseline['crm_admin_url_names'],
        )


@tag('TestCase')
class AdminSiteRegistryBaselineGenerator(BaseTestCase):
    def test_write_baseline(self):
        crm_site = get_admin_site(CRM_SITE_NAME)
        baseline = {
            'default_admin_registry': _registry_snapshot(admin.site),
            'crm_admin_registry': _registry_snapshot(crm_site),
            'crm_admin_url_names': _url_names(crm_site),
        }
        BASELINE_FILE.parent.mkdir(parents=True, exist_ok=True)
        BASELINE_FILE.write_text(
            json.dumps(baseline, indent=2, sort_keys=True) + '\n',
            encoding='utf-8',
        )
        self.assertTrue(BASELINE_FILE.exists())
