"""Admin URL helpers without project-app dependencies."""

from django.contrib.admin.utils import quote
from django.urls import NoReverseMatch
from django.urls import reverse


def resolve_log_entry_admin_url(log_entry, url_name: str = 'admin:%s_%s_change'):
    """Return the admin change URL for a log entry, or None when unavailable."""
    if log_entry.content_type and log_entry.object_id:
        reverse_name = url_name % (
            log_entry.content_type.app_label,
            log_entry.content_type.model,
        )
        try:
            return reverse(reverse_name, args=(quote(log_entry.object_id),))
        except NoReverseMatch:
            pass
    return None
