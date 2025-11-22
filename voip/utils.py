from typing import Optional, Tuple

from django.db.models import Q
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db.utils import OperationalError, ProgrammingError

from common.utils.helpers import add_phone_q_params
from common.models import UserProfile
from crm.models import Contact
from crm.models import Deal
from crm.models import Lead

User = get_user_model()


def normalize_number(value: Optional[str]) -> str:
    """Return only digits from phone/extension strings."""
    return ''.join(ch for ch in (value or '') if ch.isdigit())


def find_objects_by_phone(phone: str) -> \
        Tuple[Optional[Contact], Optional[Lead], Optional[Deal], str]:
    """
    Search Contact, Lead and active Deal by phone number.

    Returns a tuple (contact, lead, deal, error_message).
    """
    params = contact = lead = deal = None
    q_params = add_phone_q_params(phone, Q())
    try:
        contact = Contact.objects.filter(q_params).first()
    except Exception as exc:
        return contact, lead, deal, str(exc)
    if contact:
        params = {'contact_id': contact.id, 'active': True}
    else:
        lead = Lead.objects.filter(q_params).first()
        if lead:
            params = {'lead_id': lead.id, 'active': True}
    if any((contact, lead)):
        deal = Deal.objects.filter(**params).order_by('-update_date').first()

    return contact, lead, deal, ''


def resolve_targets(extension: str, matched_obj) -> list[User]:
    """
    Try to map call to specific users by PBX extension.
    Fallback to the object's owner if no extension match.
    """
    users: list[User] = []
    ext_digits = normalize_number(extension)
    if ext_digits:
        profiles = UserProfile.objects.select_related('user').filter(
            pbx_number__isnull=False,
        )
        for profile in profiles:
            if not profile.pbx_number:
                continue
            if normalize_number(profile.pbx_number) == ext_digits:
                users.append(profile.user)

    if not users:
        owner = getattr(matched_obj, 'owner', None)
        if owner and owner.is_active:
            users.append(owner)

    return users


def _get_settings_instance():
    from voip.models import VoipSettings
    try:
        return VoipSettings.objects.first()
    except (OperationalError, ProgrammingError):
        return None


def load_asterisk_config():
    base = getattr(settings, 'ASTERISK_AMI', {})
    instance = _get_settings_instance()
    if instance:
        base = base | instance.ami_config
    return base


def load_incoming_ui_config():
    data = {
        'enabled': getattr(settings, 'VOIP_INCOMING_CALL_ENABLED', True),
        'poll_interval_ms': getattr(settings, 'VOIP_INCOMING_POLL_INTERVAL_MS', 4000),
        'popup_ttl_ms': getattr(settings, 'VOIP_INCOMING_POPUP_TTL_MS', 20000),
    }
    instance = _get_settings_instance()
    if instance:
        data = data | instance.incoming_ui_config
    return data
