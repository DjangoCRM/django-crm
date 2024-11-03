## Setting up email accounts

`(ADMIN) Home > Mass mail > Email Accounts`

Mail accounts must be set up for users with the [roles](adding_crm_users.md#user-groups-roles) "Operator", "Super Operator" and "Manager" (Sales Manager).
This will allow the following to be realized:

- Users will be able to send emails from [Django CRM](https://github.com/DjangoCRM/django-crm/){target="_blank"} through their email account.
- The CRM will have access to the user's account and will be able to import and link to Deals letters sent not from CRM (if there is a corresponding ticket in the letters).
- Users will be able to [import requests from email into CRM](setting_up_adding_requests.md).
- When performing a newsletter mailing, CRM will be able to send emails through the user's account on the user's behalf.

### Fields

#### "Main"

One user can have several accounts, but sending work emails from CRM will be done only through the account marked as "Main".

#### "Massmail"

Mass mailing can be sent through all accounts marked "Massmail".

#### "Do import"

The mark "Do import" should be made for accounts through which managers conduct business correspondence or for accounts specified on the company's website, as they may receive requests from customers.

#### "Email app password"

The "Email app password" field value is specified for those accounts where you can set a password for applications.  In this case, CRM will use it when logging in to the user account.

#### Section "Service information"

This section displays statistics and service information of CRM activity in this account.

#### Section "Additional information"

Here you need to specify the account owner and its department.  
The other fields are described in detail in the [Settings](https://docs.djangoproject.com/en/dev/ref/settings/#std-setting-EMAIL_HOST){target="_blank"} section of Django documentation.
