"""Centralized OAuth2 token exchange for mailbox providers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests
from django.conf import settings

from sharedkernel.credentials import OAuthCredentials, OAuthTokenExchangeError

DEFAULT_TIMEOUT_SECONDS = 30


@dataclass(frozen=True)
class OAuthTokenResponse:
    access_token: str
    refresh_token: str | None = None
    expires_in: int | None = None


def exchange_refresh_token(credentials: OAuthCredentials) -> OAuthTokenResponse:
    return _exchange_token(
        credentials,
        {
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'refresh_token': credentials.refresh_token,
            'grant_type': 'refresh_token',
        },
    )


def exchange_authorization_code(
    credentials: OAuthCredentials,
    *,
    authorization_code: str,
    redirect_uri: str,
) -> OAuthTokenResponse:
    return _exchange_token(
        credentials,
        {
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scope': credentials.scope,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'code': authorization_code,
            'grant_type': 'authorization_code',
        },
    )


def _exchange_token(
    credentials: OAuthCredentials,
    params: dict[str, Any],
) -> OAuthTokenResponse:
    timeout = getattr(settings, 'OAUTH2_REQUEST_TIMEOUT', DEFAULT_TIMEOUT_SECONDS)
    try:
        response = requests.post(
            credentials.token_endpoint,
            params,
            timeout=timeout,
        )
    except requests.Timeout as err:
        raise OAuthTokenExchangeError(0, 'timeout') from err
    except (requests.RequestException, OSError) as err:
        raise OAuthTokenExchangeError(0, 'transport_error') from err

    payload = _parse_json_response(response)
    provider_error = payload.get('error')
    if provider_error or response.status_code >= 400:
        raise OAuthTokenExchangeError(
            response.status_code,
            str(provider_error or 'http_error'),
        )

    access_token = payload.get('access_token')
    if not access_token:
        raise OAuthTokenExchangeError(
            response.status_code,
            'missing_access_token',
        )

    return OAuthTokenResponse(
        access_token=access_token,
        refresh_token=payload.get('refresh_token'),
        expires_in=payload.get('expires_in'),
    )


def _parse_json_response(response: requests.Response) -> dict[str, Any]:
    try:
        payload = response.json()
    except ValueError as err:
        raise OAuthTokenExchangeError(
            response.status_code,
            'invalid_json',
        ) from err
    if not isinstance(payload, dict):
        raise OAuthTokenExchangeError(response.status_code, 'invalid_json')
    return payload
