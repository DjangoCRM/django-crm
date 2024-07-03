import email
import time
import threading
from datetime import timedelta
from email.parser import BytesHeaderParser
from pathlib import Path
from typing import Optional
from django.apps import apps
from django.conf import settings
from django.core.mail import mail_admins
from django.core.paginator import EmptyPage
from django.core.paginator import InvalidPage
from django.core.paginator import Paginator
from django.utils import timezone
from django.utils.translation import gettext 
from django.utils.safestring import mark_safe
from django.urls import reverse

from common.utils.helpers import popup_window
from crm.models import CrmEmail
from crm.utils.crm_imap import CrmIMAP
from crm.utils.helpers import ensure_decoding
from crm.utils.helpers import get_crmimap
from crm.utils.helpers import get_email_date
from crm.utils.helpers import get_uid_data
from massmail.models import EmailAccount

app_config = apps.get_app_config('crm')
control_period = timedelta(seconds=120)


class ImportEmails(threading.Thread):

    def __init__(self, ea_queue, eml_queue): 
        threading.Thread.__init__(self)
        self.daemon = True
        self.close = False
        self.crmimap_storage = app_config.mci.crmimap_storage
        self.ea_queue = ea_queue
        self.eml_queue = eml_queue

    def send(self, user):
        eas = EmailAccount.objects.filter(
            do_import=True, owner=user,
        )
        for ea in eas:
            if not settings.REUSE_IMAP_CONNECTION or \
                    ea.email_host_user not in self.crmimap_storage:
                if ea not in list(self.ea_queue.queue):
                    self.ea_queue.put(ea)

    def run(self):
        if not settings.TESTING:
            path = Path(settings.MEDIA_ROOT / 'locks')
            try:
                path.mkdir(mode=0o775)
            except FileExistsError:
                for child in path.glob('*'):
                    child.unlink()
        crmimap = ea = None
        while True:
            try:
                if crmimap:
                    crmimap.release()
                    crmimap = None
                ea = self.ea_queue.get()
                if not settings.TESTING:
                    # To prevent hit the db until the apps.ready() is completed.
                    time.sleep(1)
                    ea.refresh_from_db(fields=['last_import_dt'])
                    now = timezone.now()
                    if ea.last_import_dt > now - control_period:
                        continue

                    ea.last_import_dt = now
                    ea.save(update_fields=['last_import_dt'])
                    crmimap = get_crmimap(ea)
                    if not crmimap or crmimap.error:
                        continue

                    upd_fields = []
                    uid_data = get_uid_data(ea)

                    for t in ('incoming', 'sent'):
                        box = 'Sent' if t == 'sent' else 'INBOX'
                        result = crmimap.select_box(box)
                        if result != 'OK':
                            continue

                        changed, uid_validity = crmimap.check_box_status(box, upd_fields)
                        if not changed:
                            continue
                        if not uid_validity:
                            set_new_start_uid(crmimap, t)

                        result, data, e = crmimap.search(uid_data[t]['search_params'])
                        if result != 'OK':
                            continue

                        # result <class 'list'>: [b'[CANNOT] Unsupported search criterion:
                        # SENTSINCE 08-MAY-2020 FLAGGED']
                        uids = data[0].split()
                        if not uids:
                            continue

                        for i, uid in enumerate(uids):
                            result, data, e = crmimap.uid_fetch(uid)
                            if result != 'OK' or not data[0]:
                                continue

                            b_msg = parse_message_bytes(uid, data)
                            if not b_msg:
                                result, data, err = crmimap.uid_fetch(uid)
                                if result != 'OK' or not data[0]:
                                    continue
                                b_msg = parse_message_bytes(uid, data)
                                if not b_msg:
                                    continue

                            if not uid_validity:
                                email_message = email.message_from_bytes(
                                    b_msg, policy=email.policy.default)
                                if CrmEmail.objects.filter(
                                    message_id=email_message['Message-ID'],
                                    creation_date=get_email_date(email_message)
                                ).exists():
                                    continue

                            self.eml_queue.put((b_msg, ea, t, uid, '', None))
                            if i == 50:
                                break

                    ea.last_import_dt = timezone.now()
                    upd_fields.append('last_import_dt')
                    ea.save(update_fields=upd_fields)

            except Exception as e:
                mail_admins(
                    'ImportEmails Exception',
                    f'\nEmail account: {ea}\nException: {e}',
                    fail_silently=True,
                )


def get_email_headers_page(ea: EmailAccount, page_num) -> tuple:
    unseen_list, emails, uids_str, err = [], [], '', ''
    page = paginator = None
    per_page = 40
    if not settings.TESTING:
        crmimap = get_crmimap(ea, 'INBOX')
        if crmimap.error:
            crmimap.release()
            return page, crmimap.error

        # Unfortunately, the SORT command is not supported by all servers
        # result, data = imap.uid('SORT', '(REVERSE ARRIVAL)', 'UTF-8', 'All')
        result, data, err = crmimap.search('UNSEEN')
        if result != 'OK':
            crmimap.release()
            return data, err
        if data:
            unseen_list = data[0].split()
        result, data, err = crmimap.search('All')

        if result != 'OK':
            crmimap.release()
            return data, err
        if data:
            if data != [b'']:
                uid_list = data[0].split()
                uid_list.sort(key=lambda x: int(x), reverse=True)
            else:
                uid_list = []
            paginator = Paginator(uid_list, per_page)
            try:
                page = paginator.get_page(page_num + 1)  # uids
            except (EmptyPage, InvalidPage):
                page = paginator.page(paginator.num_pages)
            uids_str = b','.join(page)

        if uids_str:
            result, data, err = crmimap.uid_fetch(uids_str, '(BODY.PEEK[HEADER])')
            crmimap.release()
            if result == 'OK' and data:
                # emails = []
                parser = BytesHeaderParser(policy=email.policy.compat32)
                for item in data:
                    if isinstance(item, tuple):
                        uid = item[0].split(b'UID ')[1].split()[0]
                        msg = parser.parsebytes(item[1])
                        subject = ensure_decoding(msg["Subject"])
                        subject = subject if subject else gettext('No subject')
                        date = get_email_date(msg)
                        url = reverse('view_original_email_uid', args=(ea.id, int(uid)))
                        win_id = 'Window' + uid.decode()
                        onclick = popup_window(url, win_id)
                        subject_str = mark_safe(
                            f'<a href="#" onClick="{onclick}">{subject}</a>'
                        )
                        is_exists = CrmEmail.objects.filter(
                            incoming=True,
                            creation_date=date,
                            email_host_user=ea.email_host_user
                        ).exists()
                        emails.append({
                            'subject': subject_str,
                            'from': ensure_decoding(msg['From']),
                            'to': ensure_decoding(msg['To']),
                            'date': date,
                            'uid': int(uid),
                            'is_exists': is_exists,
                            'unseen': uid in unseen_list
                        })
                    emails.sort(key=lambda x: x['uid'], reverse=True)
            else:
                crmimap.release()
    else:
        paginator = Paginator([], per_page)
        page = paginator.get_page(page_num + 1)
    page.object_list = emails
    page.result_count = paginator.count
    return page, err


def set_new_start_uid(crmimap: CrmIMAP, t: str) -> None:
    start_uid = None
    crm_emails = CrmEmail.objects.exclude(message_id='').filter(
        sent=t == 'sent',
        incoming=t == 'incoming',
        email_host_user=crmimap.ea.email_host_user,
        uid__isnull=False
    ).only('uid', 'message_id')[:3]
    for eml in crm_emails:
        result, data, _ = crmimap.search(f'(HEADER Message-ID "{eml.message_id}")')
        if result != 'OK':
            continue
        uids = data[0].split()
        if not uids:
            continue
        start_uid = uids[0]
        eml.uid = start_uid
        eml.save(update_fields=['uid'])
        break
    if not start_uid:
        start_uid = getattr(crmimap.ea, f"start_{t}_uid") - 50
        if start_uid <= 0:
            start_uid = 1
    setattr(crmimap.ea, f"start_{t}_uid", int(start_uid))


def parse_message_bytes(uid: bytes, data: list) -> Optional[bytes]:
    tmpl = f"UID {uid.decode()} RFC822".encode('utf8')
    b_msg = next((
        x[1] for x in data if type(x) is tuple and tmpl in x[0]
    ), None)
    if type(b_msg) is int:  # FIXME: fix and remove
        mail_admins(
            f"The data[0][1] is int at _parse_message_bytes(",
            f'''
            \nData: {data}
            \nb_msg: {b_msg}
            ''',
            fail_silently=True,
        )
        b_msg = None
    return b_msg
