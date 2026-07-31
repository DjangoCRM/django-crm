import secrets
from urllib.parse import urlencode

from django.conf import settings
from django.contrib import messages
from django.contrib.sites.models import Site
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.utils.translation import gettext as _
from django.urls import reverse

from massmail.models import EmailAccount
from sharedkernel.credentials import (
    CredentialAccessor,
    MissingOAuthConfigError,
    OAuthTokenExchangeError,
    resolve_for_user,
)
from sharedkernel.mail_diagnostics import report_mail_incident
from sharedkernel.oauth_exchange import exchange_authorization_code

OAUTH2_SESSION_KEY = 'massmail_oauth2_flow'


def get_redirect_uri(ea: EmailAccount) -> str:
    site = Site.objects.get_current()
    uri = reverse('get_refresh_token')
    return f"https://{site.domain}{uri}?user={ea.email_host_user}"


def request_authorization_code(request, email_account_id):
    try:
        ea = EmailAccount.objects.get(id=email_account_id)
        resolve_for_user(request.user, ea)
    except EmailAccount.DoesNotExist:
        return HttpResponseForbidden('Email account not found.')
    except PermissionDenied:
        return HttpResponseForbidden('You cannot authorize OAuth for this account.')

    data = settings.OAUTH2_DATA.get(ea.email_host)
    if not data:
        messages.error(
            request,
            'Settings are missing in settings.OAUTH2_DATA',
        )
        url = reverse('site:massmail_emailaccount_change', args=(ea.id,))
        return HttpResponseRedirect(url)

    state = secrets.token_urlsafe(32)
    request.session[OAUTH2_SESSION_KEY] = {
        'state': state,
        'account_id': ea.pk,
    }
    redirect_uri = get_redirect_uri(ea)
    params = {
        'client_id': settings.CLIENT_ID,
        'scope': data['scope'],
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'approval_prompt': 'force',
        'access_type': 'offline',
        'state': state,
    }
    permission_url = f"{data['accounts_base_url']}/{data['auth_command']}"
    return HttpResponseRedirect(permission_url + f'?{urlencode(params)}')


def get_refresh_token(request):
    flow = request.session.pop(OAUTH2_SESSION_KEY, None)
    state = request.GET.get('state')
    if not flow or not state or not secrets.compare_digest(flow['state'], state):
        return HttpResponseForbidden('Invalid OAuth state.')

    try:
        ea = EmailAccount.objects.get(pk=flow['account_id'])
        resolve_for_user(request.user, ea)
    except EmailAccount.DoesNotExist:
        return HttpResponseForbidden('Email account not found.')
    except PermissionDenied:
        return HttpResponseForbidden('You cannot authorize OAuth for this account.')

    authorization_code = request.GET.get('code')
    if not authorization_code:
        messages.warning(
            request,
            _('Error: Failed to get authorization code.'),
        )
        url = reverse('site:massmail_emailaccount_change', args=(ea.id,))
        return HttpResponseRedirect(url)

    redirect_uri = get_redirect_uri(ea)
    try:
        oauth_credentials = CredentialAccessor.get_oauth_credentials(ea)
        token_response = exchange_authorization_code(
            oauth_credentials,
            authorization_code=authorization_code,
            redirect_uri=redirect_uri,
        )
        if token_response.refresh_token:
            CredentialAccessor.store_refresh_token(ea, token_response.refresh_token)
        messages.success(
            request,
            _('Refresh token received successfully.'),
        )
    except (MissingOAuthConfigError, OAuthTokenExchangeError) as err:
        report_mail_incident(
            account=ea,
            operation='oauth2_callback',
            exception=err,
            context={
                'provider_error': getattr(err, 'provider_error', str(err)),
                'status_code': getattr(err, 'status_code', ''),
            },
        )
        messages.error(
            request,
            _('Token exchange failed. Please try again.'),
        )

    url = reverse('site:massmail_emailaccount_change', args=(ea.id,))
    return HttpResponseRedirect(url)
