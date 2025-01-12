## Guide for sales manager

### Deal object

A Deal object is created on the basis of a request as described in the section [Working with requests](operator_and_sales_manager_roles.md#working-with-requests).  
A Deal object can be assigned to a co-owner - a second sales manager who can also work on this deal.

The object of the deal allows:

- see the customer's request
- <span style="vertical-align: baseline"><img src="../icons/envelope-check.svg" alt="Envelope icon" width="17" height="17"></span> send and receive emails and see all correspondence related to this deal
- contact the counterparty by phone and use messengers
- <span style="vertical-align: baseline"><img src="../icons/paperclip.svg" alt="Paperclip icon" width="17" height="17"></span> store all files associated with this deal
- create office memos regarding the deal
- <span style="vertical-align: baseline"><img src="../icons/chat-left-text.svg" alt="Chat icon" width="17" height="17"></span> exchange messages in the chat with company management, second sales manager and administrator
- <span style="vertical-align: baseline"><img src="../icons/alarm.svg" alt="Alarm icon" width="17" height="17"></span> create reminders
- <span style="vertical-align: baseline"><img src="../icons/tags.svg" alt="Tags icon" width="17" height="17"></span> tag the deal

The Deal object represents:

- contact details of the counterparty
- all deals with the counterparty company
- information on goods/services of the deal
- payment information

When you create an email, Django CRM injects a ticket into it. This allows [CRM software](https://github.com/DjangoCRM/django-crm/){target="_blank"} to find emails related to this deal in sales managers' email accounts and upload them to the CRM database. 
!!! Important

    Therefore, at least the first letter must be sent from the CRM. Further correspondence can be carried out from email accounts if a ticket is saved in the emails.
If for some reason a letter was created related to a deal but without a ticket, then it can be imported and linked to the deal using the "Import letter" button.

The stages of the deal, reasons for closing, and much more can be customized to suit the specifics of your company - contact your CRM administrator.

The data specified in deals is used in [CRM Analytics](guide_for_company_executives.md#crm-analytics). For example, the stages of a transaction are used to build a "sales funnel" report. It can be viewed here:  
 `Home > Analytics > Sales funnel`


At the moment, there are eight different reports available in the CRM Analytics.

### Payment object

You can create payment objects in a deal.
In addition to the usual data, the payment can have one of the following statuses:

- received
- guaranteed
- high probability
- low probability

This is used to create a [summary of income](guide_for_company_executives.md#income-summary-report), including its forecast.  
The income summary is important for management decision-making by the company's executives.  
 `Home > Analytics > Income Summary`


### List of Deals

By default, new [Deals](#deal-object) are placed at the top of the list. But by pressing the sort toggle trigger button, you can switch between this sort and sort by next step date. In this mode, transactions whose next step date is approaching will be pushed to the top of the list.

By default, only active deals are shown in the list. When work on the deal is completed, you need to select the reason for closing the deal in the drop-down menu of the deal. Then the deal will no longer be active and will not appear in the list by default.

To provide more information about deals, they are marked with different icons. To get a hint about the meaning of an icon, hover your mouse cursor over it.

### Company Newsletter

[Django CRM](https://github.com/DjangoCRM/django-crm/){target="_blank"} allows you to automatically carry out email marketing.  
Recipients can be companies, contacts and leads from the CRM database.  
Uninterested recipients have the opportunity to unsubscribe from receiving further mailings.

Mailing is performed through the main and additional mail accounts of sales managers. Additional email accounts should be created and configured by the CRM administrator to reduce the risk of spam filters blocking the main accounts of managers. For the same purpose, mailings from the main account are only sent to recipients marked as VIP. This can be done through the drop-down menu of actions on the recipient list pages ([companies](operator_and_sales_manager_roles.md#company-object), [contacts](operator_and_sales_manager_roles.md#object-of-company-contact-persons) and [leads](operator_and_sales_manager_roles.md#lead-object)).

If accounts that require [two-step authentication](imap4_protocol_client.md#configuring-two-step-oauth-20-authentication) for third-party applications are used for mailing, you should contact the administrator for assistance in passing it for the first time.

Prepare a message for the newsletter:  
 `Home > Mass mail > Email Messages`


To embed images in your message, you can use the button to upload an image file to the CRM server and the button to view uploaded images.  
Under each image, there is a html tag of the path to the file. It should be copied and pasted into the message template.

You can copy a finished message from another sales manager to yourself (the message does not contain a signature).  
You can use the "Send Test" button to check the message display. The CRM software will make a list of available email accounts of the sales manager and send the message from the first account to the other accounts.

The mailing object is created on the pages of the recipient lists (companies, contacts and leads). To do this, you can use the "Create mailing" button or the drop-down action menu.
Using the action menu, you can create a mailing to selected recipients on one page. If you have to create several mailing lists, you can combine them using the action menu on the mailing list page.  
In the created mailing object, specify the message to be sent, the desired signature and save the object with the status "active." To simulate a human being, CRM software will send emails evenly throughout the work day at random intervals. The mailing will be automatically paused on Friday, Saturday and Sunday.

### Transfer of company objects to another sales manager

A sales manager can transfer a company object to another manager. Contact persons will be transferred automatically.  
But to change the owner of a group of companies, you must contact the administrator.
