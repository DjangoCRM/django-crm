"""Token generation helpers referenced by historical migrations."""

from __future__ import annotations

import secrets


def token_default():
    return secrets.token_urlsafe(8)
