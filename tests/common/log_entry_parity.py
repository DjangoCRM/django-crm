"""Helpers for LogEntryAdmin search parity characterization."""

from __future__ import annotations

from django.contrib import admin

from tests.common.log_entry_parity_seed import PARITY_LOG_ENTRY_PKS

# Documented branches in LogEntryAdmin.get_search_results (common/admin.py):
#
# 1. Falsy search_term
#    Delegates to ModelAdmin.get_search_results (search_fields on change_message).
#
# 2. Non-empty search_term — normalize with splitlines/join/strip into ``st``.
#
# 3. ID-prefix branch — ``re.match(r"^[iI][dD]\s*\d+$", st)``:
#    Returns LogEntry.objects.filter(Q(object_id=st[2:]) | Q(id=st[2:])), True
#    Note: st[2:] drops the first two characters only (does not strip interior space).
#
# 4. Default branch — iterate queryset with .iterator():
#    Collect ids where obj.get_change_message().find(search_term) != -1
#    (case-sensitive substring on rendered change message, not raw JSON/object_repr).
#    Returns queryset.filter(id__in=ids), True


def parity_queryset():
    return admin.models.LogEntry.objects.filter(pk__in=PARITY_LOG_ENTRY_PKS)


def capture_search_pks(model_admin, request, search_term, queryset=None):
    """Return sorted PK list and may_have_duplicates from get_search_results."""
    if queryset is None:
        queryset = parity_queryset()
    results, may_have_duplicates = model_admin.get_search_results(
        request,
        queryset,
        search_term,
    )
    return sorted(results.values_list('pk', flat=True)), may_have_duplicates


def assert_search_parity(test_case, model_admin, request, search_term, expected_pks, expected_distinct):
    pks, may_have_duplicates = capture_search_pks(model_admin, request, search_term)
    test_case.assertEqual(pks, sorted(expected_pks))
    test_case.assertEqual(may_have_duplicates, expected_distinct)
