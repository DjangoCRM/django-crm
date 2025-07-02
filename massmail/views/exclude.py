from django.contrib import messages
from django.db.models import Q
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext as _

from massmail.models.mailing_out import MailingOut


def exclude_recipients(request, object_id: int) -> HttpResponseRedirect:
    """
    This view excludes recipients from the mailing out who 
    have already received the message (object.message).
    """
    mo = MailingOut.objects.get(id=object_id)
    mos = MailingOut.objects.filter(message=mo.message, content_type=mo.content_type)
    recipient_ids = mo.recipient_ids.split(',')
    excluded_num = 0
    regex_queries = Q()
    for recipient_id in recipient_ids:
        regex_queries |= Q(successful_ids__iregex=fr"(^|,){recipient_id}(,|$)")

    if regex_queries:
        excluded_ids = set()
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
