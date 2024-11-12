from email.utils import parseaddr
from smtplib import SMTPAuthenticationError
from smtplib import SMTPConnectError
from smtplib import SMTPDataError
from smtplib import SMTPRecipientsRefused
from smtplib import SMTPServerDisconnected
from smtplib import SMTPSenderRefused
from typing import List
from django.core.mail.message import BadHeaderError
from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

from crm.models import CrmEmail
from crm.utils.counterparty_name import get_counterparty_name
from massmail.utils.email_creators import email_creator
from massmail.models import EmailAccount

EMAIL_SENT_TO_str = _('The Email has been sent to "%s"')


def send_email(request: WSGIRequest, obj: CrmEmail) -> HttpResponseRedirect:
    eac = EmailAccount.objects.filter(owner=obj.owner, main=True).first()
    msg_error = ""
    if not obj.subject or not obj.content or obj.content == '<br>':
        msg_error = gettext(
            "Please fill in the subject and text of the letter."
        )
    elif not eac:
        msg_error = gettext(
            "To send a message you need to have an email account marked as main."
        )
    if msg_error:
        messages.error(request, msg_error)
        return HttpResponseRedirect(
            reverse("site:crm_crmemail_change", args=(obj.id,))
        )
    to = parse_addr(obj.to)
    cc = parse_addr(obj.cc) if obj.cc else None
    bcc = parse_addr(obj.bcc) if obj.bcc else None
    msg = email_creator(
        obj, eac, to, cc, bcc, force_multipart=True, inline_images=True)
    try:
        msg.send(fail_silently=False)
        obj.sent = True
        to_name = get_counterparty_name(obj)
        if obj.cc:
            entry = gettext(EMAIL_SENT_TO_str) + ', "%s"'
            entry = entry % (to_name, obj.cc)
        else:
            entry = gettext(EMAIL_SENT_TO_str) % to_name
        messages.success(request, entry)
        deal = obj.deal
        if deal:
            deal.add_to_workflow(entry)
            deal.save(update_fields=['workflow'])
    except (
            SMTPAuthenticationError,
            SMTPConnectError,
            SMTPDataError,
            BadHeaderError,
            SMTPRecipientsRefused,
            SMTPServerDisconnected,
            SMTPSenderRefused,
            ValueError
    ) as e:
        messages.error(
            request,
            gettext("Failed: %s") % e
        )
        redirect_url = reverse('site:crm_crmemail_change', args=(obj.id,))
        return HttpResponseRedirect(redirect_url)

    obj.save(update_fields=['sent'])
    return HttpResponseRedirect(reverse("site:crm_crmemail_changelist"))


def parse_addr(addr_str: str) -> List[str]:
    addr_list = []
    raw_addr_list = addr_str.split(',')
    for a in raw_addr_list:
        _, addr = parseaddr(a)
        if addr:
            addr_list.append(addr)
    return addr_list
