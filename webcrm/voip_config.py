"""VoIP provider settings resolved through ConfigAccessor."""

from __future__ import annotations

from typing import Any

from django.core.exceptions import ImproperlyConfigured

from webcrm.config import ENV_REMEDIATION, config

_ZADARMA_BACKEND = 'voip.backends.zadarmabackend.ZadarmaAPI'


def build_voip_settings() -> dict[str, Any]:
    """Return VoIP backend configuration and forwarding settings."""
    config.register_secret('ZADARMA_SECRET')

    key = config.get('ZADARMA_KEY', default='')
    secret = config.get('ZADARMA_SECRET', default='', secret=True)
    if bool(key.strip()) ^ bool(secret.strip()):
        missing = 'ZADARMA_SECRET' if key.strip() else 'ZADARMA_KEY'
        raise ImproperlyConfigured(
            f"Incomplete VoIP configuration: '{missing}' must be set when its "
            f"companion credential is supplied. {ENV_REMEDIATION}"
        )
    allowlist = config.get_list(
        'ZADARMA_PROVIDER_ALLOWLIST',
        default='185.45.152.42',
    )

    voip: list[dict[str, Any]] = []
    if key.strip() and secret.strip():
        voip.append(
            {
                'BACKEND': _ZADARMA_BACKEND,
                'PROVIDER': 'Zadarma',
                'ALLOWLIST': allowlist,
                'OPTIONS': {
                    'key': key,
                    'secret': secret,
                },
            }
        )

    return {
        'VOIP': voip,
        'VOIP_FORWARD_DATA': config.get_bool('VOIP_FORWARD_DATA', default=False),
        'VOIP_FORWARDING_IP': config.get('VOIP_FORWARDING_IP', default=''),
        'VOIP_FORWARD_URL': config.get('VOIP_FORWARD_URL', default=''),
        'ZADARMA_PROVIDER_ALLOWLIST': allowlist,
    }
