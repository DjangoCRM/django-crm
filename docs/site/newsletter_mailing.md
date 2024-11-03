## Newsletter mailing

!!! Note
    Please do not use this application to send spam!

The Massmail application requires:

- the existence of contact persons (recipients) in the [CRM](https://github.com/DjangoCRM/django-crm/){target="_blank"} database;
- configured [email accounts](setting_up_email_accounts.md) for sales managers (marked "Massmail");

The application provides recipients with an opportunity to unsubscribe from mailings.  
In order not to disclose the address of your CRM (on the Internet), it is necessary to create a page on your company's website, where users who clicked the **UNSUBSCRIBE** button will be forwarded.  
This page should show a message that the user unsubscribed successfully.
The address of this page should be specified in the settings (massmail/settings.py)  
`UNSUBSCRIBE_URL = 'https://<www.your_site.com>/unsubscribe'`

Each message template must contain the **UNSUBSCRIBE** button with this url.
