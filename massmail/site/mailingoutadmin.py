from django.contrib import admin
from django.conf import settings
from django.contrib import messages
from django.template.defaultfilters import linebreaksbr
from django.utils import timezone
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe

from common.utils.helpers import FRIDAY_SATURDAY_SUNDAY_MSG
from common.utils.helpers import get_today
from crm.site.crmmodeladmin import CrmModelAdmin
from crm.utils.admfilters import ByOwnerFilter
from massmail.admin_actions import merge_mailing_outs
from massmail.models import EmailAccount
from massmail.utils.adminfilters import StatusMailingFilter

accounts_title = _("Available Email accounts for MassMail")
accounts_str = _('Accounts')
accounts_safe_str = mark_safe(
    f'<div title="{accounts_title}">{accounts_str}</div>')
content_type__str = _("Recipients type")
progress_safe_str = mark_safe(
    f'<i class="material-icons" style="color: var(--body-quiet-color)">'
    f'trending_up</i></a>'
)
recipients_title_str = _("Number of recipients")
today_str = _('Today')
today_title_str = _("Sent today")
today_safe_str = mark_safe(
    f'<div title="{today_title_str}">{today_str}</div>')


class MailingOutAdmin(CrmModelAdmin):
    raw_id_fields = ('message',)
    list_display = (
        'mailingout_name', 'content_type_name', 'status',
        'progress', 'person', 'sent_today', 'recipients',
        'available_accounts', 'created', 'notification'
    )
    list_filter = (StatusMailingFilter, ByOwnerFilter)
    save_on_top = True
    exclude = (
        'recipient_ids', 'successful_ids', 'failed_ids', 'department',
    )
    readonly_fields = (
        'recipients_number', 'owner', 'modified_by',
        'content_type', 'sent_today', 'mailingout_name',
        'available_accounts', 'notification', 'recipients'
    )
    actions = [merge_mailing_outs]
    list_per_page = 20
    fieldsets = (
        (None, {
            'fields': (
                ('name', 'status'),
                ('content_type', 'recipients_number'),
                'message', 'report', ('owner', 'modified_by'),
            )
        }),
    )
    search_fields = ("name", "message__subject", "message__content")

    # -- ModelAdmin methods -- #

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        now = timezone.localtime(timezone.now())
        weekday = now.weekday()
        if weekday in (4, 5, 6):
            messages.warning(request, gettext(FRIDAY_SATURDAY_SUNDAY_MSG))
        return super().changelist_view(request, extra_context)

    def save_model(self, request, obj, form, change):
        if not obj.name:
            obj.name = settings.NO_NAME_STR
        super().save_model(request, obj, form, change)

    # -- ModelAdmin callables -- #

    @staticmethod
    @admin.display(description=accounts_safe_str)
    def available_accounts(instance):
        value = ''
        eas = EmailAccount.objects.filter(owner=instance.owner)
        for ea in eas:
            if ea.massmail:
                value += '<span style="color: var(--green-fg)">&#9733;</span>'
            else:
                value += '<span style="color: var(--error-fg)">&#9733;</span>'
        return mark_safe(value)
    
    @staticmethod
    @admin.display(description=mark_safe(
        '<i class="material-icons" style="color: '
        'var(--body-quiet-color)">subject</i>'
    ), ordering='name')
    def mailingout_name(instance):
        return instance.name
    
    @staticmethod
    @admin.display(description=content_type__str)
    def content_type_name(instance):
        return instance.content_type.name
    
    @staticmethod
    @admin.display(description=_('notification'))
    def notification(instance):
        report = instance.report or ""
        lines = report.count('\n') + 1 if report else 0
        content = linebreaksbr(report)
        style = (
            "overflow:auto; max-height:200px;"
            "white-space:pre-wrap;"
        ) if lines >= 20 else "white-space:pre-wrap;"
        custom_scrollbar = (
            "<style>"
            "div.mailingout-scroll::-webkit-scrollbar {width:10px;}"
            "div.mailingout-scroll::-webkit-scrollbar-thumb {background:#ccc; border-radius:3px;}"
            "</style>"
            if lines >= 20 else ""
        )
        div_class = "mailingout-scroll" if lines >= 20 else ""
        return mark_safe(
            f'{custom_scrollbar}<div class="{div_class}" style="{style}">{content}</div>'
        )
    
    @staticmethod
    @admin.display(description=progress_safe_str)
    def progress(instance):
        rt_ids = instance.get_recipient_ids()
        tn = len(rt_ids)
        rn = instance.recipients_number
        if rn == 0:
            return '0 %'
        return str(round((rn - tn) / rn * 100, 2)) + '%'
    
    @staticmethod
    @admin.display(description=mark_safe(
        f'<a title="{recipients_title_str}">'
        '<i class="material-icons" style="color: '
        'var(--body-quiet-color)">people_outline</i></a>'
    ))
    def recipients(instance):
        return instance.recipients_number

    @staticmethod
    @admin.display(description=today_safe_str)
    def sent_today(instance):
        if instance.sending_date == get_today():
            return instance.today_count
        return 0
