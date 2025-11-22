

import os


def env_bool(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in ('1', 'true', 'yes', 'on')


def env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


SECRET_ZADARMA_KEY = '123'
SECRET_ZADARMA = 'secret'
ASTERISK_AMI = {
    'HOST': os.getenv('ASTERISK_AMI_HOST', '127.0.0.1'),
    'PORT': env_int('ASTERISK_AMI_PORT', 5038),
    'USERNAME': os.getenv('ASTERISK_AMI_USERNAME', 'admin'),
    'SECRET': os.getenv('ASTERISK_AMI_SECRET', 'your-ami-secret'),
    'USE_SSL': env_bool('ASTERISK_AMI_USE_SSL', False),
    'CONNECT_TIMEOUT': env_int('ASTERISK_AMI_CONNECT_TIMEOUT', 5),
    'RECONNECT_DELAY': env_int('ASTERISK_AMI_RECONNECT_DELAY', 5),
}
VOIP = [
    {
        'BACKEND': 'voip.backends.zadarmabackend.ZadarmaAPI',
        'PROVIDER': 'Zadarma',
        'IP': '185.45.152.42',
        'OPTIONS': {
            'key': SECRET_ZADARMA_KEY,
            'secret': SECRET_ZADARMA
        }
    }
]

VOIP_FORWARD_DATA = False
VOIP_FORWARDING_IP = ''


VOIP_FORWARD_URL = 'Url to forward'

VOIP_INCOMING_CALL_ENABLED = env_bool('VOIP_INCOMING_CALL_ENABLED', True)
VOIP_INCOMING_POLL_INTERVAL_MS = env_int('VOIP_INCOMING_POLL_INTERVAL_MS', 4000)
VOIP_INCOMING_POPUP_TTL_MS = env_int('VOIP_INCOMING_POPUP_TTL_MS', 20000)

# JsSIP client defaults (can be overridden via environment variables)
JSSIP_WS_URI = os.getenv('JSSIP_WS_URI', '')
JSSIP_SIP_URI = os.getenv('JSSIP_SIP_URI', '')
JSSIP_SIP_PASSWORD = os.getenv('JSSIP_SIP_PASSWORD', '')
JSSIP_DISPLAY_NAME = os.getenv('JSSIP_DISPLAY_NAME', '')
