from __future__ import annotations

import json
from typing import Optional

from django.http import HttpRequest, JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import ChannelAccount
from .sms import eskiz_auth, eskiz_send_sms, playmobile_send_sms


@method_decorator(csrf_exempt, name='dispatch')
class SendSMSView(View):
    """Unified endpoint to send SMS via Eskiz or PlayMobile.
    POST JSON: {"channel_id": 1, "to": "+998901234567", "text": "Hello"}
    """

    def post(self, request: HttpRequest):
        try:
            payload = json.loads(request.body.decode('utf-8') or '{}')
        except Exception:
            payload = {}
        channel_id = payload.get('channel_id')
        to = (payload.get('to') or '').strip()
        text = (payload.get('text') or '').strip()
        if not (channel_id and to and text):
            return JsonResponse({'status': 'error', 'detail': 'Missing fields'}, status=400)
        acc: Optional[ChannelAccount] = ChannelAccount.objects.filter(id=channel_id, is_active=True).first()
        if not acc:
            return JsonResponse({'status': 'error', 'detail': 'Channel not found'}, status=404)

        ok = False
        detail = ''
        if acc.type == 'eskiz':
            token = acc.eskiz_token or eskiz_auth(acc.eskiz_email, acc.eskiz_password)
            if token:
                ok = eskiz_send_sms(token, acc.eskiz_from, to, text)
                detail = 'sent' if ok else 'failed'
            else:
                detail = 'auth failed'
        elif acc.type == 'playmobile':
            ok = playmobile_send_sms(acc.playmobile_login, acc.playmobile_password, acc.playmobile_from, to, text)
            detail = 'sent' if ok else 'failed'
        else:
            return JsonResponse({'status': 'error', 'detail': 'Unsupported channel type'}, status=400)

        return JsonResponse({'status': 'ok' if ok else 'error', 'detail': detail})
