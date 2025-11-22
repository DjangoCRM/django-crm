from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class ChannelAccount(models.Model):
    TYPE_CHOICES = (
        ('telegram', 'Telegram'),
        ('instagram', 'Instagram'),
        ('eskiz', 'Eskiz SMS'),
        ('playmobile', 'PlayMobile'),
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, db_index=True)
    name = models.CharField(max_length=150, default='', blank=True)
    is_active = models.BooleanField(default=True)

    # Telegram
    telegram_bot_token = models.CharField(max_length=255, default='', blank=True)
    telegram_webhook_secret = models.CharField(max_length=255, default='', blank=True)

    # Instagram / Meta
    ig_app_id = models.CharField(max_length=255, default='', blank=True)
    ig_app_secret = models.CharField(max_length=255, default='', blank=True)
    ig_page_id = models.CharField(max_length=255, default='', blank=True)
    ig_page_access_token = models.CharField(max_length=500, default='', blank=True)
    ig_verify_token = models.CharField(max_length=255, default='', blank=True)

    # Eskiz SMS
    eskiz_email = models.CharField(max_length=255, default='', blank=True)
    eskiz_password = models.CharField(max_length=255, default='', blank=True)
    eskiz_token = models.CharField(max_length=500, default='', blank=True)
    eskiz_from = models.CharField(max_length=20, default='', blank=True)

    # PlayMobile
    playmobile_login = models.CharField(max_length=255, default='', blank=True)
    playmobile_password = models.CharField(max_length=255, default='', blank=True)
    playmobile_from = models.CharField(max_length=20, default='', blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Channel account')
        verbose_name_plural = _('Channel accounts')

    def __str__(self):
        return f'{self.get_type_display()} {self.name or ""}'.strip()


class ExternalMessage(models.Model):
    DIRECTION = (
        ('in', 'Inbound'),
        ('out', 'Outbound'),
    )
    channel = models.ForeignKey(ChannelAccount, on_delete=models.CASCADE, related_name='messages')
    direction = models.CharField(max_length=3, choices=DIRECTION)
    external_id = models.CharField(max_length=255, db_index=True)
    sender_id = models.CharField(max_length=255, default='', blank=True)
    recipient_id = models.CharField(max_length=255, default='', blank=True)
    text = models.TextField(default='', blank=True)
    raw = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=50, default='', blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _('External message')
        verbose_name_plural = _('External messages')
        indexes = [
            models.Index(fields=['channel', 'external_id']),
        ]

    def __str__(self):
        return f'{self.channel}:{self.direction}:{self.external_id}'
