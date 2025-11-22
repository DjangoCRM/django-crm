from django.urls import reverse

from voip.utils import load_incoming_ui_config


def incoming_call(request):
    """
    Expose incoming-call polling config to templates for authenticated users.
    """
    if not request.user.is_authenticated:
        return {}

    cfg = load_incoming_ui_config()
    if not cfg.get('enabled'):
        return {}

    return {
        'incoming_call_poll_url': reverse('voip:voip_incoming_call_poll'),
        'incoming_call_poll_interval': cfg.get('poll_interval_ms', 4000),
        'incoming_call_popup_ttl': cfg.get('popup_ttl_ms', 20000),
    }
