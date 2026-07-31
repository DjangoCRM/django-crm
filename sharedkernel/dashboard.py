"""Dashboard counter and help-url provider registry."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable

from django.utils.safestring import mark_safe

logger = logging.getLogger(__name__)

CounterProvider = Callable[[object, list], None]
HelpUrlProvider = Callable[[object], str]

_registry: list[CounterRegistration] = []
_help_url_provider: HelpUrlProvider | None = None


@dataclass(frozen=True, slots=True)
class CounterRegistration:
    name: str
    order: int
    app_label: str
    provider: CounterProvider


def register_counter(
    name: str,
    order: int,
    app_label: str,
    provider: CounterProvider,
) -> None:
    for existing in _registry:
        if existing.name == name:
            raise ValueError(f'Dashboard counter {name!r} is already registered.')
    _registry.append(
        CounterRegistration(name=name, order=order, app_label=app_label, provider=provider),
    )


def register_help_url_provider(provider: HelpUrlProvider) -> None:
    global _help_url_provider
    if _help_url_provider is not None and _help_url_provider is not provider:
        raise ValueError('A help URL provider is already registered.')
    _help_url_provider = provider


def iter_counter_registrations() -> tuple[CounterRegistration, ...]:
    return tuple(sorted(_registry, key=lambda entry: (entry.order, entry.name)))


def apply_dashboard_counters(request, app_label: str, models: list) -> None:
    for entry in iter_counter_registrations():
        if entry.app_label != app_label:
            continue
        try:
            entry.provider(request, models)
        except Exception:
            logger.exception(
                'Dashboard counter %s failed for app %s',
                entry.name,
                app_label,
            )


def resolve_help_url(request) -> str:
    if _help_url_provider is None:
        return ''
    try:
        return _help_url_provider(request) or ''
    except Exception:
        logger.exception('Help URL provider failed')
        return ''


def set_counters(model, models, counts) -> None:
    model_name = model._meta.verbose_name_plural.capitalize()    # NOQA
    model_entry = next((m for m in models if m['name'] == model_name), None)
    if model_entry is None:
        return
    if counts['urgent'] and counts['regular']:
        model_entry['name'] = mark_safe(
            f"{model_name} "
            f"(<span style='color: var(--error-fg)'>{counts['urgent']}</span>"
            f" + {counts['regular']})"
        )
    elif counts['regular']:
        model_entry['name'] = mark_safe(
            f"{model_name} ({counts['regular']})"
        )
    elif counts['urgent']:
        model_entry['name'] = mark_safe(
            f"{model_name} "
            f"(<span style='color: var(--error-fg)'>{counts['urgent']}</span>)"
        )


def _reset_registry_for_tests() -> None:
    global _help_url_provider
    _registry.clear()
    _help_url_provider = None
