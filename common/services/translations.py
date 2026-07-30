"""Per-user and per-language translation helpers."""

from __future__ import annotations

from django.conf import settings
from django.utils.translation import gettext
from django.utils.translation import override


def get_trans_for_lang(text: str, language_code: str) -> str:
    """Get translation for a specific language."""
    with override(language_code):
        return gettext(text)


def get_user_language_code(user) -> str:
    if settings.USE_I18N:
        return user.profile.language_code or settings.LANGUAGE_CODE
    return settings.LANGUAGE_CODE


def get_trans_for_user(text: str, user) -> str:
    """Translate text into the user's language."""
    return get_trans_for_lang(text, get_user_language_code(user))
