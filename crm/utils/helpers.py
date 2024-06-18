import re
from datetime import datetime
from datetime import timezone as tz
from email.header import decode_header
from email.header import make_header
from email.message import Message
from email.utils import parsedate_to_datetime
from email.utils import parseaddr
from typing import Optional
from django import forms
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
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

from common.utils.helpers import USER_MODEL
from crm.utils.crm_imap import CrmIMAP
from massmail.models import EmailAccount
from massmail.models import MassContact
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


def delete_rel_mc(obj) -> None:  # obj: Union[Company, Contact, Lead]
    """Delete related object"""
    content_type = ContentType.objects.get_for_model(obj)
    MassContact.objects.filter(
        content_type=content_type,
        object_id=obj.id,
    ).delete()


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
