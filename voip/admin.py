from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from crm.utils.admfilters import ScrollRelatedOnlyFieldListFilter

from voip.models import Connection
from voip.models import IncomingCall
from voip.models import VoipSettings


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
