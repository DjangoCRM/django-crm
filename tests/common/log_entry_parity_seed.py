"""Deterministic LogEntry corpus for audit-search parity tests.

Run ``python manage.py dumpdata admin.logentry --pks ...`` after editing, or call
``build_parity_corpus()`` from a scratch script to regenerate
``tests/fixtures/log_entries_parity.json``.
"""

from __future__ import annotations

from datetime import datetime
from datetime import timezone as dt_timezone

from django.contrib import admin
from django.contrib.contenttypes.models import ContentType

from common.utils.helpers import USER_MODEL

PARITY_LOG_ENTRY_PKS = tuple(range(9001, 9013))


def build_parity_corpus(user=None, content_type=None):
    """Create the fixed-primary-key parity corpus in the active database."""
    user = user or USER_MODEL.objects.order_by('pk').first()
    content_type = content_type or ContentType.objects.get_for_model(USER_MODEL)
    action_time = datetime(2024, 1, 15, 12, 0, 0, tzinfo=dt_timezone.utc)
    rows = (
        dict(
            pk=9001,
            object_id='1001',
            object_repr='Acme Corporation deal',
            action_flag=admin.models.ADDITION,
            change_message='',
        ),
        dict(
            pk=9002,
            object_id='1002',
            object_repr='Contact record',
            action_flag=admin.models.CHANGE,
            change_message='[{"changed": {"fields": ["Email", "Name"]}}]',
        ),
        dict(
            pk=9003,
            object_id='1003',
            object_repr='Legacy contact row',
            action_flag=admin.models.CHANGE,
            change_message='Updated the phone number manually',
        ),
        dict(
            pk=9004,
            object_id='1004',
            object_repr='Removed item snapshot',
            action_flag=admin.models.DELETION,
            change_message='',
        ),
        dict(
            pk=9005,
            object_id='1005',
            object_repr='Société café résumé',
            action_flag=admin.models.CHANGE,
            change_message='naïve legacy note about café',
        ),
        dict(
            pk=9006,
            object_id='1006',
            object_repr='wildcard_test row',
            action_flag=admin.models.CHANGE,
            change_message='Progress is 100% complete',
        ),
        dict(
            pk=9007,
            object_id='1007',
            object_repr='underscore_name row',
            action_flag=admin.models.CHANGE,
            change_message='field_name updated',
        ),
        dict(
            pk=9008,
            object_id='1008',
            object_repr='North Region Office',
            action_flag=admin.models.CHANGE,
            change_message='Assigned North Region Office territory',
        ),
        dict(
            pk=9009,
            object_id='9009',
            object_repr='Identifier branch row',
            action_flag=admin.models.CHANGE,
            change_message='[{"changed": {"fields": ["Status"]}}]',
        ),
        dict(
            pk=9010,
            object_id='1010',
            object_repr='No-match decoy',
            action_flag=admin.models.CHANGE,
            change_message='Unrelated audit note',
        ),
        dict(
            pk=9011,
            object_id='1011',
            object_repr='Billing profile',
            action_flag=admin.models.CHANGE,
            change_message='[{"changed": {"fields": ["billing address"]}}]',
        ),
        dict(
            pk=9012,
            object_id='1012',
            object_repr='Accent corpus row',
            action_flag=admin.models.CHANGE,
            change_message='Adjusted naïve café résumé wording',
        ),
    )
    created = []
    for row in rows:
        entry, _ = admin.models.LogEntry.objects.update_or_create(
            pk=row['pk'],
            defaults={
                'user': user,
                'content_type': content_type,
                'object_id': row['object_id'],
                'object_repr': row['object_repr'],
                'action_flag': row['action_flag'],
                'change_message': row['change_message'],
                'action_time': action_time,
            },
        )
        created.append(entry)
    return created
