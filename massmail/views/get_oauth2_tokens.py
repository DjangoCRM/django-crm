import json
import requests
from urllib.parse import urlencode
from django.conf import settings
from django.contrib import messages
from django.contrib.sites.models import Site
from django.http import HttpResponseRedirect
from django.utils.translation import gettext as _
from django.urls import reverse
from massmail.models import EmailAccount


def get_redirect_uri(ea: EmailAccount) -> str:
    site = Site.objects.get_current()
    uri = reverse('get_refresh_token')
    return f"https://{site.domain}{uri}?user={ea.email_host_user}"


def request_authorization_code(request, email_account_id):
    ea = EmailAccount.objects.get(id=email_account_id)
    data = settings.OAUTH2_DATA.get(ea.email_host, None)
    if data:
        redirect_uri = get_redirect_uri(ea)
        params = {
            'client_id': settings.CLIENT_ID,
            'scope': data['scope'],
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'approval_prompt':  'force',
            'access_type':  'offline',
        }
        permission_url = f"{data['accounts_base_url']}/{data['auth_command']}"
        return HttpResponseRedirect(permission_url + f'?{urlencode(params)}')

    messages.error(
        request,
        f'Settings are missing in settings.OAUTH2_DATA'
    )
    url = reverse('site:massmail_emailaccount_change', args=(ea.id,))
    return HttpResponseRedirect(url)


def get_refresh_token(request):
    authorization_code = request.GET.get('code')
    email_host_user = request.GET.get('user')
    ea = EmailAccount.objects.get(email_host_user=email_host_user)
    redirect_uri = get_redirect_uri(ea)
    data = settings.OAUTH2_DATA[ea.email_host]
    if authorization_code:
        params = {
            'client_id': settings.CLIENT_ID,
            'scope': data['scope'],
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'code': authorization_code,
            'client_secret': settings.CLIENT_SECRET,
            'grant_type': 'authorization_code'
        }
        request_url = f"{data['accounts_base_url']}/{data['token_command']}"
        response = requests.post(request_url, params)
        result = json.loads(response.text)
        error = result.get('error')
        if error:
            messages.error(
                request,
                response.text
            )
        else:
            refresh_token = result['refresh_token']
            ea.refresh_token = refresh_token
            ea.save()
            messages.success(
                request,
                _(f'Refresh token received successfully.')
            )
    else:
        messages.warning(
            request,
            _(f'Error: Failed to get authorization code.')
        )
    url = reverse('site:massmail_emailaccount_change', args=(ea.id,))
    return HttpResponseRedirect(url)
