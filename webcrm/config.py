"""Environment-backed configuration accessor for Django-CRM settings."""

from __future__ import annotations

import logging
import os
import sys
from typing import Any

from django.core.exceptions import ImproperlyConfigured

MISSING = object()
SECRET_MASK = '***'
ENV_REMEDIATION = (
    'Set the variable in your process environment or add it to .env.example.'
)

logger = logging.getLogger(__name__)


class ConfigAccessor:
    """Resolve settings from environment variables, secret files, or defaults."""

    def __init__(self, secrets_dir: str | None = None) -> None:
        self._secrets_dir_override = secrets_dir
        self._secret_names: set[str] = set()
        self._access_registry: dict[str, str] = {}
        self._source_registry: dict[str, str] = {}
        self._mandatory_names: set[str] = set()

    def register_secret(self, name: str) -> None:
        self._secret_names.add(name)

    def _secrets_directory(self) -> str:
        if self._secrets_dir_override is not None:
            return self._secrets_dir_override
        return os.environ.get('DJANGO_SECRETS_DIR', '/run/secrets')

    def _is_secret(self, name: str, secret: bool) -> bool:
        if secret:
            self._secret_names.add(name)
        return name in self._secret_names

    def _record_access(
        self,
        name: str,
        value: str,
        *,
        secret: bool,
        source: str,
    ) -> None:
        stored = SECRET_MASK if self._is_secret(name, secret) else value
        self._access_registry[name] = stored
        self._source_registry[name] = source
        logger.debug('Resolved configuration key %s=%s (%s)', name, stored, source)

    def _resolve_raw(self, name: str, default: Any = MISSING) -> tuple[str | None, str]:
        if name in os.environ:
            return os.environ[name], 'environment'

        secret_path = os.path.join(self._secrets_directory(), name.lower())
        if os.path.isfile(secret_path):
            try:
                with open(secret_path, encoding='utf-8') as handle:
                    secret_value = handle.read().strip()
            except OSError as exc:
                raise ImproperlyConfigured(
                    f"Could not read secret file for '{name}' at {secret_path}: {exc}. "
                    f"{ENV_REMEDIATION}"
                ) from exc
            if secret_value:
                return secret_value, 'secret_file'

        if default is not MISSING:
            if default is None:
                return None, 'default'
            return str(default), 'default'

        return None, 'missing'

    def _missing_message(self, name: str) -> str:
        return (
            f"Required configuration variable '{name}' is not set. "
            f"{ENV_REMEDIATION}"
        )

    def get(
        self,
        name: str,
        default: Any = MISSING,
        *,
        secret: bool = False,
    ) -> str:
        if default is MISSING:
            self._mandatory_names.add(name)
        raw, source = self._resolve_raw(name, default)
        if raw is None:
            raise ImproperlyConfigured(self._missing_message(name))

        self._record_access(name, raw, secret=secret, source=source)
        return raw

    def require(self, name: str, *, secret: bool = False) -> str:
        self._mandatory_names.add(name)
        raw, source = self._resolve_raw(name)
        if raw is None:
            raise ImproperlyConfigured(self._missing_message(name))

        self._record_access(name, raw, secret=secret, source=source)
        return raw

    def get_bool(
        self,
        name: str,
        default: Any = MISSING,
        *,
        secret: bool = False,
    ) -> bool:
        if default is MISSING:
            self._mandatory_names.add(name)
        raw, source = self._resolve_raw(name, default)
        if raw is None:
            raise ImproperlyConfigured(self._missing_message(name))

        normalized = raw.strip().lower()
        value = normalized in {'true', '1', 'yes', 'on'}
        self._record_access(name, raw, secret=secret, source=source)
        return value

    def get_int(
        self,
        name: str,
        default: Any = MISSING,
        *,
        secret: bool = False,
    ) -> int:
        if default is MISSING:
            self._mandatory_names.add(name)
        raw, source = self._resolve_raw(name, default)
        if raw is None:
            raise ImproperlyConfigured(self._missing_message(name))

        try:
            value = int(raw.strip())
        except ValueError as exc:
            raise ImproperlyConfigured(
                f"Configuration variable '{name}' must be an integer; "
                f"received {raw!r}. {ENV_REMEDIATION}"
            ) from exc

        self._record_access(name, raw, secret=secret, source=source)
        return value

    def get_list(
        self,
        name: str,
        default: Any = MISSING,
        *,
        secret: bool = False,
    ) -> list[str]:
        if default is MISSING:
            self._mandatory_names.add(name)
        raw, source = self._resolve_raw(name, default)
        if raw is None:
            raise ImproperlyConfigured(self._missing_message(name))

        if not raw.strip():
            values: list[str] = []
        else:
            values = [part.strip() for part in raw.split(',')]
            values = [part for part in values if part]

        self._record_access(name, raw, secret=secret, source=source)
        return values

    def is_testing(self) -> bool:
        return sys.argv[1:2] == ['test']

    def diagnostics(self) -> dict[str, str]:
        return dict(self._access_registry)

    def source_diagnostics(self) -> dict[str, str]:
        return dict(self._source_registry)

    def mandatory_names(self) -> frozenset[str]:
        return frozenset(self._mandatory_names)

    def unresolved_mandatory(self) -> list[str]:
        return sorted(
            name for name in self._mandatory_names
            if name not in self._access_registry
        )

    def __repr__(self) -> str:
        return f'ConfigAccessor({self.diagnostics()})'


config = ConfigAccessor()
