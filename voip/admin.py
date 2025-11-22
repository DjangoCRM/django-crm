from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from crm.utils.admfilters import ScrollRelatedOnlyFieldListFilter

from voip.models import Connection
from voip.models import IncomingCall
from voip.models import VoipSettings, OnlinePBXSettings


class ConnectionAdmin(admin.ModelAdmin):
    list_display = (
        'callerid', 'provider', 'number', 'type', 'owner', 'active'
    )
    list_filter = (
        'active', 'type',
        ('owner', ScrollRelatedOnlyFieldListFilter)
    )
    fieldsets = (
        (None, {
            'fields': (
                ('provider', 'active'),
                ('number', 'type'),
                'callerid', 'owner'
            )
        }),
    )


admin.site.register(Connection, ConnectionAdmin)


@admin.register(IncomingCall)
class IncomingCallAdmin(admin.ModelAdmin):
    list_display = (
        'caller_id', 'client_name', 'client_type',
        'user', 'created_at', 'is_consumed'
    )
    list_filter = ('is_consumed', 'client_type')
    search_fields = ('caller_id', 'client_name', 'user__username')


class VoipSettingsForm(forms.ModelForm):
    ami_secret = forms.CharField(
        label='AMI secret',
        required=False,
        widget=forms.PasswordInput(render_value=True)
    )

    class Meta:
        model = VoipSettings
        fields = '__all__'


@admin.register(VoipSettings)
class VoipSettingsAdmin(admin.ModelAdmin):
    form = VoipSettingsForm
    fieldsets = (
        (_("Asterisk AMI"), {
            'fields': (
                ('ami_host', 'ami_port'),
                ('ami_username', 'ami_secret'),
                ('ami_use_ssl',),
                ('ami_connect_timeout', 'ami_reconnect_delay'),
            )
        }),
        (_("Incoming popup"), {
            'fields': (
                'incoming_enabled',
                ('incoming_poll_interval_ms', 'incoming_popup_ttl_ms'),
            )
        }),
    )

    def has_add_permission(self, request):
        return not VoipSettings.objects.exists()


@admin.register(OnlinePBXSettings)
class OnlinePBXSettingsAdmin(admin.ModelAdmin):
    change_form_template = 'admin/voip/onlinepbxsettings/change_form_object_tools.html'
    fieldsets = (
        (_("OnlinePBX"), {
            'fields': (
                'domain',
                ('key_id', 'key'),
                'api_key',
                'base_url',
                'use_md5_base64',
            )
        }),
        (_("Webhook security"), {
            'fields': (
                'allowed_ip', 'webhook_token'
            )
        }),
    )

    def has_add_permission(self, request):
        return not OnlinePBXSettings.objects.exists()

    # Custom admin URLs for OnlinePBX operations
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom = [
            path('user/add/', self.admin_site.admin_view(self.user_add_view), name='onlinepbx_user_add'),
            path('user/edit/', self.admin_site.admin_view(self.user_edit_view), name='onlinepbx_user_edit'),
            path('user/get/', self.admin_site.admin_view(self.user_get_view), name='onlinepbx_user_get'),
            path('user/flush-sip/', self.admin_site.admin_view(self.user_flush_sip_view), name='onlinepbx_user_flush_sip'),

            path('group/add/', self.admin_site.admin_view(self.group_add_view), name='onlinepbx_group_add'),
            path('group/edit/', self.admin_site.admin_view(self.group_edit_view), name='onlinepbx_group_edit'),
            path('group/get/', self.admin_site.admin_view(self.group_get_view), name='onlinepbx_group_get'),
            path('group/remove/', self.admin_site.admin_view(self.group_remove_view), name='onlinepbx_group_remove'),

            path('fifo/add/', self.admin_site.admin_view(self.fifo_add_view), name='onlinepbx_fifo_add'),
            path('fifo/edit/', self.admin_site.admin_view(self.fifo_edit_view), name='onlinepbx_fifo_edit'),
            path('fifo/get/', self.admin_site.admin_view(self.fifo_get_view), name='onlinepbx_fifo_get'),

            path('ivr/', self.admin_site.admin_view(self.ivr_get_view), name='onlinepbx_ivr_get'),
            path('ivr/create/', self.admin_site.admin_view(self.ivr_create_view), name='onlinepbx_ivr_create'),
            path('ivr/update/', self.admin_site.admin_view(self.ivr_update_view), name='onlinepbx_ivr_update'),
            path('ivr/delete/', self.admin_site.admin_view(self.ivr_delete_view), name='onlinepbx_ivr_delete'),

            path('blocklist/', self.admin_site.admin_view(self.blocklist_get_view), name='onlinepbx_blocklist_get'),
            path('blocklist/add/', self.admin_site.admin_view(self.blocklist_add_view), name='onlinepbx_blocklist_add'),
            path('blocklist/remove/', self.admin_site.admin_view(self.blocklist_remove_view), name='onlinepbx_blocklist_remove'),
        ]
        return custom + urls

    # Shared handler
    def _handle_form(self, request, title: str, func):
        from django.shortcuts import render
        from voip.forms.onlinepbx_admin import OnlinePBXJSONForm
        from voip.models import OnlinePBXSettings
        from voip.backends.onlinepbxbackend import OnlinePBXAPI
        import json as _json

        form = OnlinePBXJSONForm(request.POST or None)
        response_data = None
        error = None
        if request.method == 'POST' and form.is_valid():
            cfg = OnlinePBXSettings.get_solo()
            client = OnlinePBXAPI(
                domain=cfg.domain,
                key_id=cfg.key_id or None,
                key=cfg.key or None,
                api_key=cfg.api_key or None,
                base_url=cfg.base_url,
                use_base64_md5=cfg.use_md5_base64,
            )
            payload = form.cleaned_data['payload'] or ''
            use_json = form.cleaned_data['use_json']
            try:
                if use_json:
                    data = _json.loads(payload) if payload else {}
                    response_data = func(client, json_data=data)
                else:
                    # parse form-like a=b&c=d into dict
                    form_dict = {}
                    if payload:
                        for part in payload.split('&'):
                            if not part:
                                continue
                            if '=' in part:
                                k, v = part.split('=', 1)
                                form_dict[k] = v
                            else:
                                form_dict[part] = ''
                    response_data = func(client, form=form_dict)
            except Exception as exc:
                error = str(exc)
        ctx = {
            'title': title,
            'form': form,
            'result': response_data,
            'error': error,
        }
        return render(request, 'admin/voip/onlinepbxsettings/action_form.html', ctx)

    # Views mapping to client methods
    def user_add_view(self, request):
        return self._handle_form(request, _('User add'), lambda c, **kw: c.user_add(**(kw.get('json_data') or kw.get('form') or {})))

    def user_edit_view(self, request):
        return self._handle_form(request, _('User edit'), lambda c, **kw: c.user_edit(**(kw.get('json_data') or kw.get('form') or {})))

    def user_get_view(self, request):
        return self._handle_form(request, _('User get'), lambda c, **kw: c.user_get(**(kw.get('json_data') or kw.get('form') or {})))

    def user_flush_sip_view(self, request):
        return self._handle_form(request, _('User flush SIP'), lambda c, **kw: c.user_flush_sip(**(kw.get('json_data') or kw.get('form') or {})))

    def group_add_view(self, request):
        return self._handle_form(request, _('Group add'), lambda c, **kw: c.group_add(**(kw.get('json_data') or kw.get('form') or {})))

    def group_edit_view(self, request):
        return self._handle_form(request, _('Group edit'), lambda c, **kw: c.group_edit(**(kw.get('json_data') or kw.get('form') or {})))

    def group_get_view(self, request):
        return self._handle_form(request, _('Group get'), lambda c, **kw: c.group_get(**(kw.get('json_data') or kw.get('form') or {})))

    def group_remove_view(self, request):
        return self._handle_form(request, _('Group remove'), lambda c, **kw: c.group_remove(**(kw.get('json_data') or kw.get('form') or {})))

    def fifo_add_view(self, request):
        return self._handle_form(request, _('FIFO add'), lambda c, **kw: c.fifo_add(**(kw.get('json_data') or kw.get('form') or {})))

    def fifo_edit_view(self, request):
        return self._handle_form(request, _('FIFO edit'), lambda c, **kw: c.fifo_edit(**(kw.get('json_data') or kw.get('form') or {})))

    def fifo_get_view(self, request):
        return self._handle_form(request, _('FIFO get'), lambda c, **kw: c.fifo_get(**(kw.get('json_data') or kw.get('form') or {})))

    def ivr_get_view(self, request):
        return self._handle_form(request, _('IVR get'), lambda c, **kw: c.ivr_get(**(kw.get('json_data') or kw.get('form') or {})))

    def ivr_create_view(self, request):
        return self._handle_form(request, _('IVR create'), lambda c, **kw: c.ivr_create(**(kw.get('json_data') or kw.get('form') or {})))

    def ivr_update_view(self, request):
        return self._handle_form(request, _('IVR update'), lambda c, **kw: c.ivr_update(**(kw.get('json_data') or kw.get('form') or {})))

    def ivr_delete_view(self, request):
        return self._handle_form(request, _('IVR delete'), lambda c, **kw: c.ivr_delete(**(kw.get('json_data') or kw.get('form') or {})))

    def blocklist_get_view(self, request):
        return self._handle_form(request, _('Blocklist get'), lambda c, **kw: c.blocklist_get(**(kw.get('json_data') or kw.get('form') or {})))

    def blocklist_add_view(self, request):
        return self._handle_form(request, _('Blocklist add'), lambda c, **kw: c.blocklist_add_contacts(**(kw.get('json_data') or kw.get('form') or {})))

    def blocklist_remove_view(self, request):
        return self._handle_form(request, _('Blocklist remove'), lambda c, **kw: c.blocklist_remove_contacts(**(kw.get('json_data') or kw.get('form') or {})))
