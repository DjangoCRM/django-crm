import json
import requests

BASE = 'http://localhost:8000'

# Seed SMS events (outbound)
SMS = [
    {"channel_id": 1, "to": "+998901234567", "text": "Hello from demo 1"},
    {"channel_id": 2, "to": "+998909876543", "text": "Hello from demo 2"},
]
for s in SMS:
    r = requests.post(f'{BASE}/integrations/sms/send/', json={**s, "async": False})
    print('SMS', s, '->', r.status_code, r.text)

# Seed VoIP webhook calls would go here; depends on your webhook security/signature.
# Example (adjust payload/route):
# requests.post(f'{BASE}/voip/onlinepbx/webhook/', json={"caller": "+998901112233", "duration": 45})
