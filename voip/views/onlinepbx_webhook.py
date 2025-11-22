from __future__ import annotations

import json
from typing import Any, Dict, Iterable, Optional

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from voip.models import IncomingCall
from voip.utils import find_objects_by_phone, resolve_targets, normalize_number


def _get_onlinepbx_backend() -> Optional[dict]:
    for backend in getattr(settings, 'VOIP', []):
        if backend.get('PROVIDER') == 'OnlinePBX':
            return backend
    return None


def _client_ip(request: HttpRequest) -> str:
    # Respect reverse proxy headers if needed; fallback to REMOTE_ADDR
    for hdr in ('HTTP_X_FORWARDED_FOR', 'HTTP_X_REAL_IP'):
        val = request.META.get(hdr)
        if val:
            return val.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def _is_ip_allowed(request: HttpRequest, backend: dict) -> bool:
    allowed_ip = backend.get('IP', '*')
    if allowed_ip == '*':
        return True
    client_ip = _client_ip(request)
    return client_ip == allowed_ip


def _token_ok(request: HttpRequest) -> bool:
    # Optional shared token check; set ONLINEPBX_WEBHOOK_TOKEN env to enable
    token = getattr(settings, 'ONLINEPBX_WEBHOOK_TOKEN', None)
    if not token:
        return True
    recv = request.headers.get('X-OnlinePBX-Token') or request.headers.get('X-Obx-Token')
    return recv == token


def _parse_payload(request: HttpRequest) -> Dict[str, Any]:
    if request.content_type and 'application/json' in request.content_type:
        try:
            return json.loads(request.body.decode('utf-8') or '{}')
        except Exception:
            return {}
    # Fallback to form data
    return {k: v for k, v in request.POST.items()}


def _extract_numbers(payload: Dict[str, Any]) -> tuple[str, str]:
    """Return caller_phone, extension/target from heterogeneous payloads."""
    caller_candidates = [
        payload.get('caller_id_number'),
        payload.get('caller_id'),
        payload.get('from'),
        payload.get('src'),
        payload.get('caller'),
        payload.get('phone'),
    ]
    target_candidates = [
        payload.get('destination_number'),
        payload.get('to'),
        payload.get('dst'),
        payload.get('extension'),
        payload.get('uid'),
        payload.get('called_did'),
    ]
    caller = next((c for c in caller_candidates if c), '')
    target = next((t for t in target_candidates if t), '')
    return str(caller), str(target)


@method_decorator(csrf_exempt, name='dispatch')
class OnlinePBXWebHook(View):
    """Webhook endpoint for OnlinePBX provider.

    Security:
    - IP allow-list via settings.VOIP entry for provider 'OnlinePBX' (IP='*' allows all)
    - Optional shared token header X-OnlinePBX-Token if settings.ONLINEPBX_WEBHOOK_TOKEN is set

    Behavior:
    - Accepts JSON or form-data payloads
    - Extracts caller phone and target extension
    - Maps to CRM objects and users, creates IncomingCall entries for targets
    """

    def post(self, request: HttpRequest) -> HttpResponse:
        backend = _get_onlinepbx_backend()
        if not backend:
            return HttpResponse('OnlinePBX provider is not configured', status=503)

        if not _is_ip_allowed(request, backend):
            return HttpResponse('Forbidden (IP)', status=403)
        if not _token_ok(request):
            return HttpResponse('Forbidden (Token)', status=403)

        payload = _parse_payload(request)
        caller, target_ext = _extract_numbers(payload)
        caller_norm = normalize_number(caller)

        contact = lead = deal = None
        client_name = client_type = ''
        client_id = None
        client_url = ''

        if caller_norm:
            contact, lead, deal, err = find_objects_by_phone(caller_norm)
            if not err and not (contact or lead):
                # Auto-create lead and contact
                from integrations.utils import ensure_lead_and_contact
                lead, contact = ensure_lead_and_contact(
                    source_name='onlinepbx',
                    display_name=payload.get('caller_id_name') or caller_norm,
                    phone=caller_norm,
                )
            obj = contact or lead
            if obj and hasattr(obj, 'full_name'):
                client_name = obj.full_name
                client_type = obj.__class__.__name__.lower()
                client_id = getattr(obj, 'id', None)
                # Could be enhanced with reverse URL later

        targets = resolve_targets(target_ext, contact or lead or deal)
        created = 0
        for user in targets:
            IncomingCall.objects.create(
                user=user,
                caller_id=caller_norm or caller,
                client_name=client_name,
                client_type=client_type,
                client_id=client_id,
                client_url=client_url,
                raw_payload=payload,
            )
            created += 1

        return JsonResponse({
            'status': 'ok',
            'created': created,
            'targets': [u.id for u in targets],
        })
