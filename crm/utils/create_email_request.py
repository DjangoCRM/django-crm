import threading
from email.utils import parseaddr
from django.core.mail import mail_admins
from django.db import connection
from django.template.defaultfilters import truncatechars

from common.utils.copy_files import copy_files
from common.utils.parse_full_name import parse_full_name
from crm.models import LeadSource
from crm.models import CrmEmail
from crm.models import Request
from crm.site.requestadmin import notify_request_owners
from massmail.models import EmailAccount


class CreateEmailInquiry(threading.Thread):

    def __init__(self, inq_eml_queue, ):
        threading.Thread.__init__(self)
        self.daemon = True
        self.close = False
        self.inq_eml_queue = inq_eml_queue

    def send(self, item):
        self.inq_eml_queue.put(item)

    def finish_work(self):
        self.inq_eml_queue.put((None, None))

    def run(self):
        while True:
            email, frm, ea = self.inq_eml_queue.get()
            if email is None:
                break
            create_email_request(email, frm, ea)
            self.inq_eml_queue.task_done()
            connection.close()


def create_email_request(email: CrmEmail, frm: str = '', ea: EmailAccount = None) -> None:
    email_addr = ''
    try:
        realname, email_addr = parseaddr(frm if frm else email.from_field)
        first_name, middle_name, last_name = parse_full_name(realname)
        _, email_to_addr = parseaddr(email.to)
        lead_source = LeadSource.objects.filter(email=email_to_addr).first()
        r = Request(
            first_name=first_name,
            middle_name=middle_name,
            last_name=truncatechars(last_name, 90),
            email=email_addr,
            request_for=email.subject,
            description=email.content,
            department=email.department,
            receipt_date=email.creation_date.date(),
            lead_source=lead_source,
            owner=email.owner,
        )
        r.find_contact_or_lead()
        r.update_request_data()

        set_subsequent(r, email, ea)

        # set default country
        if email.department:
            r.country = email.department.department.default_country    # NOQA
        r.save()
        
        if r.owner:
            groups = r.owner.groups.values_list('name', flat=True)
            if 'managers' in groups:
                notify_request_owners(r)
        email.ticket = r.ticket
        email.request = r
        if r.contact:
            email.contact = r.contact
            email.company = r.contact.company
        email.lead = r.lead
        email.save(update_fields=[
            'ticket',
            'request',
            'contact',
            'company',
            'lead'
        ])
        copy_files(email, r)
    except Exception as e:
        mail_admins(
            'create_email_request exception',
            f'''
\nFrom: {email_addr}
\nSubject: {email.subject}
\nException: {e}''',
            fail_silently=True,
        )


def set_subsequent(obj: Request, email: CrmEmail, ea: EmailAccount = None) -> None:
    if obj.lead_source:
        return
    if ea:
        obj.subsequent = ea.owner.groups.filter(name='managers').exists()
        return
    obj.subsequent = email.owner.groups.filter(name='managers').exists()
