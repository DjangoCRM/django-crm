from django.contrib import messages
from django.db.models import Q
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext as _

from crm.site.crmadminsite import crm_site
from common.utils.permissions import object_not_found_response
from massmail.models.mailing_out import MailingOut


def exclude_recipients(request, object_id: int) -> HttpResponseRedirect:
    """
    This view excludes recipients from the mailing out who 
    have already received the message (object.message).
    """
    mailingout_admin = crm_site._registry[MailingOut]
    mo = mailingout_admin.get_queryset(request).filter(pk=object_id).first()
    if not mo or not mailingout_admin.has_change_permission(request, mo):
        return object_not_found_response(request, mailingout_admin, object_id)
    mos = mailingout_admin.get_queryset(request).filter(
        message=mo.message,
        content_type=mo.content_type
    )
    recipient_ids = mo.recipient_ids.split(',')
    excluded_num = 0
    regex_queries = Q()
    for recipient_id in recipient_ids:
        regex_queries |= Q(successful_ids__iregex=fr"(^|,){recipient_id}(,|$)")

    excluded_ids = set()
    if regex_queries:
        excluded_recipients = mos.filter(regex_queries).values_list('successful_ids', flat=True)
        for successful_ids in excluded_recipients:
            if not successful_ids:
                continue
            ids = successful_ids.split(',')
            excluded_ids.update(ids)

    if excluded_ids:
        recipient_ids_new = [rid for rid in recipient_ids if rid not in excluded_ids]
        excluded_num = len(recipient_ids) - len(recipient_ids_new)
        mo.recipient_ids = ','.join(recipient_ids_new)
        mo.recipients_number = len(recipient_ids_new)
        mo.save(update_fields=['recipient_ids', 'recipients_number'])

    messages.info(
        request,
        _(
            "Number of excluded recipients: {}."
        ).format(excluded_num)
    )

    url = reverse('site:massmail_mailingout_change', args=(mo.id,))
    return HttpResponseRedirect(url)
