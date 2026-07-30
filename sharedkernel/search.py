"""Portable audit-log search parsing and queryset filtering.

Case sensitivity follows the backing database collation for ``icontains``
lookups. SQLite may treat ASCII comparisons case-insensitively; PostgreSQL
and MySQL behaviour depends on column collation. The parity harness from
WO-021 captures the legacy in-Python ``str.find`` semantics that WO-024
replaces once this service is wired into ``LogEntryAdmin``.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from enum import Enum

from django.db.models import Q
from django.db.models.query import QuerySet

logger = logging.getLogger(__name__)

ID_PREFIX_PATTERN = re.compile(r'^[iI][dD]\s*\d+$')


class SearchSpecKind(str, Enum):
    EMPTY = 'empty'
    ID_LOOKUP = 'id_lookup'
    FREE_TEXT = 'free_text'


@dataclass(frozen=True, slots=True)
class SearchSpec:
    kind: SearchSpecKind
    normalized_term: str = ''
    id_suffix: str | None = None
    tokens: tuple[str, ...] = ()


class SearchTermParser:
    """Parse admin changelist ``q`` values into structured search specs."""

    @staticmethod
    def parse(raw_term: str) -> SearchSpec:
        normalized = ' '.join(raw_term.splitlines()).strip()
        if not normalized:
            return SearchSpec(kind=SearchSpecKind.EMPTY)

        if ID_PREFIX_PATTERN.match(normalized):
            return SearchSpec(
                kind=SearchSpecKind.ID_LOOKUP,
                normalized_term=normalized,
                id_suffix=normalized[2:],
            )

        tokens = tuple(normalized.split())
        return SearchSpec(
            kind=SearchSpecKind.FREE_TEXT,
            normalized_term=normalized,
            tokens=tokens,
        )


class AuditSearchService:
    """Build portable ORM filters for audit-log search terms."""

    @staticmethod
    def search(queryset: QuerySet, raw_term: str) -> tuple[QuerySet, bool]:
        spec = SearchTermParser.parse(raw_term)
        logger.debug(
            'audit_search kind=%s token_count=%s',
            spec.kind.value,
            len(spec.tokens),
        )

        if spec.kind is SearchSpecKind.EMPTY:
            return queryset, False

        if spec.kind is SearchSpecKind.ID_LOOKUP:
            assert spec.id_suffix is not None
            model = queryset.model
            return (
                model.objects.filter(
                    Q(object_id=spec.id_suffix) | Q(pk=spec.id_suffix),
                ),
                True,
            )

        return AuditSearchService._filter_free_text(queryset, spec.normalized_term)

    @staticmethod
    def _filter_free_text(
        queryset: QuerySet,
        normalized_term: str,
    ) -> tuple[QuerySet, bool]:
        return queryset.filter(change_message__contains=normalized_term), True
