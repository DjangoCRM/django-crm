## Newsletter mailing

The **Massmail application** is a specially designed component of the [Mailing CRM](https://github.com/DjangoCRM/django-crm){target="_blank"} platform that empowers businesses to manage and execute company newsletters efficiently.
It provides tools to create, manage and send marketing emails to [contact persons](operator_and_sales_manager_roles.md#object-of-company-contact-persons), leads, and companies (recipients) directly from your CRM system.

The Massmail application requires:

- the existence of recipients in the CRM database
- configured [email accounts](setting_up_email_accounts.md) for sales managers (marked "Massmail")

Mailings from the **main** sales manager account are only sent to **VIP recipients** to avoid spam filters.    
Use the **Action menu** on the Contact persons, Companies and Leads pages to **mark them as VIP**.  
For other recipients, it is recommended to set up additional email accounts.

### Use of business time

The application allows you to send mailings only during business hours, which are defined in the settings file (`massmail/settings.py`).  
To do this, set the `USE_BUSINESS_TIME` setting to `True` (default: `False`) then the mailing will also not be performed on Friday, Saturday and Sunday.

### Unsubscribe from the mailing list

The application provides recipients with an opportunity to unsubscribe from mailings.  
To prevent revealing your CRM site's web address, create a page on your company's website to which users clicking the **UNSUBSCRIBE** button will be redirected.
This page should show a message that the user unsubscribed successfully.  
The address of this page must be specified in the settings file as follows:  
`UNSUBSCRIBE_URL = 'https://<www.your_site.com>/unsubscribe'`  
Each message template must contain the **UNSUBSCRIBE** button with this url.

### How to create mailing

There are two ways to create a mailing list.
But in any case, you first need to prepare a message for the mailing list and a signature (if necessary).  

The **first way** is to simply select recipients, for example, on the company list page, and then use the **Action menu** to create a mailing list.
This method is easier.

The **second way** is to use the **Create Mailing button** and specify the values of all filters. This method is indispensable when you are dealing with a huge number of recipients.  

The progress of mailings is displayed on the mailing list page. The data is updated when the page is refreshed.

### Responses to newsletter

In order not to create a mess, CRM automatically imports only emails related to Requests and Deals (they are provided with a ticket).
If a commercial request comes in response to a newsletter, it can be imported using the corresponding button on the page of Requests, and then all subsequent correspondence will be imported into CRM.

!!! Warning
    Do not use this application to send spam!
