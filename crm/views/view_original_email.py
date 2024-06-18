import email
import mimetypes
import os
from base64 import b64encode
from email import policy
from email.message import Message
from typing import Optional
from django.core.handlers.wsgi import WSGIRequest
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render
from django.template.defaultfilters import linebreaks
from django.http import HttpResponse

from common.utils.helpers import OBJ_DOESNT_EXIT_STR
from crm.models import CrmEmail
from crm.utils.crm_imap import CrmIMAP
from crm.utils.helpers import ensure_decoding
from crm.utils.helpers import get_crmimap
from massmail.models import EmailAccount

not_enough_data_str = _("Not enough data to identify the "
                        "email or email has been deleted")
something_wrong_str = _("Something went wrong")


def view_original_email(request: WSGIRequest, object_id=None, ea_id=None, uid=None):  
    ea, eml, uid, err = get_ea_eml_uid(object_id, ea_id, uid)
    if not err:
        box = 'INBOX' if ea_id or eml.incoming else 'Sent'
        crmimap = get_crmimap(ea, box)
        err = something_wrong_str
        if crmimap:
            result, data, err = crmimap.uid_fetch(str(uid).encode('utf8'), '(BODY[])')
            if result != 'OK' and not err or not data[0]:
                err = not_enough_data_str
            elif result == 'OK' and not err:
                b_msg = parse_message_bytes(uid, data)
                if b_msg:
                    msg = email.message_from_bytes(b_msg, policy=policy.default)
                    if object_id and eml.message_id != '':
                        err = update_eml_uid(eml, msg, crmimap)     # run crmimap.release()
                    else:
                        crmimap.release()
                    if not err:
                        context, err = get_context(msg)
                        if not err:
                            return render(request, 'crm/email.html', context)
                err = something_wrong_str
            crmimap.release()
    return HttpResponse(f"Error: {err}")    


def get_context(msg: Message):
    attachments = []
    body = err = ''
    context = {}
    try:
        simplest = msg.get_body(preferencelist=('html', 'plain'))
        if simplest:
            body = body or simplest.get_content()
            if simplest['content-type'] and simplest['content-type'].maintype == 'text':
                if simplest['content-type'].subtype == 'plain':
                    body = linebreaks(body)

        if msg.is_multipart():
            for richest in msg.walk():

                if richest.get_content_maintype() != 'multipart' and \
                        richest.get('Content-Disposition') is not None:
                    filename = richest.get_filename()
                    if filename and richest.get_content_disposition() == 'attachment':
                        attachments.append(filename)

                elif getattr(richest['content-type'], 'content_type', None) == 'multipart/related':
                    for part in richest.iter_attachments():
                        filename = part.get_filename()
                        if filename:
                            extension = os.path.splitext(part.get_filename())[1]
                        else:
                            extension = mimetypes.guess_extension(part.get_content_type())
                        encoding = part.get('Content-Transfer-Encoding')
                        src = f"cid:{part.get('Content-ID').strip('<, >')}"
                        if part.get('Content-ID'):
                            if encoding == 'base64':
                                payload = part.get_payload()
                            else:
                                payload = b64encode(part.get_payload(decode=True)).decode()
                            new_src = f'data:{filename}/{extension};base64,{payload}'
                            body = body.replace(src, new_src)
        context['from_field'] = msg['From']
        context['date'] = msg['Date']
        context['to'] = msg['To']
        context['cc'] = msg['CC']
        context['subject'] = ensure_decoding(msg['Subject'])
        context['body'] = mark_safe(body)
        context['attachments'] = attachments
    except Exception as e:
        err = e
    return context, err


def get_ea_eml_uid(object_id: int, ea_id, uid: Optional[int]) -> tuple:
    ea = eml = err = None
    if object_id:   # crmemail.id
        eml = CrmEmail.objects.get(id=object_id)
        uid = eml.uid
        ea = EmailAccount.objects.filter(email_host_user=eml.email_host_user).first()
    elif ea_id:
        ea = EmailAccount.objects.get(id=ea_id)
    if not ea:
        err = OBJ_DOESNT_EXIT_STR.format(
            EmailAccount._meta.verbose_name, ea_id  # NOQA
        )
    return ea, eml, uid, err
        
        
def parse_message_bytes(uid: int, data: list) -> Optional[bytes]:
    tmpl = f"UID {uid}".encode('utf8')
    return next((
        x[1] for x in data
        if type(x) is tuple and tmpl in x[0] and b"BODY[]" in x[0]
    ), None)    


def update_eml_uid(eml: CrmEmail, msg: Message, crmimap: CrmIMAP) -> str:
    """Update the uid value of the email message. Run crmimap.release()"""
    err = ''
    if eml.message_id != msg['Message-ID']:
        result, data, err = crmimap.search(f'(HEADER Message-ID "{eml.message_id}")')
        crmimap.release()
        if result == 'OK':
            uids = data[0].split()
            if uids:
                eml.uid = int(uids[0])
                eml.save(update_fields=['uid'])
        else:
            if not err:
                err = not_enough_data_str
    else:
        crmimap.release()
    return err
