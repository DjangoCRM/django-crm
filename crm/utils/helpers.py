import re
from datetime import datetime
from datetime import timezone as tz
from datetime import timedelta
from email.header import decode_header
from email.header import make_header
from email.message import Message
from email.utils import parsedate_to_datetime
from email.utils import parseaddr
from typing import Optional, Tuple
from django import forms
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import CharField
from django.db.models import F
from django.db.models import Value
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe, SafeString
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy

from common.utils.helpers import USER_MODEL, get_active_users
from crm.utils.crm_imap import CrmIMAP
from massmail.models import EmailAccount
from settings.models import BannedCompanyName
from settings.models import PublicEmailDomain
from settings.models import StopPhrase

NO_DEAL_AMOUNT_STR = gettext_lazy("No deal amount")
PHONE_NUMBER_MSG = gettext_lazy("Unacceptable phone number value")
counterparty_str = gettext_lazy('Counterparty')
counterparty_safe_icon = mark_safe(
    f'<i class="material-icons" title="{counterparty_str}"'
    f'style="color: var(--body-quiet-color)">business</i>'
)


class DateForm(forms.Form):
    birth_date = forms.DateField()


def add_id_to_raw_id_field_label(admin_obj, form) -> None:
    for field in admin_obj.raw_id_fields:
        if field in form.base_fields:
            label = form.base_fields[field].label
            form.base_fields[field].label = f"{label}, ID"


def delete3enters(text):
    text = re.sub(r"[\xc2\xa0\x8b]|cid:[a-zA-Z0-9.@]+", '', text)
    return re.sub(r"[\r\n]+\s+[\r\n]+", '\r\n\r\n', text)


def ensure_decoding(string):
    if string is None:
        return ''
    try:
        # It does not work correctly with all possible emails subject.
        return str(make_header(decode_header(string)))
    except Exception:   # NOQA
        return string


def get_counterparty_header() -> SafeString:
    return counterparty_safe_icon


def get_crmimap(ea: EmailAccount, box: Optional[str] = None) -> Optional[CrmIMAP]:
    app_config = apps.get_app_config('crm')
    return app_config.mci.get_crmimap(ea, box)    
    

def get_email_date(msg: Message) -> datetime:
    if msg['Date']:
        eml_date = parsedate_to_datetime(msg['Date'])
    elif msg['Delivery-date']:
        eml_date = parsedate_to_datetime(msg['Delivery-date'])
    else:
        eml_date = timezone.now()
    if timezone.is_naive(eml_date):
        eml_date = eml_date.replace(tzinfo=tz.utc)
    return eml_date


def get_email_domain(email: str) -> str:
    _, email = parseaddr(email)
    try:
        domain = email.split('@')[1]
        domain = domain.lower()
    except IndexError:
        return ''
    if PublicEmailDomain.objects.filter(domain=domain).exists():
        return ''
    return domain


def resolve_lead_source_by_email_to(to_addr: str):
    """Try to resolve LeadSource by recipient email address."""
    LeadSource = apps.get_model('crm', 'LeadSource')
    _, email_to_addr = parseaddr(to_addr or '')
    if not email_to_addr:
        return None
    return LeadSource.objects.filter(email__iexact=email_to_addr).first()


def assign_request_owner_by_department(request_obj) -> None:
    """Assign an owner to a Request based on department managers.
    If the lead_source has a department, prefer its managers; otherwise
    fallback to the request department. Leaves owner unchanged if already set.
    """
    if getattr(request_obj, 'owner', None):
        return
    dept = None
    if getattr(request_obj, 'lead_source', None) and request_obj.lead_source:
        dept = request_obj.lead_source.department
    if not dept and getattr(request_obj, 'department', None):
        dept = request_obj.department
    if not dept:
        return
    # Pick the first active manager in this department
    managers = get_active_users().filter(groups__in=[dept], groups__name='managers')
    owner = managers.first()
    if owner:
        request_obj.owner = owner


def ensure_request_sla_reminder(request_obj, hours: int = 4) -> None:
    """Create a Reminder as an SLA target for first response.
    Does nothing if the request already has any reminders.
    """
    Reminder = apps.get_model('common', 'Reminder')
    if Reminder.objects.filter(
        content_type__model=request_obj._meta.model_name,
        object_id=request_obj.pk
    ).exists():
        return
    from django.utils.timezone import now
    reminder_date = now() + timedelta(hours=hours)
    subject = _('First response due')
    description = _('Auto-created SLA for first response time')
    Reminder.objects.create(
        content_object=request_obj,
        subject=subject,
        description=description,
        reminder_date=reminder_date,
        owner=getattr(request_obj, 'owner', None),
        send_notification_email=True,
    )


def get_products_header() -> SafeString:
    return mark_safe(
        f'<i class="material-icons" title={_("Products")}'
        f' style="color: var(--body-quiet-color)">shopping_cart</i>'
    )


def get_owner(request: WSGIRequest, username: str):
    if username:
        try:
            value = USER_MODEL.objects.get(username=username)
        except ObjectDoesNotExist:
            value = None
    else:
        if request.user.is_superuser:
            value = None
        else:
            value = request.user
    return value


def get_owner_header() -> SafeString:
    return mark_safe(
        f'<i class="material-icons" title={_("Owner")}'
        f' style="color: var(--body-quiet-color)">person</i>'
    )


def get_uid_data(ea: EmailAccount) -> dict:
    return {
        'incoming': {
            'incoming': True,
            'sent': False,
            'search_params': f'(TEXT "[ticket:" UID {ea.start_incoming_uid}:*)',
            'start_uid': 'start_incoming_uid'
        },
        'sent': {
            'incoming': False,
            'sent': True,
            'search_params': f'(TEXT "[ticket:" UID {ea.start_sent_uid}:*)',
            'start_uid': 'start_sent_uid'
        }
    }


def html2txt(html: str) -> str:
    html = html.replace('&lt;', '<')
    html = html.replace('&gt;', '>')
    html = html.replace('&apos;', "'")
    html = html.replace('&quot;', '"')
    html = html.replace('&nbsp;', " ")
    html = html.replace(u'\xa0', " ")
    html = re.sub(r'\r\n\s?', '', html)
    html = re.sub(r'<br\s?/?>|</p>|</div>', '\r\n', html)
    return delete3enters(strip_tags(html).strip())


def is_company_banned(data: dict) -> bool:
    return BannedCompanyName.objects.annotate(
                company=Value(data['company'], CharField())
            ).filter(
        company__icontains=F('name')
    ).exists()


def is_text_relevant(txt: str) -> bool:
    for sp in StopPhrase.objects.all():
        if txt.find(sp.phrase) != -1:
            sp.hit()
            return False
    return True


def phone_number_check(phone: str) -> None:
    if phone:
        digits = [i for i in phone if i.isdigit()]
        if len(digits) < 7:
            raise forms.ValidationError(
                PHONE_NUMBER_MSG, code='invalid'
            )
