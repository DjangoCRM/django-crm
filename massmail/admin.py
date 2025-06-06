from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from crm.site.crmmodeladmin import CrmModelAdmin
from crm.site.crmadminsite import crm_site
from massmail.models import EmailAccount
from massmail.models import EmlMessage
from massmail.models import EmlAccountsQueue
from massmail.models import MailingOut
from massmail.models import MassContact
from massmail.models import Signature
from massmail.site import emailaccountadmin
from massmail.site import emlmessageadmin
from massmail.site import mailingoutadmin
from massmail.site import signatureadmin

class EmailAccountAdmin(emailaccountadmin.EmailAccountAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'name', 'main', 'massmail', 'do_import',
                'email_host', 'imap_host', 'email_host_user',
                'email_host_password', 'email_app_password', 'email_port',
                'from_email', 'email_use_tls', 'email_use_ssl',
                'email_imail_ssl_certfile', 'email_imail_ssl_keyfile',
                'refresh_token'
            )
        }),
        (_('Service information'), {
            'fields': (
                'report', 'today_date', 'today_count',
                'start_incoming_uid', 'start_sent_uid', 'last_import_dt'
            )
        }),
        (_('Additional information'), {
            'fields': (
                ('owner', 'co_owner', 'modified_by'), 'department',
                ('creation_date', 'update_date',)
            )
        }),
    )


class MessageAdmin(emlmessageadmin.EmlMessageAdmin):
    readonly_fields = (
        'modified_by',
        'signature_preview',
        'msg_preview'
    )

    # -- ModelAdmin methods -- #

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.media = forms.Media(js=[])
        return form


class SignatureAdmin(signatureadmin.SignatureAdmin):
    readonly_fields = (
        'modified_by', 'update_date', 'creation_date', 'preview'
    )


class MailingOutAdmin(mailingoutadmin.MailingOutAdmin):
    exclude = []
    readonly_fields = list()  # ('recipients_number',)
    fieldsets = (
        (None, {
            'fields': (
                ('name', 'status'),
                ('content_type', 'recipients_number'),
                'message', 'report',
                'recipient_ids', 'successful_ids', 'failed_ids',
                ('owner', 'modified_by'),
            )
        }),
    )


class MassContactAdmin(CrmModelAdmin):
    list_display = ('content_object', 'content_type', 'object_id', 'email_account', 'massmail',)
    list_filter = (
        ('email_account__owner', admin.RelatedOnlyFieldListFilter),
        'massmail',
        ('content_type', admin.RelatedOnlyFieldListFilter),
        ('email_account', admin.RelatedOnlyFieldListFilter),
    )
    search_fields = ['object_id', ]
    save_on_top = False
    
    # -- ModelAdmin methods -- #

    def get_list_filter(self, request):
        return self.list_filter

    def get_queryset(self, request):
        return super(admin.ModelAdmin, self).get_queryset(request)


admin.site.register(Signature, SignatureAdmin)
admin.site.register(EmlMessage, MessageAdmin)
admin.site.register(MailingOut, MailingOutAdmin)
admin.site.register(EmailAccount, EmailAccountAdmin)
admin.site.register(MassContact, MassContactAdmin)
admin.site.register(EmlAccountsQueue)

crm_site.register(EmailAccount, emailaccountadmin.EmailAccountAdmin)
crm_site.register(EmlMessage, emlmessageadmin.EmlMessageAdmin)
crm_site.register(MailingOut, mailingoutadmin.MailingOutAdmin)
crm_site.register(Signature, signatureadmin.SignatureAdmin)
