# Django-CRM - installation and configuration guide

## Table of contents

- [Introduction](#introduction)
- [Project installation](#project-installation)
  - [Download or clone the project](#download-or-clone-the-project)
  - [Install the requirements](#install-the-requirements)
- [Settings of Django CRM](#settings-of-django-crm)
- [CRM and database testing](#crm-and-database-testing)
- [Installing the initial data](#installing-the-initial-data)
- [Launch CRM on the development server](#launch-crm-on-the-development-server)
- [Access to CRM and admin sites](#access-to-crm-and-admin-sites)
- [Specify CRM site domain](#specify-crm-site-domain)
- [Ability to translate Django CRM interface into another language](#ability-to-translate-django-crm-interface-into-another-language)
- [Built-in assistance system](#built-in-assistance-system)
- [Adding Django CRM users](#adding-django-crm-users)
  - [Permissions for users](#permissions-for-users)
  - [User groups](#user-groups)
  - [Departments](#departments)
  - [Adding users](#adding-users)
- [User access to applications and objects](#user-access-to-applications-and-objects)
- [Helping users to master Django CRM](#helping-users-to-master-django-crm)
- [Setting up adding commercial requests in Django CRM](#setting-up-adding-commercial-requests-in-django-crm)
  - [Sources of Leads](#sources-of-leads)
  - [Forms](#forms)
    - [Submitting form data with a POST request](#submitting-form-data-with-a-post-request)
    - [Embedding CRM form in an iframe of a website page](#embedding-crm-form-in-an-iframe-of-a-website-page)
    - [Activate form protection with Google's reCAPTCHA v3](#activate-form-protection-with-googles-recaptcha-v3)
    - [Activation of geolocation of the country and city of the counterparty by its IP](#activation-of-geolocation-of-the-country-and-city-of-the-counterparty-by-its-ip)
    - [Adding a custom form for iframe](#adding-a-custom-form-for-iframe)
- [Setting up email accounts](#setting-up-email-accounts)
  - [Fields](#fields)
    - ["Main"](#main)
    - ["Massmail"](#massmail)
    - ["Do import"](#do-import)
    - ["Email app password"](#email-app-password)
    - [Section "Service information"](#section-service-information)
    - [Section "Additional information"](#section-additional-information)
- [IMAP4 protocol client](#imap4-protocol-client)
- [Configuring two-step OAuth 2.0 authentication](#configuring-two-step-oauth-20-authentication)
- [Company product categories](#company-product-categories)
- [Company products](#company-products)
- [Currencies](#currencies)
- [Newsletter](#newsletter)
- [VoIP telephony](#voip-telephony)
- [CRM integration with messengers](#crm-integration-with-messengers)

## Introduction

[Django-CRM](https://github.com/DjangoCRM/django-crm/) (Customer Relationship Management) is an open source web application.  
It is based on the [Django Admin site](https://docs.djangoproject.com/en/dev/ref/contrib/admin/) and is written in the [Python](https://www.python.org/) programming language.

The CRM project consists of the following main applications:

- TASKS;
- CRM;
- ANALYTICS;
- MASS MAIL.

The TASKS application does not require complicated CRM configuration and allows users to work with the following objects:

- Memos;
- Tasks;
- Projects;
- Chat;
- Tags.

Access to this application is available to all CRM users.

Access to the rest of the applications is only available to users with the appropriate roles, such as sales managers, company executives, etc.  
To use all the features of these applications, you need to set up CRM integration:

- with your company's websites;
- with your company's mailboxes and sales managers' mailboxes;
- with the service of receiving current exchange rates (if necessary);
- with VoIP telephony service (if necessary).

## Project installation

The CRM code is a ready Django project.  
To deploy the project, you will need: [Python](https://www.python.org/), and database.  
CRM is developed and used with [MySQL](https://www.mysql.com/) database
but taking into account compatibility with [PostgreSQL](https://www.postgresql.org)
(passes the current set of tests).  
After downloading, you need to deploy and customize the CRM code like a normal Django project.  
If the project is deployed on a production server, a website server will also be required
(for example [Apache](https://httpd.apache.org/)).  
Full tutorial [here](https://docs.djangoproject.com/en/dev/topics/install/).

### Download or clone the project

Create Clone the GitHub repository:

```cmd
git clone https://github.com/DjangoCRM/django-crm.git
```
(the project will be cloned into the 'django-crm' folder)

Or download the zip file and unpack it:

```cmd
wget https://github.com/DjangoCRM/django-crm/archive/main.zip
unzip main.zip
```
The project will be unzipped into the 'django-crm-main' folder.  
Rename the folder to "django-crm".  

### Install the requirements

It is recommended to first create a virtual environment:

```cmd
python3 -m venv ./myvenv
```

and activate it:

```cmd
cd ./myvenv/bin
source activate
cd ../../django-crm
```

then install the project requirements:

```cmd
pip install -r requirements.txt
```

## Settings of Django CRM

The project settings are contained in the file  
`webcrm/settings.py`

As well as in the Django CRM application files:  
`common/settings.py`  
`crm/settings.py`  
`massmai/settings.py`  
`voip/settings.py`  
The syntax of the data in these files must match the syntax of the Python language.

Most of the project settings are Django settings.
Their full list is [here](https://docs.djangoproject.com/en/dev/ref/settings/).  
The settings missing in this list are CRM specific settings. Explanations can be found in the comments to them.  
Most of the settings can be left at their default values.

The default settings are for running the project on a development server.
Change them for the production server.  

To start the project for the first time, it is enough to specify the database settings in the file  
`webcrm/settings.py`  
But in the following, you will need to specify at least the `EMAIL_HOST` and `ADMINS` settings.

### DATABASES

Provide data to connect to the database.  
Detailed instructions [here](https://docs.djangoproject.com/en/dev/ref/settings/#std-setting-DATABASES).  
Configure the `USER` specified in the `DATABASES` setting to have the right to create and drop databases.  
Running tests will create
and then destroy a separate [test database](https://docs.djangoproject.com/en/dev/topics/testing/overview/#the-test-database).

### For MySQL database, it is recommended to  

- setup the timezone table;  
- set the extended encoding:
  - charset `utf8mb4`
  - collation  `utf8mb4_general_ci`

And also if an aggregation or annotation error occurs when running the tests, 
you need to change sql_mode to `ONLY_FULL_GROUP_BY`.

### Optimizing PostgreSQL's configuration

You'll need the [psycopg](https://www.psycopg.org/psycopg3/) or [psycopg2](https://www.psycopg.org/) package.
Set the timezone to 'UTC' (when USE_TZ is True),
default_transaction_isolation: 'read committed'.  
You can configure them directly in postgresql.conf `(/etc/postgresql/<version>/main/)`

### EMAIL_HOST

Specify details for connecting to an email account 
through which CRM will be able to send notifications to users and administrators.  

- `EMAIL_HOST` (smtp server)
- `EMAIL_HOST_PASSWORD`
- `EMAIL_HOST_USER` (login)

### ADMINS

Add the addresses of CRM administrators to the list, so they can receive error logs.  
`ADMINS = [("<Admin1 name>", "<admin1_box@example.com>"), (...)]`


## CRM and database testing

Run the built-in tests:  

```cmd
python manage.py test --noinput
```

## Installing the initial data

To fill CRM with initial data, you need to execute the command "setupdata" in the root directory of the project:  

```cmd
python manage.py setupdata
```
This command will execute `migrate`, `loaddata` and `createsuperuser`.
As a result, the database will be populated with objects such as  
countries, currencies, departments, industries, etc.  
Also the superuser will be created.
You will be able to modify them or add your own.  
Use the superuser credentials from the output to log into the CRM site.


## Launch CRM on the development server

Don’t use this server in anything resembling a production environment.  
It’s intended only for use while developing.  

 ```cmd
python manage.py runserver
 ```

## Access to CRM and admin sites

Now you have two websites.  
Use the superuser credentials to log in.  

CRM site for all users:  
`http://127.0.0.1:8000/en/123/`  
It's according to the template  
`<your CRM host>/<LANGUAGE_CODE>/<SECRET_CRM_PREFIX>`

and Admin site for administrators (superusers):  
`http://127.0.0.1:8000/en/456-admin`  
`<your CRM host>/<LANGUAGE_CODE>/<SECRET_ADMIN_PREFIX>`

`LANGUAGE_CODE`, `SECRET_CRM_PREFIX` and `SECRET_ADMIN_PREFIX`
are on file `webcrm/settings.py`

**Attention!** 
Do not attempt to access the bare `<your CRM host>` address (http://127.0.0.1:8000/).  
This address is not supported.  
To protect CRM with a site server (e.g. [Apache](https://httpd.apache.org/)), a redirect to a fake login page can be placed on this address.

## Specify CRM site domain

In the SITES section for administrators (superusers):  
`(ADMIN site) Home > Sites > Sites`  
Add a CRM site and specify its domain name.

## Ability to translate Django CRM interface into another language

Users can choose the language of the [Django-CRM](https://github.com/DjangoCRM/django-crm/) interface.  
The list of available languages (LANGUAGES) and the default language (LANGUAGE_CODE) are defined in the file:
`webcrm/settings.py`

Add the desired language, e.g., German:  

```cmd
LANGUAGES = [
    ("de", _("German")),
    ("en", _("English")),
]
```

Save the file.  
Run the following command in the terminal in the root directory of the project:

```cmd
python manage.py makemessages -l de
```

In the directory  
`locale/de/LC_MESSAGES`  
django.po file will appear.  
Use the po file editor to translate its contents and create a mo file.  
Put the mo file in the same directory.

CRM remembers the user's language choice, so there is no need to change the default language.

Restart CRM.

If the objects you added, such as deal stages, reasons for closing deals, have names in English, these names can also be translated. To do this, perform the above steps again, starting with the "makemessages" command.

More details [here](https://docs.djangoproject.com/en/5.0/topics/i18n/translation/).

## Built-in assistance system

Many pages have an icon (?) in the upper right corner.  
This is a link to a help page.

Many buttons and icons on CRM pages have tooltips that appear when you hover your mouse over them.

## Adding Django CRM users

After completing the previous steps of this instruction, you can begin adding users. But in order for sales managers to be able to use all the features of Django CRM, they must follow the remaining points of this instruction.  
Please review the following sections before adding users.

### Permissions for users

There are four permissions for users in relation to objects (e.g., Tasks, Deals, etc.):  

- add (create),
- view,
- change,
- change.

Permissions can be assigned to individual users or groups of users.  
In relation to a particular object instance, CRM can dynamically change the permissions set for the object type. For example, a user who has permission to modify emails will not be able to modify an email if it is an incoming email.

### User groups

Groups are a convenient way to assign users a specific set of permissions or attributes. A user can belong to any number of groups. For example, the head of the sales department needs to be added to the "managers", "department heads" groups and the group of the department in which he works (for example, "Global sales").  
The "department heads" and "Global sales" groups give their members the appropriate attribute but do not provide any permissions.  
The "managers" (sales managers) group provides its members with sets of permissions in relation to such objects as: Request, Deal, Lead, Company, Contact person, etc.  
A group that gives its members certain rights is called a role.

The following roles are available:

- chiefs (company executives),
- managers (sales managers),
- operators (employees who receive commercial requests coming to the company. For example, a secretary or receptionist),
- superoperators (the same as operator but with the rights to serve several sales departments),
- accountants,
- co-workers (this group is added to all users by default to work with TASKS),
- task_operators (allows you to edit Memos (Office notes) and Tasks objects owned by other users).

You can view the permission sets for each role here:  
 `(ADMIN site) Home > Authentication and Authorization > Groups`

A user can have multiple roles.  
For example, if your company does not have an employee who could perform the role of operator, then this role should be given to an employee with the role of sales manager.  
Attention! It is possible that some combinations of roles can lead to incorrect CRM operation. In this case, you can create several accounts for the user in CRM with different roles.

### Departments

The Department object contains the name and properties of a specific department.
You need to create a department on the page:  
`(ADMIN site) Home > Common > Departments`

When creating a department, a group with the same name is automatically created.  
**Please note** that creating a group for use as a department without creating a Department object will result in CRM not working correctly.
The following departments are preinstalled in CRM:  

- Global sales,
- Local sales,
- Bookkeeping.

You can rename them or add new ones.

### Adding users

`(ADMIN site) Home > Authentication and Authorization > Users`

To allow user access to the CRM website, check the following check-boxes:  
Active and Staff status.

If there is no suitable role for a user, then the set of permissions for him can be set individually.
All users must be added to their department group. The only exceptions are company managers (users with the "chiefs" roles).
For superusers (CRM administrators), assigning a department is optional.

A User profile is automatically created for each user. You can specify additional data in the User profile.  
 `(ADMIN site) Home > Common > User profiles`

This profile will be available to all CRM users at:  
 `(CRM site) Home > Common > User profiles`

## User access to applications and objects

CRM may contain commercial information or confidential information. Therefore, a user's access to applications and objects is determined by his role (set of rights).  
The rights can be permanent or dynamic.  
For example, if a company has two sales departments, sales managers can always see only objects (Requests, Deals, Reports, etc.) related to their department.

Dynamic rights can depend on many factors. For example, the value of filters. Even company managers or CRM administrators who can see all objects will not be able to see an object belonging to a department different from the current one selected in the department filter. To see this object, you need to select the corresponding department in the filter or select the "all" value.

## Helping users to master Django CRM

Before starting to work in Django CRM, users should be informed about the following:  

- It is important to familiarize yourself with the user guide to learn the CRM more easily.
- Many CRM pages have a button to go to the help page - (?). It is located in the upper right corner. Help pages should be read.
- Many page elements such as buttons, icons, links have tooltips. To do this, you need to hover the mouse cursor over them.  
It is also important for the administrator to help users to master the CRM.

**Pay attention!** Help pages are dynamic. Their content depends on the user's role. Users who are assigned rights individually (without a role assignment) will not be able to access the help page. Such users should be instructed to work in CRM by the administrator.

## Setting up adding commercial requests in Django CRM

In Django CRM you can add commercial requests ("Requests") in manual, automatic and semi-automatic mode.
In manual mode, you must press the "ADD REQUESTS" button at:  
  `Home > Crm > Requests`  
and fill out the form.

Requests coming from forms on your company's website are automatically created (if configured accordingly).  
In a semi-automatic mode, requests are created by sales managers or operators when importing emails received to their mail into CRM.  
To do this, you need to specify the details of their [mail accounts](#setting-up-email-accounts) in CRM to ensure CRM access to these accounts.
CRM automatically assigns the owner of the imported request to the owner of the email account.

### Sources of Leads

`(ADMIN) Home > Crm > Lead Sources`  
For marketing purposes, each "Request", "Lead", "Contact" and "Company" has a link to the corresponding "Lead Source".  
Each Lead Source is identified by the value of its UUID field, which is generated automatically when a new Lead Source is added to the CRM.  
For convenience, CRM has a number of pre-defined "Leads Sources". These can be edited.
Each "Lead Source" has a link to a "Department". Therefore, each department can have its own set of lead sources.  
The "Form template name" and "Success page template name" fields are only populated when [adding a custom iframe form](#adding-a-custom-form-for-iframe).  
The "Email" field is only specified in the "Lead Source" of your website. You need to specify the Email value indicated on your site.

### Forms

CRM can automatically receive data from forms on your company's websites and, based on it, create commercial requests in the database.
To do this, you need to configure the site to send POST form data via a request to CRM. Or use CRM forms by adding them to sites via iframe.

#### Submitting form data with a POST request

Your site can pass the values of the following form fields to CRM by POST request:  
`"name" - CharField (max_length=200, required)`  
`"email" - EmailField / CharField (max_length=254, required)`
`"subject" - CharField(max_length=200, required)`  
`"phone" - CharField(max_length=400, required)`  
`"company" - CharField(max_length=200,  required)`  
`"message" - TextField`  
`"country" - CharField(max_length=40)`  
`"city"- CharField(max_length=40)`  
`"leadsource_token" - UUIDField(required, hidden Input)`

The value of the "leadsource_token" field must match the value of the "UUID" field of the corresponding (selected by you) "Leadsource".  
`(ADMIN site) Home > Crm > Lead Sources`

Url for POST request:  
`https://<yourCRM.domain>/<language_code>/add-request/`

#### Embedding CRM form in an iframe of a website page

Place an iframe string in the HTML code of a website page.  
Here is an example of a simple string:

```HTL
<iframe src="<url>" style="width: 600px;height: 450px;"></iframe>
```

url must follow the format:  
`https://<yourCRM.domain>/<language_code>/contact-form/<uuid>/`
where uuid is the values of the "UUID" field of the selected "Lead Source".

#### Activate form protection with Google's reCAPTCHA v3

CRM form has built-in reCAPTCHA v3 protection.  
To activate it, specify the values of keys received during registration on this service:  
`GOOGLE_RECAPTCHA_SITE_KEY = ''<your site key>"`  
`GOOGLE_RECAPTCHA_SECRET_KEY = ''<your secret key>"`

#### Activation of geolocation of the country and city of the counterparty by its IP

CRM form has a built-in ability to geolocate the country and city of the counterparty (site visitor) by its IP.  For this purpose, GeoIP2 module is used.  
To activate its work:

- save the [MaxMind](https://dev.maxmind.com/geoip/docs/databases) files of the city and country databases (GeoLite2-Country.mmdb and GeoLite2-City.mmdb) to the media/geodb directory;
- set GEOIP = True in the file

#### Adding a custom form for iframe

You can change the style of a preset form or add forms with different styles to fit on different pages of the site or on different sites.  
To add a new form, place the HTML template for that form and the successful form submission message template at the following location:  
`<crmproject>/crm/templates/crm/`

Save the names of these files in the "Form template name" and "Success page template name" fields of the selected "Lead Source" in the following format:  
 `"crm/<file name>.html"`

## Setting up email accounts

`(ADMIN) Home > Mass mail > Email Accounts`

Mail accounts must be set up for users with the roles "Operator", "Super Operator" and "Manager" (Sales Manager).
This will allow the following to be realized:

- Users will be able to send emails from CRM through their email account.
- CRM will have access to the user's account and will be able to import and link to Deals letters sent not from CRM (if there is a corresponding ticket in the letters).
- Users will be able to import requests from email into CRM.
- When performing a newsletter, CRM will be able to send emails through the user's account on the user's behalf.

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
The other fields are described in detail in the "[Settings](https://docs.djangoproject.com/en/dev/ref/settings/#std-setting-EMAIL_HOST)" section of Django documentation.

## IMAP4 protocol client

Django CRM uses an IMAP4 protocol client to allow users to view, import and delete emails in their email account.  
Unfortunately, the operation of the IMAP4 client depends on the mail service. Because not all email services strictly adhere to the IMAP4 protocol.  
In some cases, changing CRM settings will not help. You need to either make changes to the code or change the service provider. For example, if the service does not support IMAP4 or only supports some commands.

CRM settings related to IMAP4 client operation are in the file:  
`<crmproject>/crm/settings.py`  
In most cases, they do not need to be changed.

## Configuring two-step OAuth 2.0 authentication

If users use gmail accounts, then to connect CRM to them via SMTP and IMAP protocols, you will need to set up access and pass two-step authentication once.  
Google APIs use the [OAuth 2.0 protocol](https://tools.ietf.org/html/rfc6749) for authentication and authorization.
Visit the [Google API Console](https://console.developers.google.com/). Create "OAuth 2.0 Client IDs" settings
 for "Web application" to specify the Authorized redirect URI in the format:  
 `https://<yourCRM.domain>/OAuth-2/authorize/?user=<box_name>@gmail.com`

And also get the credentials OAuth 2.0 "CLIENT_ID" and "CLIENT_SECRET". Save them in the project settings  
`<crmproject>/webcrm/settings.py`

Then on the desired "Email Account" page  
 `(ADMIN) Home > Mass mail > Email Accounts`  
In the upper right corner, click the button "Get or update a refresh token".  
CRM will open the authorization page. After successful authorization, the "Refresh token" value will be received and CRM will get access to this account.

## Company product categories

Add categories of your company's products, goods or services.  
`(ADMIN) Home > Crm > Product categories`

## Company products

Add your company's products, services or goods
(this can be done later by sales managers).  
`(ADMIN) Home > Crm > Products`

## Currencies

Since CRM uses currencies for marketing purposes, users can change the exchange rates themselves.  
But it is also possible to configure CRM to automatically receive accurate exchange rates from a bank or other service in your country.  
To do this, you need to create a backend file, put it in the directory  
`crm/backends`  
You can use already existing backends as a basis.  
Then in the settings file, specify the name of the backend class in the setting  
LOAD_RATE_BACKEND

## Newsletter

Please do not use this application to send spam!

The Massmail application requires:

- the existence of contact persons (recipients) in the database;
- configured [email accounts](#setting-up-email-accounts) for sales managers (marked "Massmail");

The application provides recipients with an opportunity to unsubscribe from mailings.  
In order not to disclose the address of your CRM (on the Internet), it is necessary to create a page on your company's website, where users who clicked the "unsubscribe" button will be forwarded.  This page should show a message that the user unsubscribed successfully.
The address of this page should be specified in the settings (massmail/settings.py)  
`UNSUBSCRIBE_URL = 'https://<www.your_site.com>/unsubscribe'`

Each message template must contain the UNSUBSCRIBE button with this url.

## VoIP telephony

A properly configured application allows you to make calls directly from Django CRM.
This application allows you to integrate CRM with the services of VoIP provider ZADARMA.  But it can also be used to create integration files with other providers.

It is necessary to receive from the provider (zadarma.com) and to specify in voip/settings.py file the following values: SECRET_ZADARMA_KEY, SECRET_ZADARMA.
FORWARD settings are specified independently, but only if you have a second instance of working CRM (for example, for a subsidiary company).

Then add Connections objects for users in the  
 `(ADMIN) Home > Voip > Connections`

To connect to a different provider, you must create new files for it
backend (voip/backends) and (voip/views).  
And also add provider data to the VOIP list in the file  
`voip/settings.py`

## CRM integration with messengers

Django CRM has the ability to send messages via messengers.  Such as  
Viber, WhatsApp, Skype. To do this, these applications must be installed on the user's device.
