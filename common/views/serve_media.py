"""Staff-gated media file serving for non-debug container runtimes."""

from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.http import Http404
from django.http import HttpResponseForbidden
from django.views.static import serve


def serve_protected_media(request, path: str):
    """Serve a file from MEDIA_ROOT to authenticated staff users only."""
    if not settings.SERVE_MEDIA_FILES:
        raise Http404('Media serving is disabled.')

    if not request.user.is_authenticated:
        return redirect_to_login(request.get_full_path(), login_url=settings.LOGIN_URL)
    if not request.user.is_staff:
        return HttpResponseForbidden()

    media_root = Path(settings.MEDIA_ROOT).resolve()
    if '..' in Path(path).parts:
        raise Http404('Media file not found.')

    try:
        full_path = (media_root / path).resolve()
    except (OSError, ValueError) as exc:
        raise Http404('Media file not found.') from exc

    if full_path != media_root and media_root not in full_path.parents:
        raise Http404('Media file not found.')
    if not full_path.is_file():
        raise Http404('Media file not found.')

    return serve(request, path, document_root=settings.MEDIA_ROOT)
