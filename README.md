# Django-CRM

*(Customer Relationship Management app)*

The use of CRM by companies allows them to improve the sales performance of their products and services 📈.  
The more complex and time-consuming the sales process, the greater the improvement.  
This Enterprise level [CRM](https://github.com/DjangoCRM/django-crm) software is designed for individual use by any company. Access to the company's business data remains solely under its control.

[<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/pics/deals_screenshot.png" alt="Screenshot Django-CRM" align="center" style="float: center"/>](https://github.com/DjangoCRM/django-crm/blob/main/docs/pics/deals_screenshot.png)

## Customer relationship management features

|                              |                                                           |                                  |
|------------------------------|-----------------------------------------------------------|----------------------------------|
| ☑️ **Team tasks & projects** | ☑️ **Lead management**                                    | ☑️ **Email marketing**           |
| ☑️ **Contact management**    | ☑️ **Deal management. Instant overview all active deals** | ☑️ **Sales forecasting**         |
| ☑️ **Email sync & tracking** | ☑️ **Marketing activities. Lead sources**                 | ☑️ **Internal Chat Integration** |
| ☑️ **Reminder System**       | ☑️ **Role based access control**                          | ☑️ **Analytical reporting**      |
| ☑️ **Apps & integrations**   | ☑️ **Sales Performance Management**                       | ☑️ **Mobile Access**             |  

***For a more detailed software overview, click [here](https://github.com/DjangoCRM/django-crm/blob/main/docs/crm_system_overview.md)***.

Django CRM is an open-source client relationship software. This CRM is written in [Python](https://www.python.org).  
Frontend and backend are entirely based on the Django [Admin site](https://docs.djangoproject.com/en/dev/ref/contrib/admin/).
CRM app uses adaptive Admin HTML templates out-of-the-box.  
Django is an excellently documented framework with lots of examples.
The documentation on the Admin site takes up only one web page.  
💡 The **original idea** is that since Django Admin is already a professional object management interface with a flexible permissions system for users (view, change, add, and delete objects), all you need to do is create models for the objects (such as Leads, Requests, Deals, Companies, etc.) and add business logic.  

All this ensures:

- significantly easier project customization and development
- simpler project deployment and production server support

The **project is mature, and the code is stable** (has been in practical use for many years).  
The software package provides two websites:

- CRM site for all users
- site for administrators

## Elevate Your Team's Productivity with Collaborative CRM Solution

This CRM is designed to enhance collaboration within teams and streamline project management processes.  
As a collaborative CRM, it allows users to create and manage memos, tasks, and projects with ease.  
Office memos can be directed to department heads or company executives, who can then transform these memos into tasks or projects, assigning responsible persons or executors.  
Tasks can be individual or collective. Tasks provide features such as chat discussions, reminders, file sharing, creating subtasks, and sharing results.  
Users receive notifications directly in the CRM and via email, ensuring they stay informed.  
Each user has a clear view of their task stack, including priorities, statuses, and next steps, thereby enhancing productivity and accountability in collaborative customer relationship management.

## Main applications

The CRM software suite consists of the following **main applications** and their models:

- **TASKS app**:
  - Task (with related: files, chat, reminders, tags)
    - subtasks
  - Memo (office memo)
    - tasks / project
  - Project (*tasks collection*):
    - tasks
  - Tags
  - ... (+ *3 more models*)
- **CRM app**:
  - Requests (commercial inquiries)
  - Leads (potential customers)
  - Companies
  - Contact persons (associated with their companies)
  - Deals (like "Opportunities")
  - Emails (sync with user email accounts)
  - Products (goods and services)
  - Payments (received, guaranteed, high and low probability)
  - ... (*+ 12 more models*)
[<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/pics/income_summary_thumbnail.png" alt="Analytical crm report" align="right" width="190px" style="float: right"/>](https://github.com/DjangoCRM/django-crm/blob/main/docs/pics/income_summary_screenshot.png)
- **ANALYTICS app**:
  - Income Summary report (*see [screenshot](https://github.com/DjangoCRM/django-crm/blob/main/docs/pics/income_summary_screenshot.png)*)
  - Sales funnel report
  - Lead source Summary report
  - ... (+ *5 more analytical reports*)
- **MASS MAIL app**:
  - Email Accounts
  - Email Messages (newsletters)
  - Email Signatures (user signatures)
  - Mailing Outs

## Supporting applications

The crm package also contains **supporting applications** such as:

- Chat app (chat is available in every instance of a task, project, office memo and deal)
- VoIP app (contact clients from deals)
- Help app (dynamic help pages depending on user role)
- Common app:
  - 🪪 User profiles
  - ⏰ Reminders (for tasks, projects, office memos and deals)

In total, at the moment, there are 79 tables in the database.

## Additional functionality

- Web form integration
  - CRM contact form has built-in reCAPTCHA v3 protection
  - Automatically detects the country and city of the user who filled out the form
- User's email account integration
- VoIP callback to smartphone
- Sending messages via messengers (like: Viber, WhatsApp, Skype)
- Work with Excel files to import/export of contact details

## Email client

The system includes a built-in email client that operates using **SMTP** and **IMAP** protocols.  
This enables Django CRM to automatically store copies of all correspondence related to each request and deal within its database.  
The functionality ensures that even if communications occur through the user's external email account (outside the CRM).  
They are captured and organized within the system using a **ticketing mechanism**.

The CRM can integrate with email service providers (like gmail) that require mandatory two-step authentication (using the **OAuth 2.0** protocol) for third-party applications.

## User Assistance

- On the CRM pages, there is a link to a help page.
  Help pages are dynamic. Their content depends on the user's role.
- Tooltips appear when you hover the mouse over many page elements, such as icons, buttons, links, table headings, etc.
- There is also a user guide file.

## Project localization

Django CRM has [full support](https://docs.djangoproject.com/en/dev/topics/i18n/) for translation of interface, formatting of dates, times and time zones.

## Getting started

Django-CRM can be easily deployed as a regular Django project.

📚 Please refer to:

- [Installation and Configuration Guide](https://github.com/DjangoCRM/django-crm/blob/main/docs/installation_and_configuration_guide.md)
- [User Guide](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_user_guide.md)

Compatibility

- Django 5.1.x
- Python 3.10+
- MySQL 8.0.11+ and PostgreSQL 12+  

⭐️ If you like Django-CRM, please **star** and **fork** the project!

## Contributing

We're excited to have you contribute to Django-CRM!  
Whether you're a developer, designer, or simply passionate about CRM systems, there are many ways you can help.  
Check out our [Contributing Guide](https://github.com/DjangoCRM/django-crm/blob/main/CONTRIBUTING.md) to learn how to get started. Every contribution, big or small, makes a difference

## Credits

- Uses Google material [icons](https://fonts.google.com/icons).
- Includes [NicEdit](https://nicedit.com) - WYSIWYG Content Editor.
