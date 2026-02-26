from django.contrib import admin
from django.template.defaultfilters import linebreaks
from django.utils.formats import date_format
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from crm.site.crmmodeladmin import CrmModelAdmin
from crm.utils.admfilters import ByOwnerFilter
from massmail.models import EmlAccountsQueue


EMAILS_SENT = _("Emails Sent That Day")
EMAILS_SENT_TITLE = _("Number of emails sent on that mailing date.")
IMPORT = _("import")
IMPORT_TITLE = _(
    "Shows whether automatic import of emails from the account is enabled.")
LAST_IMPORT_DATE = _("last import date")
LAST_IMPORT_TITLE = _(
    "The date when an email was last imported from this account.")
LAST_MAILING_DATE = _("last mailing date")
LAST_MAILING_TITLE = _(
    "The most recent date when the mass-email campaign was sent.")
MASS_MAILING = _("mass mailing")
MASS_MAILING_TITLE = _("Email account availability for mass mailing.")


class EmailAccountAdmin(CrmModelAdmin):
    list_display = (
        'name', 'main', 'perform_import', 'mass_mailing', 'last_import_date',
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

    @admin.display(description=mark_safe(
        '<i class="material-icons" style="color: var(--body-quiet-color)">subject</i>'
    ))
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
