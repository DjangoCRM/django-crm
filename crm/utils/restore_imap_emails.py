import io
import email
import threading
from email.utils import parseaddr
from django.db.models import F
from django.db.models import TextField
from django.db.models import Value
from django.db.models.functions import Concat
from django.db import connection
from django.db import IntegrityError
from django.db import transaction
from django.conf import settings
from django.contrib import messages
from django.core.files import File
from django.core.mail import mail_admins
from django.template.defaultfilters import truncatechars
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from common.templatetags.util import replace_lang
from common.utils.helpers import get_formatted_short_date
from common.utils.helpers import save_message
from common.models import TheFile
from crm.models import CrmEmail
from crm.models import Deal
from crm.models import Request
from crm.utils.helpers import ensure_decoding
from crm.utils.helpers import delete3enters
from crm.utils.helpers import html2txt
from crm.utils.helpers import get_email_date
from crm.utils.ticketproc import get_ticket
from crm.utils.helpers import get_uid_data
from massmail.models import EmailAccount

EXCEPT_SUBJECT = 'RestoreImapEmails Exception'


class RestoreImapEmails(threading.Thread):

    def __init__(self, eml_queue, inq_eml_queue):
        threading.Thread.__init__(self)
        self.daemon = True
        self.eml_queue = eml_queue
        self.inq_eml_queue = inq_eml_queue

    def run(self):
        while True:
            raw_content = ea = t = uid = ''
            try:
                item, ea, t, uid, ticket, request = self.eml_queue.get()
                email_message = email.message_from_bytes(
                    item, policy=email.policy.default)
                uid_data = get_uid_data(ea)
                if received_from_crm(email_message):
                    if request:
                        messages.error(
                            request,
                            "ERROR: Trying to import an email sent from CRM!"
                        )
                        request = None
                    else:
                        if int(uid) > getattr(ea, uid_data[t]['start_uid']):
                            update_ea(ea, uid_data, t, uid)
                    connection.close()
                    self.eml_queue.task_done()
                    continue

                subj = ensure_decoding(email_message['Subject'])
                richest = email_message.get_body(   # NOQA
                    preferencelist=('plain', 'html', 'related'))
                if richest is None:
                    if email_message.is_multipart():
                        raw_content, is_html, e = '', False, ''
                    else:
                        raise RuntimeError("Unknown content")
                else:
                    raw_content, is_html, e = get_raw_content(
                        richest, ea, t, uid, subj)
                if e:
                    self.eml_queue.task_done()
                    continue
                if t != 'inquiry':
                    ticket = ticket or get_ticket((subj, raw_content))
                    if not ticket:
                        update_ea(ea, uid_data, t, uid)
                        connection.close()
                        self.eml_queue.task_done()
                        continue
                    crm_eml = CrmEmail(
                        ticket=ticket,
                        incoming=uid_data[t]['incoming'],
                        sent=uid_data[t]['sent']
                    )
                    update_with_deal_and_request(crm_eml, ticket)
                else:
                    crm_eml = CrmEmail(inquiry=True, incoming=True)

                crm_eml.creation_date = get_email_date(email_message)
                crm_eml.content = html2txt(
                    raw_content) if is_html else delete3enters(raw_content)
                crm_eml.to = email_message['To']
                crm_eml.cc = email_message['CC']
                crm_eml.bcc = email_message['BCC']
                crm_eml.subject = truncatechars(subj, 220)   # 250 - 30
                crm_eml.from_field = parseaddr(email_message['From'])[1]
                crm_eml.uid = int(uid)
                crm_eml.imap_host = ea.imap_host
                crm_eml.email_host_user = ea.email_host_user
                crm_eml.owner = ea.owner
                crm_eml.department = ea.department
                crm_eml.is_html = False
                if email_message['Message-ID'] is not None:
                    crm_eml.message_id = email_message['Message-ID']
                if eml_already_exists(email_message, uid):
                    continue
                try:
                    self.crm_eml_save(crm_eml, t, uid_data, uid, ea, email_message)
                    self.eml_queue.task_done()
                except IntegrityError as e:
                    raise e
                except Exception as e:
                    if f'{e}'.count('Incorrect string value:'):
                        if f'{e}'.count('content'):
                            crm_eml.content = '--- ERROR importing content of the email ---'
                        elif f'{e}'.count('subject'):
                            crm_eml.subject = '--- ERROR importing content of the email ---'
                        self.crm_eml_save(crm_eml, t, uid_data, uid, ea, email_message)
                    raise e

            except Exception as e:
                mail_admins(
                    EXCEPT_SUBJECT,
                    f"""
                    \nEmail account: {ea}
                    \nEmail account: {ea.owner}
                    \nException: {e}
                    \nType: {t}
                    \nUID: {uid}
                    \nraw_content: {raw_content}
                    """,
                    fail_silently=True,
                )
                self.eml_queue.task_done()

            connection.close()

    def crm_eml_save(self, crm_eml: CrmEmail, t: str, uid_data: dict, uid: str,
                     ea: EmailAccount, email_message: email.message.Message) -> None:
        with transaction.atomic():
            crm_eml.save()
            if t != 'inquiry':
                update_ea(ea, uid_data, t, uid)
        attach_files(email_message, crm_eml)
        if t == 'inquiry':
            self.inq_eml_queue.put((crm_eml, email_message['From'], ea))
        if crm_eml.ticket:
            f_date = get_formatted_short_date()
            msg = ''
            if t in ('incoming', 'inquiry'):
                msg = _('Received an email from "%s"') % crm_eml.from_field
                if t == 'incoming':
                    notify_user(crm_eml, msg)

            elif t == 'sent':
                msg = _('The Email has been sent to "%s"') % crm_eml.to
            msg_str = f"{f_date} - {msg}\n"
            Deal.objects.filter(ticket=crm_eml.ticket).update(
                workflow=Concat(Value(msg_str), F('workflow'),  output_field=TextField())
            )


def notify_user(crm_eml: CrmEmail, msg: str) -> None:
    if crm_eml.deal:
        url = f"{crm_eml.deal.get_absolute_url()}#Emails"
    elif crm_eml.request:
        url = f"{crm_eml.request.get_absolute_url()}#Emails"
    else:
        url = crm_eml.get_absolute_url()
    url = replace_lang(url, crm_eml.owner.profile.language_code)
    message = mark_safe(f'{msg}: <a href="{url}">{crm_eml.subject}</a>')
    save_message(crm_eml.owner, message)


def update_ea(ea: EmailAccount, uid_data: dict, t: str, uid: str) -> None:
    """ Update start_uid and last import datetime"""
    setattr(ea, uid_data[t]['start_uid'], int(uid) + 1)
    ea.last_import_dt = timezone.now()
    ea.save(update_fields=[uid_data[t]['start_uid'], 'last_import_dt'])


def received_from_crm(email_message: email.message.Message) -> bool:
    """ Checks if a letter was received from CRM"""
    received = email_message['Received']
    if received:
        if received.count(settings.CRM_IP):
            return True
    return False


def get_raw_content(richest, ea: EmailAccount, t: str, uid: str, subj: str):
    raw_content, is_html, err = '', True, None

    try:
        if richest.get_content_type() == 'multipart/related':
            richest = richest.get_body(
                preferencelist=('plain', 'html', 'related'))
        if richest.get_content_maintype() == 'text':
            raw_content = richest.get_content()
            subtype = richest.get_content_subtype()
            if subtype == 'plain':
                is_html = False
            elif subtype == 'html':
                is_html = True
            else:
                raw_content = f"-- Unknown format --\n{richest}"
                mail_admins(
                    'RestoreImapEmails Exception - Unknown format',
                    f'''\nEmail account: {ea}
                        \nOwner: {ea.owner}
                        \nType: {t}
                        \nUID: {uid}
                        \n Subject: {subj}
                        \n{raw_content}''',
                    fail_silently=True,
                )
    except Exception as e:
        err = e
        # LookupError: unknown encoding: windows-874
        mail_admins(
            f'RestoreImapEmails.get_raw_content Exception - {e}',
            f'''\nEmail account: {ea}
            \nOwner: {ea.owner}
            \nType: {t}
            \nUID: {uid}
            \n Subject: {subj}
            \n richest: {richest}''',
            fail_silently=True,
        )
    return raw_content, is_html, err


def attach_files(email_message: email.message.Message, crm_eml: CrmEmail) -> None:
    if email_message.is_multipart():
        for part in email_message.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue
            filename = part.get_filename()
            if filename and part.get_content_disposition() == 'attachment':
                filename = ensure_decoding(filename)
                f = io.BytesIO(part.get_payload(decode=True))
                memory_file = File(f)
                the_file = TheFile(content_object=crm_eml)
                the_file.save()
                attached_file = getattr(the_file, 'file')
                attached_file.save(filename, memory_file)
                f.close()


def eml_already_exists(email_message, uid) -> bool:
    if email_message['Message-ID']:
        return CrmEmail.objects.filter(
            message_id=email_message['Message-ID']).exists()
    
    if email_message['Date'] or email_message['Delivery-date']:
        return CrmEmail.objects.filter(
            uid=int(uid),
            creation_date=get_email_date(email_message)
        ).exists()

    return CrmEmail.objects.filter(
        uid=int(uid),
        subject=ensure_decoding(email_message['Subject']),
    ).exists()   


def update_with_deal_and_request(crm_eml: CrmEmail, ticket: str) -> None:
    """
    Gets a deal or request using a ticket and sets fk on it. 
    It also sets fk on Lead, Contact and Company.
    """
    try:
        deal = Deal.objects.get(ticket=ticket)
        crm_eml.deal = deal
        crm_eml.lead = deal.lead
        crm_eml.request = deal.request
        if deal.contact:
            crm_eml.contact = deal.contact
            crm_eml.company = deal.contact.company
    except Deal.DoesNotExist:
        try:
            request = Request.objects.get(ticket=ticket)
            crm_eml.request = request
            crm_eml.lead = request.lead
            crm_eml.contact = request.contact
            crm_eml.company = request.company
        except Request.DoesNotExist:
            return
