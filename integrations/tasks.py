from __future__ import annotations

import time
from celery import shared_task
from django.conf import settings

from .models import ChannelAccount, ExternalMessage
from .sms import (
    eskiz_auth, eskiz_send_sms,
    playmobile_send_sms_basic, playmobile_send_sms_token,
)
from common.utils.notif_email_sender import NotifEmailSender


@shared_task(bind=True, max_retries=5)
def send_sms_task(self, channel_id: int, to: str, text: str) -> dict:
    acc = ChannelAccount.objects.filter(id=channel_id, is_active=True).first()
    if not acc:
        return {'ok': False, 'detail': 'Channel not found'}

    max_retries = getattr(settings, 'SMS_SEND_MAX_RETRIES', 2)
    backoff_sec = getattr(settings, 'SMS_SEND_BACKOFF_SEC', 2)

    attempt = 0
    ok = False
    detail = ''
    provider_id = None
    raw = None

    def send_once():
        nonlocal provider_id, raw
        if acc.type == 'eskiz':
            token = acc.eskiz_token or eskiz_auth(acc.eskiz_email, acc.eskiz_password)
            if token:
                ok_, provider_id, raw = eskiz_send_sms(token, acc.eskiz_from, to, text)
                return ok_, 'sent' if ok_ else 'failed'
            return False, 'auth failed'
        elif acc.type == 'playmobile':
            if acc.playmobile_auth_type == 'token' and acc.playmobile_token:
                ok_, provider_id, raw = playmobile_send_sms_token(acc.playmobile_api_url, acc.playmobile_token, acc.playmobile_from, to, text)
            else:
                ok_, provider_id, raw = playmobile_send_sms_basic(acc.playmobile_api_url, acc.playmobile_login, acc.playmobile_password, acc.playmobile_from, to, text)
            return ok_, 'sent' if ok_ else 'failed'
        return False, 'unsupported'

    while attempt <= max_retries and not ok:
        ok, detail = send_once()
        if ok:
            break
        # schedule retry via Celery if attempts left
        attempt += 1
        delay = backoff_sec * attempt
        if attempt <= max_retries:
            try:
                raise self.retry(countdown=delay)
            except self.MaxRetriesExceededError:
                break
        time.sleep(delay)

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

    if not ok:
        try:
            to_admins = getattr(settings, 'SMS_ALERT_EMAILS', [])
            if to_admins:
                sender = NotifEmailSender()
                sender.send_msg(
                    subject='SMS send failed (task)',
                    body=f'Channel: {acc}\nTo: {to}\nText: {text[:200]}\nDetail: {detail}',
                    to=to_admins
                )
                sender.start()
        except Exception:
            pass

    return {'ok': ok, 'detail': detail, 'attempts': attempt, 'external_id': provider_id}
