from django.conf import settings
from django.contrib import admin
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.db.models import Q
from django.http import HttpRequest
from django.http import HttpResponseRedirect
from django.template.defaultfilters import truncatechars
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from common.utils.helpers import FRIDAY_SATURDAY_SUNDAY_MSG
from massmail.models import EmailAccount
from massmail.models import MailingOut
from massmail.models import MassContact

MULTIPLE_OWNERS_MSG = _("Please select recipients only with the same owner.")
BAD_RESULT_MSG = _("Bad result - no recipients! Make another choice.")

@admin.action(description=_(
    "Create a mailing out for selected objects"))
def make_mailing_out(modeladmin, request, queryset):
    if not have_massmail_accounts(request)\
            or multiple_owners(request, queryset):
        return HttpResponseRedirect(request.path)

    q_params = Q(massmail=False)
    q_params |= Q(disqualified=True)
    if queryset.filter(q_params).exists():
        queryset= queryset.exclude(q_params)
        messages.warning(
            request,
            _("Unsubscribed users were excluded from the mailing list.")
        )
    if not queryset.exists():
        messages.error(
            request,
            _(BAD_RESULT_MSG)
        )
        return HttpResponseRedirect(request.path)

    content_type = ContentType.objects.get_for_model(queryset.model)
    mailing_out = MailingOut.objects.create(
        name=settings.NO_NAME_STR,
        content_type=content_type,
        owner=request.user,
        modified_by=request.user,
        department_id=request.user.department_id,
        recipient_ids=",".join([str(obj.id) for obj in queryset]),
        recipients_number=queryset.count()
    )
    messages.info(request, _(FRIDAY_SATURDAY_SUNDAY_MSG))
    return HttpResponseRedirect(
        reverse(
            'site:massmail_mailingout_change',
            args=(mailing_out.id,)
        )
    )


@admin.action(description=_("Merge selected mailing outs"))
def merge_mailing_outs(modeladmin, request, queryset):
    if any((multiple_owners(request, queryset),
            multiple_content_types(request, queryset),
            multiple_messages(request, queryset))):
        return HttpResponseRedirect(request.path)
    recipient_ids, successful_ids, failed_ids = [], [], []
    report, recipients_number = '', 0
    for mo in queryset:
        r_ids = mo.get_recipient_ids()
        recipient_ids.extend(r_ids)
        s_ids = mo.get_successful_ids()
        successful_ids.extend(s_ids)
        f_ids = mo.get_failed_ids()
        failed_ids.extend(f_ids)
        recipients_number += mo.recipients_number
        if mo.report:
            report += f"\n\n<+>\n\n{mo.report}\n\n"
    recipient_ids = list(set(recipient_ids))
    m_o = queryset.first()
    united = _("united")
    name = m_o.name + f' ({united})'
    name_len = len(name)
    if name_len > 100:
        delta = name_len - 100
        name = truncatechars(m_o.name, 100 - delta) + f' ({_("united")})'
    m_o.id = None
    m_o.name = name
    m_o.recipient_ids = ",".join([str(x) for x in recipient_ids])
    m_o.successful_ids = ",".join([str(x) for x in successful_ids])
    m_o.failed_ids = ",".join([str(x) for x in failed_ids])
    m_o.recipients_number = recipients_number
    m_o.report = report
    m_o.save()
    messages.success(
        request,
        f' {queryset.count()} mailing outs have been merged.'
    )
    queryset.delete()
    return HttpResponseRedirect(reverse('site:massmail_mailingout_change', args=(m_o.id,)))


@admin.action(description=_("Specify VIP recipients"))
def specify_vip_recipients(modeladmin, request, queryset):
    owner = queryset[0].owner
    try:
        mea = EmailAccount.objects.get(owner=owner, main=True)
    except EmailAccount.DoesNotExist:
        messages.warning(
            request,
            _('Please first add your main email account.')
        )
        return HttpResponseRedirect(request.path)

    if multiple_owners(request, queryset):
        return HttpResponseRedirect(request.path)

    selected = list(set(request.POST.getlist(ACTION_CHECKBOX_NAME)))
    selected_ids = [int(x) for x in selected]
    content_type = ContentType.objects.get_for_model(queryset.model)
    mcs = MassContact.objects.filter(
        object_id__in=selected_ids,
        content_type=content_type
    )
    n = mcs.update(email_account=mea)
    if n != len(selected_ids):
        updated_ids = mcs.values_list('object_id', flat=True)
        create_ids = [x for x in selected_ids if x not in updated_ids]
        for x in create_ids:
            mc = MassContact(
                content_type=content_type,
                object_id=x,
                content_object=queryset.get(id=x),
                email_account=mea
            )
            mc.save()
    messages.success(
        request,
        _("The main email address has been successfully assigned to the selected recipients.")
    )
    return HttpResponseRedirect(request.path)


def multiple_content_types(request, queryset):
    message = _("Please select mailings with only the same recipient type.")
    return multiple_value(request, queryset, 'content_type', message)


def multiple_messages(request, queryset):
    message = _("Please select only mailings with the same message.")
    return multiple_value(request, queryset, 'message', message)


def multiple_owners(request, queryset):
    message = _(MULTIPLE_OWNERS_MSG)
    return multiple_value(request, queryset, 'owner', message)


def multiple_value(request, queryset, value, message):
    value_num = len(set(queryset.values_list(value, flat=True)))
    if value_num > 1:
        messages.warning(request, message)
        return True
    return False


def have_massmail_accounts(request: HttpRequest) -> bool:
    """Check if there are user's Email accounts
     available for the massmail"""

    accounts = EmailAccount.objects.filter(
        massmail=True,
        owner=request.user
    )
    if not accounts:
        messages.warning(
            request,
            _(
                "There are no mail accounts available for mailing."
                " Please contact your administrator."
            )
        )
    elif not accounts.exclude(main=True):
        messages.warning(
            request,
            _(
                "There are no mail accounts available for mailing to non-VIP recipients."
                " Please contact your administrator."
            )
        )
    num = accounts.count()
    return bool(num)
