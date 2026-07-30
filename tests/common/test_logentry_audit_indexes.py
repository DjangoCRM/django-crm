"""Tests for LogEntry audit-search index migration."""

from __future__ import annotations

from django.db import connection
from django.test import TestCase

EXPECTED_INDEX_NAMES = {
    'crm_audit_log_object_id_idx',
    'crm_audit_log_action_time_idx',
    'crm_audit_log_user_id_idx',
    'crm_audit_log_content_type_id_idx',
}


class LogEntryAuditIndexTests(TestCase):
    def test_expected_indexes_are_present(self):
        with connection.cursor() as cursor:
            constraints = connection.introspection.get_constraints(
                cursor,
                'django_admin_log',
            )
        present = {
            name
            for name, meta in constraints.items()
            if meta['index'] and name in EXPECTED_INDEX_NAMES
        }
        self.assertEqual(present, EXPECTED_INDEX_NAMES)
