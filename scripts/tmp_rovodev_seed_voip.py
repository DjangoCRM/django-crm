import requests

BASE = 'http://localhost:8000'

# Zadarma-like webhook (adjust fields as your handler expects)
try:
    resp = requests.post(f'{BASE}/voip/webhook/', data={
        'event': 'NOTIFY_END',
        'caller_id': '+998901234567',
        'called_did': '100',
        'duration': '45',
        'call_id': 'demo-call-1',
    })
    print('Zadarma webhook:', resp.status_code, resp.text)
except Exception as e:
    print('Zadarma webhook error:', e)

# OnlinePBX webhook (adjust to your endpoint)
try:
    resp = requests.post(f'{BASE}/voip/onlinepbx/webhook/', json={
        'caller': '+998909998877',
        'duration': 30,
        'uuid': 'demo-pbx-1',
        'ext': '101'
    })
    print('OnlinePBX webhook:', resp.status_code, resp.text)
except Exception as e:
    print('OnlinePBX webhook error:', e)
