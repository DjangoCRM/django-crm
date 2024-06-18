import random
import time
import threading
from datetime import timedelta
from email.errors import HeaderParseError
from typing import Union
from smtplib import SMTPAuthenticationError
from smtplib import SMTPDataError
from smtplib import SMTPRecipientsRefused
from smtplib import SMTPServerDisconnected
from smtplib import SMTPSenderRefused
from tendo.singleton import SingleInstance
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.mail import mail_admins
from django.core.mail.message import BadHeaderError
from django.db import connection
from django.utils import timezone
from django.contrib.sites.models import Site

from common.utils.helpers import get_now
from crm.models import Company
from crm.models import Contact
from crm.models import Lead
from massmail.settings import BUSINESS_TIME_START
from massmail.settings import BUSINESS_TIME_END
from massmail.settings import EMAILS_PER_DAY
from massmail.models import MailingOut
from massmail.models import MassContact
from massmail.models import EmailAccount
from massmail.models import EmlAccountsQueue
from .email_creators import email_creator

USER_MODEL = get_user_model()


class SendMassmail(threading.Thread, SingleInstance):

    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.daemon = True
        if settings.TESTING:
            SingleInstance.__init__(self, flavor_id='Massmail_test')
        else:
            SingleInstance.__init__(self, flavor_id='Massmail')

    def run(self):

        while True:
            
            if settings.DEBUG or settings.TESTING:
                break
            
            s = get_seconds_to_business_time()
            connection.close()
            time.sleep(s + random.randint(120, 300))
            
            send_massmail()


def send_massmail() -> None:
    try:
        mailing_outs = MailingOut.objects.filter(
            status__in=['A', 'E']
        ).order_by('?')
        if not mailing_outs:
            return
        
        now = get_now()
        today = now.date()
        mailing_outs = check_owners(mailing_outs)
        while mailing_outs:

            mailing_out = mailing_outs.pop(0)
            if mailing_out.sending_date != today:
                mailing_out.today_count = 0
            recipient_ids = get_recipient_ids(mailing_out)
            if not recipient_ids:
                continue
            fix_masscontacts(mailing_out, recipient_ids)
            email_accounts = EmailAccount.objects.filter(
                owner=mailing_out.owner,
                massmail=True
            )
            for email_account in email_accounts:
                if email_account.today_date == today:
                    if email_account.today_count > EMAILS_PER_DAY:
                        continue
                else:
                    email_account.today_count = 0
                mc = MassContact.objects.filter(
                    content_type=mailing_out.content_type,
                    object_id__in=recipient_ids,
                    email_account=email_account
                ).first()
                if not mc:
                    continue
                recipient = get_recipient(mailing_out, mc)
                if not recipient:
                    continue
                extra_context = get_extra_context(mc)
                to = extra_context['to'].split(',')
                try:
                    msg = email_creator(
                        mailing_out.message, email_account, to=to,
                        extra_context=extra_context,
                        force_multipart=True, inline_images=True
                    )
                    if not settings.DEBUG:
                        msg.send(fail_silently=False)
                    mailing_out.move_to_successful_ids(mc.object_id)
                except (SMTPAuthenticationError, SMTPSenderRefused) as e:
                    off = True
                    report(email_account, mailing_out, mc, now, e, off)
                    continue

                except (
                        SMTPDataError, BadHeaderError, SMTPRecipientsRefused,
                        SMTPServerDisconnected, IndexError, HeaderParseError,
                        FileNotFoundError
                ) as e:
                    report(email_account, mailing_out, mc, now, e)
                    continue

                except Exception as e:
                    report(email_account, mailing_out, mc, now, e)
                    continue

                counter_increment(email_account, mailing_out, today)

                if not any((settings.DEBUG, settings.TESTING)):
                    time.sleep(random.randint(5, 25))
    except Exception as err:
        msg = f"Exception at send_massmail"
        mail_admins(
            msg,
            f'''{msg}\n
            \nException:____{err}
            ''',
        )


def check_owners(mailing_outs) -> list:
    owner_list = []
    new_mailing_outs = []
    mailing_outs = list(mailing_outs)
    while mailing_outs:
        mo = mailing_outs.pop(0)
        if mo.owner not in owner_list:
            new_mailing_outs.append(mo)
            owner_list.append(mo.owner)
        
    return new_mailing_outs
        

def counter_increment(
        email_account: EmailAccount,
        mailing_out: MailingOut,
        today
) -> None:
    email_account.today_count += 1
    email_account.today_date = today
    email_account.save()
    mailing_out.today_count += 1
    mailing_out.sending_date = today
    mailing_out.save()


def get_recipient(
        mailing_out: MailingOut, mc: MassContact
) -> Union[Company, Contact, Lead]:
    recipient = mc.content_object
    if not recipient:
        mailing_out.remove_recipient_ids(mc.object_id)
        mailing_out.recipients_number -= 1
        mailing_out.save()
        mc.delete()
    return recipient


def get_recipient_ids(mailing_out: MailingOut) -> list:
    recipient_ids = mailing_out.get_recipient_ids()
    if not recipient_ids:
        report_msg = 'Done successfully.'
        mailing_out.report = report_msg + mailing_out.report
        mailing_out.status = 'D'
        mailing_out.save()
    return recipient_ids


def fix_masscontacts(mailing_out: MailingOut, recipient_ids: list) -> None:
    wrong_masscontacts = MassContact.objects.filter(
        content_type=mailing_out.content_type,
        object_id__in=recipient_ids,
    ).exclude(email_account__owner=mailing_out.owner)
    if wrong_masscontacts:
        queue_obj = EmlAccountsQueue.objects.get(owner=mailing_out.owner)
        for masscontact in wrong_masscontacts:
            email_account_id = queue_obj.get_next()
            if email_account_id:
                masscontact.email_account_id = email_account_id
                masscontact.save(update_fields=["email_account_id"])
    # set masscontact
    recipient_ids_with = MassContact.objects.filter(
        content_type=mailing_out.content_type,
        object_id__in=recipient_ids
    ).values_list('object_id', flat=True)
    recipient_ids_without = list(set(recipient_ids) - set(recipient_ids_with))
    if recipient_ids_without:
        queue_obj = EmlAccountsQueue.objects.get(owner=mailing_out.owner)
        for recipient_id in recipient_ids_without:
            email_account_id = queue_obj.get_next()
            if email_account_id:
                MassContact.objects.create(
                    content_type=mailing_out.content_type,
                    object_id=recipient_id,
                    email_account_id=email_account_id
                )


def get_seconds_to_business_time() -> float:
    now = timezone.localtime(timezone.now())
    bt_start = now.replace(
        hour=BUSINESS_TIME_START['hour'],
        minute=BUSINESS_TIME_START['minute']
    )
    bt_end = now.replace(
        hour=BUSINESS_TIME_END['hour'],
        minute=BUSINESS_TIME_END['minute']
    )
    weekday = now.weekday()
    if weekday in (4, 5, 6):
        days = 7 - weekday
        delta = timedelta(days=days)
        bt_start = bt_start + delta
        bt_end = bt_end + delta
    if bt_start > now:
        return (bt_start - now).total_seconds()
    elif now > bt_end:
        return (timedelta(hours=24) + bt_start - now).total_seconds()
    return 0


def report(
        email_account: EmailAccount,
        mailing_out: MailingOut,
        mc: MassContact, now, e, off=False):
    report_str = f"""
{now}
{e}
{mc.content_object}
{email_account.email_host_user}\r\n\r\n
"""
    email_account.report = report_str + email_account.report
    if off:
        email_account.massmail = False
        report_str = 'Account OFF!\r\n' + report_str
    email_account.save()
    mailing_out.report = report_str + mailing_out.report
    mailing_out.status = 'E'
    if off:
        mailing_out.save()
        subj = 'Massmail error: ' + f'{mc.content_object}'
        mail_admins(subj, mailing_out.report, fail_silently=True)
    else:
        mailing_out.move_to_failed_ids(mc.object_id)


def get_extra_context(mc: MassContact) -> dict:
    DATA = {
        ContentType.objects.get_for_model(Contact): [
            'email', 'first_name', 'first_middle_name',
            'last_name', 'full_name',
            'title', 'company'
        ],
        ContentType.objects.get_for_model(Company): [
            'email', 'full_name'
        ],
        ContentType.objects.get_for_model(Lead): [
            'email', 'first_name', 'first_middle_name',
            'last_name', 'full_name',
            'title', 'company_name'
        ]
    }
    url = reverse(
            'unsubscribe', args=[mc.uuid]
    )
    extra_context = {
        'unsubscribe_url': Site.objects.get(
            pk=settings.SITE_ID
        ).domain + url
    }
    fields = DATA[mc.content_type].copy()
    field = fields.pop(0)
    extra_context['to'] = getattr(mc.content_object, field)
    for field in fields:
        extra_context[field] = getattr(mc.content_object, field)
    return extra_context
