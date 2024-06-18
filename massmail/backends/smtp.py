import base64
import json
import requests
from smtplib import SMTP
from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend


class OAuth2EmailBackend(EmailBackend):
    def __init__(self, host=None, port=None, username=None, password=None,
                 use_tls=None, fail_silently=False, use_ssl=None, timeout=None,
                 ssl_keyfile=None, ssl_certfile=None, refresh_token=None,
                 **kwargs):
        super().__init__(host=host, port=port, username=username, password=password,
                         use_tls=use_tls, fail_silently=fail_silently, use_ssl=use_ssl,
                         timeout=timeout, ssl_keyfile=ssl_keyfile, ssl_certfile=ssl_certfile,
                         **kwargs)
        self.refresh_token = refresh_token
        
    def get_access_token(self) -> str:
        params = {
            'client_id': settings.CLIENT_ID,
            'client_secret': settings.CLIENT_SECRET,
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token'
        }
        data = settings.OAUTH2_DATA[self.host]
        request_url = f"{data['accounts_base_url']}/{data['token_command']}"
        response = requests.post(request_url, params)
        result = json.loads(response.text)
        if result.get('error', None):
            raise RuntimeError(response.text)
        return result['access_token']
    
    def get_auth_string(self):
        access_token = self.get_access_token()
        auth_string = f"user={self.username}\1auth=Bearer {access_token}\1\1"
        auth_string_bytes = auth_string.encode("utf-8")
        auth_string_b64encoded = base64.b64encode(auth_string_bytes)
        auth_string_encoded = auth_string_b64encoded.decode("utf-8")
        return auth_string_encoded             

    def open(self):
        """
        Ensure an open connection to the email server. Return whether or not a
        new connection was required (True or False) or None if an exception
        passed silently.
        """
        if self.connection:
            # Nothing to do if the connection is already open.
            return False

        connection_params = {}
        if self.timeout is not None:
            connection_params['timeout'] = self.timeout

        try:
            self.connection = SMTP(self.host, self.port, **connection_params)
            self.connection.starttls()
            auth_string = self.get_auth_string()
            response = self.connection.docmd('AUTH', 'XOAUTH2 ' + auth_string)
            if response != (235, b'2.7.0 Accepted'):
                raise RuntimeError("SMTP AUTH failed!")
            return True
        except OSError:
            if not self.fail_silently:
                raise
