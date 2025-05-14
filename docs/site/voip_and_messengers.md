## VoIP telephony

A properly configured application allows you to make calls directly from [Django CRM](https://github.com/DjangoCRM/django-crm/){target="_blank"}.
This application allows you to integrate CRM with the services of VoIP provider ZADARMA.  But it can also be used to create integration files with other providers.

It is necessary to receive from the provider (zadarma.com) and to specify in `voip/settings.py` file the following values: SECRET_ZADARMA_KEY, SECRET_ZADARMA.
FORWARD settings are specified independently, but only if you have a second instance of working CRM (for example, for a subsidiary company).

Then add Connections objects for users in the  
 `(ADMIN) Home > Voip > Connections`

To connect to a different provider, you must create new files for it
backend `voip/backends` and `voip/views`.  
And also add provider data to the VOIP list in the file  
`voip/settings.py`

## CRM integration with messengers

Django CRM has the ability to send messages via messengers.  Such as  
Viber, WhatsApp. To do this, these applications must be installed on the user's device.
