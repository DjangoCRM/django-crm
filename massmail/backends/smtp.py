import base64
from smtplib import SMTP
from dataclasses import replace

from django.core.mail.backends.smtp import EmailBackend

from sharedkernel.credentials import (
    CredentialAccessor,
    OAuthTokenExchangeError,
    SmtpCredentials,
)
from sharedkernel.oauth_exchange import exchange_refresh_token


class OAuth2EmailBackend(EmailBackend):
    def __init__(
        self,
        host=None,
        port=None,
        username=None,
        password=None,
        use_tls=None,
        fail_silently=False,
        use_ssl=None,
        timeout=None,
        ssl_keyfile=None,
        ssl_certfile=None,
        refresh_token=None,
        email_account=None,
        **kwargs,
    ):
        super().__init__(
            host=host,
            port=port,
            username=username,
            password=password,
            use_tls=use_tls,
            fail_silently=fail_silently,
            use_ssl=use_ssl,
            timeout=timeout,
            ssl_keyfile=ssl_keyfile,
            ssl_certfile=ssl_certfile,
            **kwargs,
        )
        self.refresh_token = refresh_token
        self.email_account = email_account

    @classmethod
    def from_smtp_credentials(
        cls,
        credentials: SmtpCredentials,
        *,
        email_account=None,
        fail_silently: bool = False,
        timeout=None,
        ssl_keyfile=None,
        ssl_certfile=None,
    ) -> 'OAuth2EmailBackend':
        return cls(
            host=credentials.host,
            port=credentials.port,
            username=credentials.user,
            use_tls=credentials.use_tls,
            fail_silently=fail_silently,
            timeout=timeout,
            ssl_keyfile=ssl_keyfile,
            ssl_certfile=ssl_certfile,
            refresh_token=credentials.password,
            email_account=email_account,
        )

    def get_access_token(self) -> str:
        if self.email_account is None:
            raise OAuthTokenExchangeError(0, 'missing_email_account')

        credentials = CredentialAccessor.get_oauth_credentials(self.email_account)
        if not credentials.refresh_token and self.refresh_token:
            credentials = replace(credentials, refresh_token=self.refresh_token)

        try:
            token_response = exchange_refresh_token(credentials)
        except OAuthTokenExchangeError as err:
            raise OAuthTokenExchangeError(
                err.status_code,
                err.provider_error,
                account_id=self.email_account.pk,
            ) from err

        if token_response.refresh_token:
            CredentialAccessor.store_refresh_token(
                self.email_account,
                token_response.refresh_token,
            )
        CredentialAccessor.store_access_token(
            self.email_account,
            token_response.access_token,
        )
        return token_response.access_token

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
