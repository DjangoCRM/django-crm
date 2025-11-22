from __future__ import annotations

import json
from typing import Optional

from django.http import HttpRequest, JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
import time

from .models import ChannelAccount, ExternalMessage
from .sms import eskiz_auth, eskiz_send_sms, playmobile_send_sms_basic, playmobile_send_sms_token
from common.utils.notif_email_sender import NotifEmailSender


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

        # retry strategy
        max_retries = getattr(settings, 'SMS_SEND_MAX_RETRIES', 2)
        backoff_sec = getattr(settings, 'SMS_SEND_BACKOFF_SEC', 2)

        def send_once():
            if acc.type == 'eskiz':
                token = acc.eskiz_token or eskiz_auth(acc.eskiz_email, acc.eskiz_password)
                if token:
                    return eskiz_send_sms(token, acc.eskiz_from, to, text), 'sent' if ok else 'failed'
                return False, 'auth failed'
            elif acc.type == 'playmobile':
                if acc.playmobile_auth_type == 'token' and acc.playmobile_token:
                    return playmobile_send_sms_token(acc.playmobile_api_url, acc.playmobile_token, acc.playmobile_from, to, text), ''
                return playmobile_send_sms_basic(acc.playmobile_api_url, acc.playmobile_login, acc.playmobile_password, acc.playmobile_from, to, text), ''
            return False, 'unsupported'

        attempt = 0
        while attempt <= max_retries and not ok:
            ok, detail = send_once()
            if ok:
                break
            time.sleep(backoff_sec * (attempt + 1))
            attempt += 1
        # Log ExternalMessage
        try:
            ExternalMessage.objects.create(
                channel=acc,
                direction='out',
                external_id='',
                sender_id=acc.playmobile_from if acc.type == 'playmobile' else acc.eskiz_from,
                recipient_id=to,
                text=text,
                raw={'attempts': attempt, 'provider': acc.type},
                status='SENT' if ok else 'FAILED'
            )
        except Exception:
            pass

        # Notify admins on failure
        if not ok:
            try:
                to_admins = getattr(settings, 'SMS_ALERT_EMAILS', [])
                if to_admins:
                    sender = NotifEmailSender()
                    sender.send_msg(
                        subject='SMS send failed',
                        body=f'Channel: {acc}\nTo: {to}\nText: {text[:200]}\nDetail: {detail}',
                        to=to_admins
                    )
                    sender.start()
            except Exception:
                pass

        return JsonResponse({'status': 'ok' if ok else 'error', 'detail': detail, 'attempts': attempt})
