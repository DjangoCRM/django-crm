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
        use_async = payload.get('async', True)
        if not (channel_id and to and text):
            return JsonResponse({'status': 'error', 'detail': 'Missing fields'}, status=400)
        acc: Optional[ChannelAccount] = ChannelAccount.objects.filter(id=channel_id, is_active=True).first()
        if not acc:
            return JsonResponse({'status': 'error', 'detail': 'Channel not found'}, status=404)

        ok = False
        detail = ''

        if use_async and not settings.CELERY_TASK_ALWAYS_EAGER:
            # enqueue background task
            res = send_sms_task.delay(channel_id, to, text)
            return JsonResponse({'status': 'accepted', 'task_id': res.id}, status=202)

        # retry strategy
        max_retries = getattr(settings, 'SMS_SEND_MAX_RETRIES', 2)
        backoff_sec = getattr(settings, 'SMS_SEND_BACKOFF_SEC', 2)

        def send_once():
            provider_id = None
            raw = None
            if acc.type == 'eskiz':
                token = acc.eskiz_token or eskiz_auth(acc.eskiz_email, acc.eskiz_password)
                if token:
                    ok, provider_id, raw = eskiz_send_sms(token, acc.eskiz_from, to, text)
                    return ok, ('sent' if ok else 'failed'), provider_id, raw
                return False, 'auth failed', None, None
            elif acc.type == 'playmobile':
                if acc.playmobile_auth_type == 'token' and acc.playmobile_token:
                    ok, provider_id, raw = playmobile_send_sms_token(acc.playmobile_api_url, acc.playmobile_token, acc.playmobile_from, to, text)
                else:
                    ok, provider_id, raw = playmobile_send_sms_basic(acc.playmobile_api_url, acc.playmobile_login, acc.playmobile_password, acc.playmobile_from, to, text)
                return ok, ('sent' if ok else 'failed'), provider_id, raw
            return False, 'unsupported', None, None

        attempt = 0
        provider_id = None
        raw = None
        while attempt <= max_retries and not ok:
            ok, detail, provider_id, raw = send_once()
            if ok:
                break
            time.sleep(backoff_sec * (attempt + 1))
            attempt += 1
        # Log ExternalMessage
        try:
            ExternalMessage.objects.create(
                channel=acc,
                direction='out',
                external_id=provider_id or '',
                sender_id=acc.playmobile_from if acc.type == 'playmobile' else acc.eskiz_from,
                recipient_id=to,
                text=text,
                raw=(raw or {}) | {'attempts': attempt, 'provider': acc.type},
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
