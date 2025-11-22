from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.urls import reverse

from .models import ChannelAccount, ExternalMessage


@admin.register(ChannelAccount)
class ChannelAccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'name', 'is_active')
    list_filter = ('type', 'is_active')
    search_fields = ('name', 'telegram_webhook_secret', 'ig_page_id')
    actions = ('test_webhook',)
    readonly_fields = (
        'telegram_webhook_url',
        'instagram_webhook_url',
        'instagram_verify_example',
    )
    fieldsets = (
        (_('Base'), {
            'fields': (
                'type', 'name', 'is_active',
                'telegram_webhook_url', 'instagram_webhook_url', 'instagram_verify_example',
            )
        }),
        (_('Telegram'), {'fields': ('telegram_bot_token', 'telegram_webhook_secret')}),
        (_('Instagram'), {'fields': (
            'ig_app_id', 'ig_app_secret', 'ig_page_id', 'ig_page_access_token', 'ig_verify_token'
        )}),
        (_('Eskiz SMS'), {'fields': (
            'eskiz_email', 'eskiz_password', 'eskiz_token', 'eskiz_from'
        )}),
        (_('PlayMobile'), {'fields': (
            'playmobile_auth_type', 'playmobile_api_url', 'playmobile_status_url', 'playmobile_token',
            'playmobile_login', 'playmobile_password', 'playmobile_from'
        )}),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Help texts
        ht = form.base_fields
        if 'telegram_bot_token' in ht:
            ht['telegram_bot_token'].help_text = _('Bot token from @BotFather (keep secret).')
        if 'telegram_webhook_secret' in ht:
            ht['telegram_webhook_secret'].help_text = _('Secret path component used to protect the webhook endpoint.')
        if 'ig_app_id' in ht:
            ht['ig_app_id'].help_text = _('Meta app id from Developer portal.')
        if 'ig_app_secret' in ht:
            ht['ig_app_secret'].help_text = _('Meta app secret (keep secret).')
        if 'ig_page_id' in ht:
            ht['ig_page_id'].help_text = _('Facebook Page ID connected to Instagram Business account.')
        if 'ig_page_access_token' in ht:
            ht['ig_page_access_token'].help_text = _('Long-lived Page access token (keep secret).')
        if 'ig_verify_token' in ht:
            ht['ig_verify_token'].help_text = _('Arbitrary token you set and provide to Meta during webhook verification.')
        if 'name' in ht:
            ht['name'].help_text = _('Friendly name to distinguish multiple accounts.')
        if 'type' in ht:
            ht['type'].help_text = _('Select the integration channel type.')
        # Eskiz/PlayMobile
        if 'eskiz_email' in ht:
            ht['eskiz_email'].help_text = _('Eskiz account email.')
        if 'eskiz_password' in ht:
            ht['eskiz_password'].help_text = _('Eskiz account password. Not stored if token is set.')
        if 'eskiz_token' in ht:
            ht['eskiz_token'].help_text = _('Eskiz API token (optional if email/password provided).')
        if 'eskiz_from' in ht:
            ht['eskiz_from'].help_text = _('Sender name (from).')
        if 'playmobile_auth_type' in ht:
            ht['playmobile_auth_type'].help_text = _('Select auth type: Login/Password or Bearer Token.')
        if 'playmobile_api_url' in ht:
            ht['playmobile_api_url'].help_text = _('PlayMobile send API URL (from HTTP.pdf).')
        if 'playmobile_status_url' in ht:
            ht['playmobile_status_url'].help_text = _('PlayMobile status API URL (optional).')
        if 'playmobile_token' in ht:
            ht['playmobile_token'].help_text = _('PlayMobile Bearer token (if token auth).')
        if 'playmobile_login' in ht:
            ht['playmobile_login'].help_text = _('PlayMobile API login (if basic auth).')
        if 'playmobile_password' in ht:
            ht['playmobile_password'].help_text = _('PlayMobile API password (if basic auth).')
        if 'playmobile_from' in ht:
            ht['playmobile_from'].help_text = _('Sender name (from).')
        return form

    def telegram_webhook_url(self, obj):
        if not obj or obj.type != 'telegram' or not obj.telegram_webhook_secret:
            return '-'
        path = reverse('telegram-webhook', args=[obj.telegram_webhook_secret])
        btn = f"<button type='button' class='button' data-copy='{path}' onclick=\"navigator.clipboard.writeText(this.dataset.copy);this.innerText='" + str(_('Copied')) + "';setTimeout(()=>this.innerText='" + str(_('Copy')) + "',1500);\">" + str(_('Copy')) + "</button>"
        return mark_safe(f"<code>{path}</code> {btn}")
    telegram_webhook_url.short_description = _('Telegram webhook URL')

    def instagram_webhook_url(self, obj):
        if not obj or obj.type != 'instagram':
            return '-'
        path = reverse('instagram-webhook')
        btn = f"<button type='button' class='button' data-copy='{path}' onclick=\"navigator.clipboard.writeText(this.dataset.copy);this.innerText='" + str(_('Copied')) + "';setTimeout(()=>this.innerText='" + str(_('Copy')) + "',1500);\">" + str(_('Copy')) + "</button>"
        return mark_safe(f"<code>{path}</code> {btn}")
    instagram_webhook_url.short_description = _('Instagram webhook URL')

    def instagram_verify_example(self, obj):
        if not obj or obj.type != 'instagram' or not obj.ig_verify_token:
            return '-'
        path = reverse('instagram-webhook')
        example = f"{path}?hub.mode=subscribe&hub.verify_token={obj.ig_verify_token}&hub.challenge=CHALLENGE"
        btn = f"<button type='button' class='button' data-copy='{example}' onclick=\"navigator.clipboard.writeText(this.dataset.copy);this.innerText='" + str(_('Copied')) + "';setTimeout(()=>this.innerText='" + str(_('Copy')) + "',1500);\">" + str(_('Copy')) + "</button>"
        return mark_safe(f"<code>{example}</code> {btn}")
    instagram_verify_example.short_description = _('Instagram verify URL example')

    def test_webhook(self, request, queryset):
        """Attempt to ping configured webhook endpoints and report status."""
        import requests
        from django.contrib import messages
        from django.contrib.sites.models import Site

        scheme = 'https' if request.is_secure() else 'http'
        domain = Site.objects.get_current().domain if 'django.contrib.sites' in settings.INSTALLED_APPS else request.get_host()
        ok, fail = 0, 0
        for acc in queryset:
            try:
                if acc.type == 'telegram' and acc.telegram_webhook_secret:
                    path = reverse('telegram-webhook', args=[acc.telegram_webhook_secret])
                    url = f"{scheme}://{domain}{path}"
                    resp = requests.post(url, json={})
                    if resp.status_code < 400:
                        ok += 1
                    else:
                        fail += 1
                elif acc.type == 'instagram':
                    path = reverse('instagram-webhook')
                    url = f"{scheme}://{domain}{path}"
                    # GET without verify params should still return 403/503; we treat reachable as success
                    resp = requests.get(url)
                    if resp.status_code < 500:
                        ok += 1
                    else:
                        fail += 1
            except Exception:
                fail += 1
        if ok:
            messages.success(request, _(f"Webhook test successful for {ok} account(s)."))
        if fail:
            messages.warning(request, _(f"Webhook test failed for {fail} account(s). Check configuration and server logs."))
    test_webhook.short_description = _('Test webhook connectivity')


@admin.register(ExternalMessage)
class ExternalMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'channel', 'direction', 'external_id', 'sender_id', 'recipient_id', 'created_at')
    list_filter = ('channel__type', 'direction')
    search_fields = ('external_id', 'sender_id', 'recipient_id', 'text')
