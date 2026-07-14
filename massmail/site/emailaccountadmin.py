from django.contrib import admin
from django.template.defaultfilters import linebreaks
from django.urls import reverse
from django.utils.formats import date_format
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from common.utils.helpers import CONTENT_COPY_ICON
from common.utils.helpers import CONTENT_COPY_LINK
from common.utils.helpers import COPY_STR
from common.utils.helpers import SAFE_SUBJECT_ICON
from crm.site.crmmodeladmin import CrmModelAdmin
from crm.utils.admfilters import ByOwnerFilter
from massmail.models import EmlAccountsQueue


EMAILS_SENT = _("Emails Sent That Day")
EMAILS_SENT_TITLE = _("Number of emails sent on that mailing date")
IMPORT = _("import")
IMPORT_TITLE = _(
    "Shows whether automatic import of emails from the account is enabled")
LAST_IMPORT_DATE = _("last import date")
LAST_IMPORT_TITLE = _(
    "The date when an email was last imported from this account")
LAST_MAILING_DATE = _("last mailing date")
LAST_MAILING_TITLE = _(
    "The most recent date when the mass-email campaign was sent")
MAIN = _("main")
MAIN_TITLE = _("Default email account for all customer correspondence")
MASS_MAILING = _("mass mailing")
MASS_MAILING_TITLE = _("Email account availability for mass mailing")
COPIED_FIELDS = (
    'name',
    'massmail',
    'do_import',
    'email_host',
    'imap_host',
    'email_host_user',
    'email_host_password',
    'email_app_password',
    'email_port',
    'from_email',
    'email_use_tls',
    'email_use_ssl',
    'email_imail_ssl_certfile',
    'email_imail_ssl_keyfile',
    'refresh_token',
    'owner',
    'co_owner',
    'department',
)


class EmailAccountAdmin(CrmModelAdmin):
    list_display = (
        'account', 'main_account', 'perform_import', 'mass_mailing', 'last_import_date',
        'last_mailing_date', 'emails_sent', 'notifications',  'owner'
    )

    readonly_fields = ('creation_date', 'update_date',)
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
        ('Additional information', {
            'classes': ('collapse',),
            'fields': (
                ('owner', 'co_owner', 'modified_by'), 'department',
                ('creation_date', 'update_date',)
            )
        }),
    )
    save_as = True
    search_fields = ('name', "email_host", "email_host_user")

    # -- ModelAdmin methods -- #

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        email_account_id = request.GET.get('copy_email_account')
        if email_account_id:
            email_account = self.get_object(request, email_account_id)
            if email_account:
                for field in COPIED_FIELDS:
                    initial[field] = getattr(email_account, field)
                initial['main'] = False
        return initial

    def get_list_display(self, request):
        list_display = list(super().get_list_display(request))
        if self.has_add_permission(request):
            list_display.append('content_copy')
        return list_display

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(owner=request.user)

    def get_list_filter(self, request):
        list_filter = super().get_list_filter(request)
        if request.user.is_superuser:
            list_filter.append(ByOwnerFilter)
            return list_filter
        return []

    def has_view_permission(self, request, obj=None):
        if not obj:
            return super().has_view_permission(request, obj=None)
        if request.user.is_superuser:
            return True
        if obj.owner == request.user:
            return True
        return False

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        queue_obj, _ = EmlAccountsQueue.objects.get_or_create(
            owner=obj.owner)
        if obj.massmail and not obj.main:
            queue_obj.add_id(obj.pk)

        if change:
            if 'main' in form.changed_data and obj.main:
                queue_obj.remove_id(obj.pk)
            if 'owner' in form.changed_data:
                queue_objs = EmlAccountsQueue.objects.all()
                for qobj in queue_objs:
                    qobj.remove_id(obj.pk)

    # -- ModelAdmin Callables -- #

    @admin.display(description='')
    def content_copy(self, obj):
        url = reverse(
            "site:massmail_emailaccount_add"
        ) + f"?copy_email_account={obj.id}"
        return mark_safe(
            CONTENT_COPY_LINK.format(url, COPY_STR, CONTENT_COPY_ICON)
        )

    @admin.display(description=SAFE_SUBJECT_ICON)
    def account(self, obj):
        return obj.name

    @admin.display(description=mark_safe(
        f'<div title="{EMAILS_SENT_TITLE}">{EMAILS_SENT}</div>'
    ))
    def emails_sent(self, obj):
        return mark_safe(
            f'<div title="{EMAILS_SENT_TITLE}">{obj.today_count}</div>')

    @admin.display(description=mark_safe(
        f'<div title="{LAST_IMPORT_TITLE}">{LAST_IMPORT_DATE}</div>'
    ))
    def last_import_date(self, obj):
        if obj.last_import_dt:
            date = date_format(
                obj.last_import_dt,
                format="DATETIME_FORMAT",
                use_l10n=True
            )
            return mark_safe(
                f'<div title="{LAST_IMPORT_TITLE}">{date}</div>')

    @admin.display(description=mark_safe(
        f'<div title="{LAST_MAILING_TITLE}">{LAST_MAILING_DATE}</div>')
    )
    def last_mailing_date(self, obj):
        if obj.today_date:
            date = date_format(
                obj.today_date,
                format="SHORT_DATE_FORMAT",
                use_l10n=True
            )
            return mark_safe(
                f'<div title="{LAST_MAILING_TITLE}">{date}</div>')

    @admin.display(description=mark_safe(
        f'<div title="{MAIN_TITLE}">{MAIN}</div>'),
        boolean=True,
    )
    def main_account(self, obj):
        return obj.main

    @admin.display(description=mark_safe(
        f'<div title="{MASS_MAILING_TITLE}">{MASS_MAILING}</div>'),
        boolean=True,
    )
    def mass_mailing(self, obj):
        return obj.massmail

    @admin.display(description=_('notifications'))
    def notifications(self, instance):
        return mark_safe(linebreaks(instance.report))

    @admin.display(description=mark_safe(
        f'<div title="{IMPORT_TITLE}">{IMPORT}</div>'),
        boolean=True,
    )
    def perform_import(self, obj):
        return obj.do_import
