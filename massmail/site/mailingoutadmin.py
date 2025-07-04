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
from massmail.utils.helpers import get_rendered_msg
from settings.models import MassmailSettings

accounts_title = _("Available Email accounts for MassMail")
accounts_str = _('Accounts')
accounts_safe_str = mark_safe(
    f'<div title="{accounts_title}">{accounts_str}</div>')
content_type_str = _("Recipient<br>type")
no_massmal_account_str = _("You do not have an email account available for massmaling.")
no_redirect_url_str = _("The address for redirecting unsubscribed recipients is not specified."
                       " Contact the administrator.")
vip_recipients_only_str = _("You have one Email account with Mailing enabled. "
        "As the main account, it can only send emails to VIP recipients.")
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
        'display_preview', 'content_type_name', 'status',
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
        'content_type', 'sent_today', 'display_preview',
        'available_accounts', 'notification', 'recipients',
        "msg_preview", 'exclude_recipients'
    )
    actions = [merge_mailing_outs]
    list_per_page = 20
    search_fields = ("name", "message__subject", "message__content")

    # -- ModelAdmin methods -- #

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        now = timezone.localtime(timezone.now())
        weekday = now.weekday()
        if weekday in (4, 5, 6):
            messages.warning(request, gettext(FRIDAY_SATURDAY_SUNDAY_MSG))
        return super().changelist_view(request, extra_context)

    def get_fieldsets(self, request, obj=None):
        fields = [
            ('status', 'content_type'),
        ]
        if obj:
            if obj.message:
                fields.append(
                    ('recipients_number', 'exclude_recipients')
                )
            else:
                fields.append('recipients_number')
        fields.append('message')
        if obj:
            if obj.report:
                fields.append('report')
            if obj.message:
                fields.append('msg_preview')
        fields.append(('owner', 'modified_by'))
        fieldsets = [(None, {'fields': fields})]
        return fieldsets

    def save_model(self, request, obj, form, change):
        if 'status' in form.changed_data and obj.status == obj.ACTIVE:
            eas = EmailAccount.objects.filter(
                owner=obj.owner,
                massmail=True
            )
            if not eas.exists():
                obj.status = obj.PAUSED
                messages.error(
                    request,
                    gettext(no_massmal_account_str)
                )
            elif eas.count() == 1 and eas.first().main:
                messages.warning(
                    request,
                    gettext(vip_recipients_only_str)
                )
            massmail_settings = MassmailSettings.objects.get(id=1)
            if massmail_settings.unsubscribe_url in ("https://www.example.com/unsubscribe", ''):
                messages.warning(
                    request,
                    gettext(no_redirect_url_str)
                )
        if not obj.name:
            if obj.message:
                obj.name = obj.message.subject
            else:
                obj.name = settings.NO_NAME_STR
        else:
            if obj.name == settings.NO_NAME_STR and obj.message:
                obj.name = obj.message.subject
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
    @admin.display(description=mark_safe(content_type_str))
    def content_type_name(instance):
        return instance.content_type.name

    @staticmethod
    @admin.display(description=mark_safe(
        '<i class="material-icons" style="color: '
        'var(--body-quiet-color)">subject</i>'
    ), ordering='name')
    def display_preview(obj):
        msg = obj.message
        if msg:
            content = get_rendered_msg(msg)
            style = (
                "overflow:auto; "
                "max-height:300px; "
                "max-width:300px;"
            )
            return mark_safe(
                f'<div class="mailingout-scroll" style="{style}">{content}</div>'
            )
        return obj.name

    @admin.display(description='')
    def exclude_recipients(self, obj):
        from django.urls import reverse
        url = '#'
        if obj.recipient_ids:
            url = reverse(
                'exclude_recipients', args=(obj.id,)
            )
        name = _("Exclude recipients")
        tooltip = _(
            "Exclude recipients who have already received this message.")
        return mark_safe(
            f'<ul class="object-tools" style="margin-left: 0px;margin-top: 0px;">'
            f'<li><a title="{tooltip}" href="{url}">{name}</a></li></ul>'
        )

    @admin.display(description=_("Message"))
    def msg_preview(self, obj):
        if obj.message:
            content = get_rendered_msg(obj.message)
            style = (
                'max-height: 400px; '
                'overflow: auto;'
            )
            return mark_safe(
                f'<div class="emlmessage-scroll" style="{style}">{content}</div>'
            )

    @staticmethod
    @admin.display(description=_('notification'))
    def notification(instance):
        report = instance.report or ""
        lines = report.count('\n') + 1 if report else 0
        content = linebreaksbr(report)
        style = (
            "overflow:auto; "
            "max-height:300px; "
            "white-space:pre-wrap; "
            "word-wrap: break-word;"
        ) if lines >= 20 else "white-space:pre-wrap;"
        div_class = "mailingout-scroll" if lines >= 20 else ""
        return mark_safe(
            f'<div class="{div_class}" style="{style}">{content}</div>'
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
