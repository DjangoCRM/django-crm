from __future__ import annotations

import requests
try:
    from eskiz_sms.client import EskizSMS
except Exception:
    EskizSMS = None
from typing import Optional


def eskiz_auth(email: str, password: str) -> Optional[str]:
    if EskizSMS:
        try:
            client = EskizSMS(email=email, password=password)
            token = client.login()
            return token
        except Exception:
            return None
    # Fallback to raw HTTP
    try:
        resp = requests.post('https://notify.eskiz.uz/api/auth/login', json={'email': email, 'password': password}, timeout=10)
        if resp.status_code == 200:
            return resp.json().get('data', {}).get('token')
    except Exception:
        return None
    return None


def eskiz_send_sms(token: str, from_name: str, phone: str, text: str) -> bool:
    if EskizSMS and token:
        try:
            client = EskizSMS(token=token)
            resp = client.send_message(phone, text, from_name or '4546')
            return bool(resp)
        except Exception:
            return False
    # Fallback to raw HTTP
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


def playmobile_send_sms_basic(api_url: str, login: str, password: str, from_name: str, phone: str, text: str) -> bool:
    try:
        url = api_url or 'https://send.smsxabar.uz/api/v1/send'
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


def playmobile_send_sms_token(api_url: str, token: str, from_name: str, phone: str, text: str) -> bool:
    try:
        url = api_url or 'https://api.playmobile.uz/v1/messages'
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        payload = {
            'from': from_name,
            'to': phone,
            'text': text,
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        return resp.status_code in (200, 202)
    except Exception:
        return False
