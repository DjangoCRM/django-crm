from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from common.utils.copy_files import copy_files
from crm.models import CrmEmail
from crm.settings import KEEP_TICKET
from crm.utils.helpers import html2txt
from crm.utils.ticketproc import get_ticket
from crm.utils.ticketproc import get_ticket_str
from massmail.models import EmailAccount
from massmail.models import Signature


def reply_email(request: WSGIRequest,
                object_id: int) -> HttpResponseRedirect:
    """Create new CrmEmail instance for reply or forward action
     and opens it for editing.
    """

    ea = EmailAccount.objects.filter(
        owner=request.user, main=True
    ).first()
    if not ea:
        return _get_warning(request, object_id)

    rep_eml = CrmEmail.objects.get(id=object_id)
    subject = " ".join(rep_eml.subject.splitlines())
    signature = Signature.objects.filter(
        owner=request.user, default=True
    ).first()

    new_eml = _get_new_eml(ea, rep_eml, request, signature)
    act = request.GET.get('act')
    if act == 'reply-all':
        new_eml.cc = rep_eml.cc

    if act == 'forward':
        new_eml.subject = f"Fwd: {subject}"
        fwd_msg = _get_fwd_msg(rep_eml, subject)

        if not rep_eml.is_html:
            new_eml.content = fwd_msg + "<br>".join(rep_eml.content.splitlines())
        else:
            new_eml.content = fwd_msg + rep_eml.content

    else:
        new_eml.subject = f"Re: {subject}"
        new_eml.prev_corr = _get_prev_corr(rep_eml)
        new_eml.to = rep_eml.from_field if rep_eml.incoming else rep_eml.to

    if rep_eml.ticket:
        new_eml.content += KEEP_TICKET % rep_eml.ticket
        if not get_ticket((subject,)):
            new_eml.subject += get_ticket_str(rep_eml.ticket)

    new_eml.save()
    if act == 'forward':
        copy_files(rep_eml, new_eml)

    return HttpResponseRedirect(reverse(
        'site:crm_crmemail_change', args=(new_eml.id,))
    )


def _get_new_eml(ea: EmailAccount, rep_eml: CrmEmail,
                 request: WSGIRequest, signature: str) -> CrmEmail:
    """Returns a new CrmEmail instance with most fields filled in."""

    department_id = request.user.department_id or rep_eml.department_id  # NOQA
    return CrmEmail(
        from_field=ea.from_email,
        signature=signature,
        owner=request.user,
        department_id=department_id,
        deal=rep_eml.deal,
        lead=rep_eml.lead,
        request=rep_eml.request,
        contact=rep_eml.contact,
        company=rep_eml.company,
        ticket=rep_eml.ticket,
        is_html=True
    )


def _get_fwd_msg(rep_eml: CrmEmail, subject: str) -> str:
    """Return paragraph with information about the message being forwarded."""

    return f"""<div>============ Forwarded Message ============
        <div style="padding-left: 20px;">
            From: {rep_eml.from_field}<br>
            To: {rep_eml.to}<br>
            Date: {rep_eml.creation_date}<br>
            Subject: {subject}<br>
        </div>============ Forwarded Message ============</div><br>
        """


def _get_prev_corr(rep_eml: CrmEmail) -> str:
    """Return content of original email marked symbols '>'."""

    info_paragraph = f"""
    ============ Original Message ============ 
        From: {rep_eml.from_field}
        To: {rep_eml.to}
        Sent: {rep_eml.creation_date}
        Subject: {rep_eml.subject}
    ============ Original Message ============
    """

    content = rep_eml.content
    if rep_eml.is_html:
        content = html2txt(content)
    content = "\r\n> ".join(content.splitlines())
    return f"{info_paragraph}\r\n>{content}"


def _get_warning(request: WSGIRequest,
                 object_id: int) -> HttpResponseRedirect:

    messages.error(
        request,
        _(
            "You do not have an email account in CRM for sending Emails."
            " Contact your administrator."
        )
    )
    return HttpResponseRedirect(
        reverse('site:crm_crmemail_change', args=(object_id,))
    )
