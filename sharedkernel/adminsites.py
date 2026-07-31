"""Neutral admin-site registry for cross-app admin wiring without import cycles."""

from __future__ import annotations

from django.contrib.admin import AdminSite
from django.core.exceptions import ImproperlyConfigured

CRM_SITE_NAME = 'crm'

_registry: dict[str, AdminSite] = {}


def register_admin_site(name: str, site: AdminSite) -> None:
    """Register a named admin site instance."""
    if name in _registry:
        raise ImproperlyConfigured(
            f"Admin site {name!r} is already registered.",
        )
    _registry[name] = site


def get_admin_site(name: str) -> AdminSite:
    """Return a registered admin site by name."""
    try:
        return _registry[name]
    except KeyError as exc:
        raise ImproperlyConfigured(
            f"Unknown admin site {name!r}. Register it with register_admin_site() "
            f'before requesting it. Known sites: {sorted(_registry)}',
        ) from exc


def registered_admin_site_names() -> tuple[str, ...]:
    return tuple(sorted(_registry))
