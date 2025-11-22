from __future__ import annotations

import hashlib
import hmac
import json
from typing import Optional

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone

from .models import ChannelAccount, ExternalMessage
from chat.models import ChatMessage
from django.contrib.contenttypes.models import ContentType
from crm.models import Lead


def _find_telegram_account_by_secret(secret: str) -> Optional[ChannelAccount]:
    try:
        return ChannelAccount.objects.get(type='telegram', telegram_webhook_secret=secret, is_active=True)
    except ChannelAccount.DoesNotExist:
        return None


def _find_instagram_account() -> Optional[ChannelAccount]:
    return ChannelAccount.objects.filter(type='instagram', is_active=True).first()


@method_decorator(csrf_exempt, name='dispatch')
class TelegramWebhookView(View):
    def post(self, request: HttpRequest, secret: str) -> HttpResponse:
        account = _find_telegram_account_by_secret(secret)
        if not account:
            return HttpResponse('Forbidden', status=403)
        try:
            update = json.loads(request.body.decode('utf-8') or '{}')
        except Exception:
            update = {}
        message = update.get('message') or update.get('edited_message')
        if not message:
            return JsonResponse({'status': 'ok'})
        chat = message.get('chat', {})
        sender = message.get('from', {})
        text = message.get('text') or ''
        ext_id = str(message.get('message_id') or update.get('update_id'))
        sender_id = str(sender.get('id') or '')
        recipient_id = str(chat.get('id') or '')

        em = ExternalMessage.objects.create(
            channel=account,
            direction='in',
            external_id=ext_id,
            sender_id=sender_id,
            recipient_id=recipient_id,
            text=text,
            raw=update,
            created_at=timezone.now(),
        )
        # Auto-create lead on first message if not exists (simple heuristic by tg id)
        lead = Lead.objects.filter(source='telegram', others__icontains=sender_id).first()
        if not lead:
            lead = Lead.objects.create(
                name=f"tg:{sender.get('username') or sender_id}",
                source='telegram',
                others=sender_id,
            )
        # Create ChatMessage bound to Lead
        ct = ContentType.objects.get_for_model(Lead)
        ChatMessage.objects.create(
            content_type=ct,
            object_id=lead.id,
            content=text,
        )
        return JsonResponse({'status': 'ok'})


@method_decorator(csrf_exempt, name='dispatch')
class InstagramWebhookView(View):
    # Verification
    def get(self, request: HttpRequest) -> HttpResponse:
        account = _find_instagram_account()
        if not account:
            return HttpResponse('No account', status=503)
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge', '')
        if mode == 'subscribe' and token == account.ig_verify_token:
            return HttpResponse(challenge)
        return HttpResponse('Forbidden', status=403)

    def post(self, request: HttpRequest) -> HttpResponse:
        account = _find_instagram_account()
        if not account:
            return HttpResponse('No account', status=503)
        # Optional signature verification
        sig = request.headers.get('X-Hub-Signature-256')
        if account.ig_app_secret and sig:
            try:
                sha_name, signature = sig.split('=')
                mac = hmac.new(account.ig_app_secret.encode('utf-8'), msg=request.body, digestmod=hashlib.sha256)
                if not hmac.compare_digest(mac.hexdigest(), signature):
                    return HttpResponse('Forbidden', status=403)
            except Exception:
                return HttpResponse('Forbidden', status=403)
        try:
            payload = json.loads(request.body.decode('utf-8') or '{}')
        except Exception:
            payload = {}
        # Log entries as ExternalMessage (simplified; real mapping requires deeper parsing of Graph API payload)
        ext_id = str(payload.get('object') or timezone.now().timestamp())
        ExternalMessage.objects.create(
            channel=account,
            direction='in',
            external_id=ext_id,
            sender_id='',
            recipient_id=account.ig_page_id or '',
            text='',
            raw=payload,
        )
        return JsonResponse({'status': 'ok'})
