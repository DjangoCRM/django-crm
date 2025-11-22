from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import ChannelAccount, ExternalMessage


@admin.register(ChannelAccount)
class ChannelAccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'name', 'is_active')
    list_filter = ('type', 'is_active')
    search_fields = ('name', 'telegram_webhook_secret', 'ig_page_id')
    fieldsets = (
        (_('Base'), {'fields': ('type', 'name', 'is_active')}),
        (_('Telegram'), {'fields': ('telegram_bot_token', 'telegram_webhook_secret')}),
        (_('Instagram'), {'fields': ('ig_app_id', 'ig_app_secret', 'ig_page_id', 'ig_page_access_token', 'ig_verify_token')}),
    )


@admin.register(ExternalMessage)
class ExternalMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'channel', 'direction', 'external_id', 'sender_id', 'recipient_id', 'created_at')
    list_filter = ('channel__type', 'direction')
    search_fields = ('external_id', 'sender_id', 'recipient_id', 'text')
