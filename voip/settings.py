

SECRET_ZADARMA_KEY = '123'
SECRET_ZADARMA = 'secret'
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
