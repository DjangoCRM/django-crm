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


def eskiz_send_sms(token: str, from_name: str, phone: str, text: str):
    """Return tuple: (ok: bool, provider_id: str|None, raw: dict|None)."""
    if EskizSMS and token:
        try:
            client = EskizSMS(token=token)
            resp = client.send_message(phone, text, from_name or '4546')
            ok = bool(resp)
            provider_id = None
            raw = resp if isinstance(resp, dict) else None
            if isinstance(resp, dict):
                provider_id = resp.get('message_id') or resp.get('id') or resp.get('message')
            return ok, provider_id, raw
        except Exception as e:
            return False, None, {'error': str(e)}
    # Fallback to raw HTTP
    try:
        headers = {'Authorization': f'Bearer {token}'}
        payload = {
            'mobile_phone': phone,
            'message': text,
            'from': from_name or '4546',
        }
        resp = requests.post('https://notify.eskiz.uz/api/message/sms/send', headers=headers, data=payload, timeout=10)
        ok = resp.status_code in (200, 202)
        provider_id = None
        raw = None
        try:
            raw = resp.json()
            provider_id = raw.get('message_id') or raw.get('id')
        except Exception:
            raw = {'status_code': resp.status_code, 'text': resp.text[:500]}
        return ok, provider_id, raw
    except Exception as e:
        return False, None, {'error': str(e)}


def playmobile_send_sms_basic(api_url: str, login: str, password: str, from_name: str, phone: str, text: str):
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
        ok = resp.status_code in (200, 202)
        provider_id = None
        raw = None
        try:
            raw = resp.json()
            provider_id = raw.get('message_id') or raw.get('id')
        except Exception:
            raw = {'status_code': resp.status_code, 'text': resp.text[:500]}
        return ok, provider_id, raw
    except Exception:
        return False, None, None


def playmobile_send_sms_token(api_url: str, token: str, from_name: str, phone: str, text: str):
    try:
        url = api_url or 'https://api.playmobile.uz/v1/messages'
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        payload = {
            'from': from_name,
            'to': phone,
            'text': text,
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        ok = resp.status_code in (200, 202)
        provider_id = None
        raw = None
        try:
            raw = resp.json()
            provider_id = raw.get('message_id') or raw.get('id')
        except Exception:
            raw = {'status_code': resp.status_code, 'text': resp.text[:500]}
        return ok, provider_id, raw
    except Exception:
        return False, None, None
