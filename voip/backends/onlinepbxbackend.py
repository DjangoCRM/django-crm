# -*- coding: utf-8 -*-
"""
OnlinePBX HTTP API client (scaffold)

Docs spec discovered at https://api.onlinepbx.ru (spec-url=api-scheme.yaml)
Execution server base URL: https://api2.onlinepbx.ru

Auth flow:
- POST /{domain}/auth.json with form field auth_key (and new=true) to obtain key_id and key
- Subsequent requests: header x-pbx-authentication: "{key_id}:{key}"
- Recommended headers: Content-Type: application/x-www-form-urlencoded, Content-MD5 (MD5 of body), x-pbx-date (ms timestamp)

This client provides minimal endpoints used in this project:
- call_now (/{domain}/call/now.json)
- call_instantly (/{domain}/call/instantly.json)
- search_history (/{domain}/mongo_history/search.json) with optional download

NOTE: This is a scaffold. Adjust error handling and extend endpoints as needed.
"""
from __future__ import annotations

import hashlib
import time
from typing import Dict, Optional, Any

import requests


class OnlinePBXAPI:
    def __init__(
        self,
        domain: str,
        key_id: Optional[str] = None,
        key: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: str = "https://api2.onlinepbx.ru",
        use_base64_md5: bool = False,
        session: Optional[requests.Session] = None,
    ) -> None:
        """
        :param domain: your onlinePBX domain, e.g. example.onpbx.ru
        :param key_id: identifier issued by auth
        :param key: secret issued by auth
        :param api_key: one-time API key used to obtain key_id/key
        :param base_url: API host (execution is on api2.onlinepbx.ru)
        :param use_base64_md5: if True, Content-MD5 is base64(md5(body)), otherwise hex digest
        :param session: optional requests.Session
        """
        self.domain = domain.strip()
        self.key_id = key_id
        self.key = key
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.use_base64_md5 = use_base64_md5
        self.http = session or requests.Session()

    # --------------- helpers ---------------
    def _url(self, path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path
        return f"{self.base_url}/{self.domain}{path}"

    @staticmethod
    def _now_ms() -> int:
        return int(time.time() * 1000)

    def _content_md5(self, body: str) -> str:
        m = hashlib.md5()
        m.update(body.encode("utf-8"))
        digest = m.digest()
        if self.use_base64_md5:
            import base64
            return base64.b64encode(digest).decode("ascii")
        return m.hexdigest()

    def _headers(self, body: str, extra: Optional[Dict[str, str]] = None, content_type: str = "application/x-www-form-urlencoded") -> Dict[str, str]:
        headers = {
            "Content-Type": content_type,
            "Content-MD5": self._content_md5(body or ""),
            "x-pbx-date": str(self._now_ms()),
        }
        if self.key_id and self.key:
            headers["x-pbx-authentication"] = f"{self.key_id}:{self.key}"
        if extra:
            headers.update(extra)
        return headers

    def _request(self, method: str, path: str, *, form: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        method = method.upper()
        url = self._url(path)
        if params:
            # requests will append params to URL
            pass
        if json_data is not None:
            import json as _json
            body_str = _json.dumps(json_data, separators=(",", ":"))
            headers = self._headers(body_str, content_type="application/json")
            return self.http.request(method, url, data=body_str, headers=headers, params=params)
        else:
            encoded = requests.models.RequestEncodingMixin._encode_params(form or {})
            headers = self._headers(encoded, content_type="application/x-www-form-urlencoded")
            return self.http.request(method, url, data=encoded, headers=headers, params=params)

    # --------------- public API ---------------
    def auth(self, auth_key: Optional[str] = None, force_new: bool = True) -> Dict[str, Any]:
        """
        Obtain (key_id, key) by API key.
        :param auth_key: if None, will use self.api_key
        :param force_new: include new=true
        """
        auth_key = auth_key or self.api_key
        if not auth_key:
            raise ValueError("auth_key is required to request OnlinePBX credentials")
        body_kv = [
            ("auth_key", auth_key),
        ]
        if force_new:
            body_kv.append(("new", "true"))
        body = "&".join(f"{k}={requests.utils.quote(str(v))}" for k, v in body_kv)
        url = self._url("/auth.json")
        resp = self.http.post(url, data=body, headers=self._headers(body))
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") == "1" and isinstance(data.get("data"), dict):
            creds = data["data"]
            self.key_id = creds.get("key_id") or self.key_id
            self.key = creds.get("key") or self.key
        return data

    def call_now(self, from_num: str, to_num: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Initiate a call: POST /{domain}/call/now.json
        Required: from, to
        Optional kwargs: gate_from, gate_to, to_domain, from_orig_number, from_orig_name
        """
        form = {"from": str(from_num), "to": str(to_num)}
        form.update({k: v for k, v in kwargs.items() if v is not None})
        resp = self._request("POST", "/call/now.json", form=form)
        resp.raise_for_status()
        return resp.json()

    def call_instantly(self, from_num: str, to_num: str, **kwargs: Any) -> Dict[str, Any]:
        form = {"from": str(from_num), "to": str(to_num)}
        form.update({k: v for k, v in kwargs.items() if v is not None})
        resp = self._request("POST", "/call/instantly.json", form=form)
        resp.raise_for_status()
        return resp.json()

    def search_history(self, **filters: Any) -> Dict[str, Any]:
        """
        Search in calls history: POST /{domain}/mongo_history/search.json
        Provide at least one filter: e.g., start_stamp_from, uuid, phone_numbers, etc.
        To get download link for a specific call, add download=1 and uuid.
        """
        if not filters:
            raise ValueError("At least one filter is required for history search")
        resp = self._request("POST", "/mongo_history/search.json", form=filters)
        resp.raise_for_status()
        return resp.json()

    # Simple convenience for getting download link by uuid
    def get_record_download_link(self, uuid: str) -> Optional[str]:
        data = self.search_history(uuid=uuid, download=1)
        if data.get("status") == "1":
            return data.get("data")
        return None

    # Compatibility with existing callback workflow
    def make_query(self, from_num: str, to_num: str, **kwargs: Any) -> str:
        """
        Proxy to call_now and return JSON text to match existing callers
        (Zadarma backend returns response.text)
        """
        import json as _json
        res = self.call_now(from_num, to_num, **kwargs)
        return _json.dumps(res)

    # ---------------- Management endpoints (Users, Groups, Queues, IVR, Blocklist) ----------------
    # Users
    def user_add(self, **fields: Any) -> Dict[str, Any]:
        return self._request("POST", "/user/add.json", form=fields).json()

    def user_edit(self, **fields: Any) -> Dict[str, Any]:
        return self._request("POST", "/user/edit.json", form=fields).json()

    def user_get(self, **filters: Any) -> Dict[str, Any]:
        return self._request("POST", "/user/get.json", form=filters).json()

    def user_flush_sip(self, **fields: Any) -> Dict[str, Any]:
        return self._request("POST", "/user/flush-sip", form=fields).json()

    # Groups
    def group_add(self, **fields: Any) -> Dict[str, Any]:
        return self._request("POST", "/group/add.json", form=fields).json()

    def group_edit(self, **fields: Any) -> Dict[str, Any]:
        return self._request("POST", "/group/edit.json", form=fields).json()

    def group_get(self, **filters: Any) -> Dict[str, Any]:
        return self._request("POST", "/group/get.json", form=filters).json()

    def group_remove(self, **fields: Any) -> Dict[str, Any]:
        return self._request("POST", "/group/remove.json", form=fields).json()

    # Queues (FIFO)
    def fifo_add(self, **fields: Any) -> Dict[str, Any]:
        return self._request("POST", "/fifo/add.json", form=fields).json()

    def fifo_edit(self, **fields: Any) -> Dict[str, Any]:
        return self._request("POST", "/fifo/edit.json", form=fields).json()

    def fifo_get(self, **filters: Any) -> Dict[str, Any]:
        return self._request("POST", "/fifo/get.json", form=filters).json()

    # IVR
    def ivr_get(self, **params: Any) -> Dict[str, Any]:
        # IVR GET is a RESTful collection under /ivr, using GET with query params
        url = self._url("/ivr")
        resp = self.http.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    def ivr_create(self, **payload: Any) -> Dict[str, Any]:
        return self._request("POST", "/ivr", json_data=payload).json()

    def ivr_update(self, **payload: Any) -> Dict[str, Any]:
        return self._request("PATCH", "/ivr", json_data=payload).json()

    def ivr_delete(self, **payload: Any) -> Dict[str, Any]:
        # Spec shows requestBody for DELETE /ivr
        return self._request("DELETE", "/ivr", json_data=payload).json()

    # Blocklist
    def blocklist_get(self, **params: Any) -> Dict[str, Any]:
        url = self._url("/blocklist")
        resp = self.http.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    def blocklist_add_contacts(self, **payload: Any) -> Dict[str, Any]:
        return self._request("POST", "/blocklist/contact", json_data=payload).json()

    def blocklist_remove_contacts(self, **payload: Any) -> Dict[str, Any]:
        return self._request("DELETE", "/blocklist/contact", json_data=payload).json()

