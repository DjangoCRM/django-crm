from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import JsonResponse, HttpRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from voip.models import OnlinePBXSettings
from voip.backends.onlinepbxbackend import OnlinePBXAPI


def build_client() -> OnlinePBXAPI:
    cfg = OnlinePBXSettings.get_solo()
    return OnlinePBXAPI(
        domain=cfg.domain,
        key_id=cfg.key_id or None,
        key=cfg.key or None,
        api_key=cfg.api_key or None,
        base_url=cfg.base_url,
        use_base64_md5=cfg.use_md5_base64,
    )


class OnlinePBXAuthView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest):
        client = build_client()
        data = client.auth()
        # persist keys if returned
        cfg = OnlinePBXSettings.get_solo()
        creds = data.get('data') or {}
        changed = False
        if isinstance(creds, dict):
            key_id = creds.get('key_id')
            key = creds.get('key')
            if key_id and key_id != cfg.key_id:
                cfg.key_id = key_id
                changed = True
            if key and key != cfg.key:
                cfg.key = key
                changed = True
        if changed:
            cfg.save(update_fields=['key_id', 'key', 'updated_at'])
        return JsonResponse(data)


class OnlinePBXCallView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest):
        to = request.POST.get('to')
        from_num = request.POST.get('from')
        if not to or not from_num:
            return JsonResponse({'status': 'error', 'message': 'from and to are required'}, status=400)
        client = build_client()
        data = client.call_now(from_num, to)
        return JsonResponse(data)
