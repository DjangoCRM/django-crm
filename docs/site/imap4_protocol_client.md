## IMAP4 protocol client

[Django CRM](https://github.com/DjangoCRM/django-crm/){target="_blank"} uses an IMAP4 protocol client to allow users to view, import and delete emails in their email account.  

!!! IMPORTANT
    Unfortunately, the operation of the IMAP4 client depends on the mail service. Because not all email services strictly adhere to the [IMAP4 protocol](https://datatracker.ietf.org/doc/html/rfc3501){target="_blank"}.  
In some cases, changing CRM settings will not help. You need to either make changes to the code or change the service provider. For example, if the service does not support IMAP4 or only supports some commands.

The CRM settings related to IMAP4 client operation are in the file:  
`<crmproject>/crm/settings.py`  
In most cases, they do not need to be changed.

## Configuring two-step OAuth 2.0 authentication

In some cases, for CRM to access your Gmail account, you will need to set up access for third-party applications in your Gmail account and pass two-factor authentication once.
This is not an easy procedure. So first, make sure that SRM really can't access your account without it.    
Google APIs use the [OAuth 2.0 protocol](https://tools.ietf.org/html/rfc6749){target="_blank"} for authentication and authorization.  
Visit the [Google API Console](https://console.developers.google.com/){target="_blank"}. Create "OAuth 2.0 Client IDs" settings
 for "Web application" to specify the Authorized redirect URI in the format:  
 `https://<yourCRM.domain>/OAuth-2/authorize/?user=<box_name>@gmail.com`

And also get the credentials OAuth 2.0 "CLIENT_ID" and "CLIENT_SECRET". Save them in the project settings  
`<crmproject>/webcrm/settings.py`

Then on the desired [Email Account](setting_up_email_accounts.md) page  
 `(ADMIN) Home > Mass mail > Email Accounts`  
In the upper right corner, click the button "Get or update a refresh token".  
CRM will open the authorization page. After successful authorization, the "Refresh token" value will be received and CRM will get access to this account.

!!! WARNING
    To receive the refresh token, the CRM must be running on a server that supports the HTTPS scheme.
You can also retrieve the refresh token separately from the CRM, for example, using curl.