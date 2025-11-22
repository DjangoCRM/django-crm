from __future__ import annotations

import requests
from typing import Optional


def eskiz_auth(email: str, password: str) -> Optional[str]:
    try:
        resp = requests.post('https://notify.eskiz.uz/api/auth/login', json={'email': email, 'password': password}, timeout=10)
        if resp.status_code == 200:
            return resp.json().get('data', {}).get('token')
    except Exception:
        return None
    return None


def eskiz_send_sms(token: str, from_name: str, phone: str, text: str) -> bool:
    try:
        headers = {'Authorization': f'Bearer {token}'}
        payload = {
            'mobile_phone': phone,
            'message': text,
            'from': from_name or '4546',
        }
        resp = requests.post('https://notify.eskiz.uz/api/message/sms/send', headers=headers, data=payload, timeout=10)
        return resp.status_code in (200, 202)
    except Exception:
        return False


def playmobile_send_sms(login: str, password: str, from_name: str, phone: str, text: str) -> bool:
    try:
        # Example endpoint; adjust to your PlayMobile provider
        url = 'https://send.smsxabar.uz/api/v1/send'
        payload = {
            'login': login,
            'password': password,
            'from': from_name,
            'to': phone,
            'text': text,
        }
        resp = requests.post(url, json=payload, timeout=10)
        return resp.status_code in (200, 202)
    except Exception:
        return False
