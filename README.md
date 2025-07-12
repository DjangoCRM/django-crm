<p align="right">
<a href="https://github.com/DjangoCRM/django-crm/blob/main/README.md">English</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-hindi.md">हिन्दी</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-spanish.md">Español</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-chinese.md">中文</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-portuguese.md">Português</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-arabic.md">اَلْعَرَبِيَّةُ</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-french.md">Français</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-german.md">Deutsch</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-dutch.md">Nederlands</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-italian.md">Italiano</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/README/README-ukrainian.md">Українська</a>
</p>

---

# Django-CRM

*(Collaborative and Analytical Customer Relationship Management Software)*

**Django-CRM** is an open-source CRM solution designed with **two primary goals**:

- **For end users**: Deliver enterprise-level open-source CRM software with a comprehensive suite of business solutions.  
- **For maintainers and developers**: Significantly simplify the:

  - Customization of the application
  - Set up and maintain a production environment
  - Development of new features and integrations


**No need to learn a proprietary framework**: everything is built using the popular Django framework.  
CRM also takes full advantage of the Django Admin site, with documentation all contained on a single web page!

[<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/pics/deals_screenshot.png" alt="Screenshot Django-CRM" align="center" style="float: center"/>](https://github.com/DjangoCRM/django-crm/blob/main/docs/pics/deals_screenshot.png)

## Customer Relationship Management Features

|                              |                                          |                                  |
|------------------------------|------------------------------------------|----------------------------------|
| ☑️ **Team Tasks & Projects** | ☑️ **Lead Management**                   | ☑️ **Email Marketing**           |
| ☑️ **Contact Management**    | ☑️ **Deal Tracking & Sales Forecasting** | ☑️ **Role-Based Access Control** |
| ☑️ **Sales Analytics**       | ☑️ **Internal Chat Integration**         | ☑️ **Mobile-Friendly Design**    |
| ☑️ **Customizable Reports**  | ☑️ **Automated Email Sync**              | ☑️ **Multi-Currency Support**    |

Learn more about [the software's capabilities](https://github.com/DjangoCRM/django-crm/blob/main/docs/crm_system_overview.md).

Django CRM is an open-source client relationship management software.  
This CRM is written in <a href="https://www.python.org" target="_blank"><img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/python-logo.svg" style="vertical-align: bottom" alt="python logo" width="25" height="25"> Python</a>.  
Frontend and backend are entirely based on the [Django Admin site](https://docs.djangoproject.com/en/dev/ref/contrib/admin/).  
CRM app uses adaptive Admin HTML templates out-of-the-box.  
Django is an excellently documented framework with lots of examples.  
The documentation on the Admin site takes up only one web page.

💡 The **original idea** is that since Django Admin is already a professional object management interface with a flexible permissions system for users (view, change, add, and delete objects), all you need to do is create models for the objects (such as Leads, Requests, Deals, Companies, etc.) and add business logic.  
A **table view of CRM objects** with sorting and filtering by multiple fields enables users to quickly locate relevant information, prioritize tasks, and manage large volumes of data with greater efficiency.

**All this ensures**:

- **significantly easier project customization and development**
- **simpler project deployment and production server support**

The software package provides two websites:

1. CRM site for all users
2. Site for administrators

The **project is mature and stable**, and has been successfully used in real applications for many years.

## Main Applications

The CRM software suite consists of the following **main applications** and their models:

- **TASKS Management app**:
  (available to all users by default, regardless of their role)
  - Task (with related: files, chat, reminders, tags - see [task features](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_task_features.md))
    - subtasks
  - Memo (office memo) - see [memo features](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_memo_features.md)
    - tasks / project
  - Project (*tasks collection*):
  - ... (+ *4 more <a href="https://github.com/DjangoCRM/django-crm/tree/main/tasks/models" target="_blank">models</a>*)
- **CRM app**:
  - Requests (commercial inquiries)
  - Leads (potential customers)
  - Companies
  - Contact persons (associated with their companies)
  - Deals (like "Opportunities")
  - Email messages (sync with user email accounts)
  - Products (goods and services)
  - Payments (received, guaranteed, high and low probability)
  - ... (*+ 12 more <a href="https://github.com/DjangoCRM/django-crm/tree/main/crm/models" target="_blank">models</a>*)
[<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/pics/income_summary_thumbnail.png" alt="Analytical crm report" align="right" width="190px" style="float: right"/>](https://github.com/DjangoCRM/django-crm/blob/main/docs/pics/income_summary_screenshot.png)
- **ANALYTICS app**: ([detailed software overview](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_analytics_app_overview.md))
  - Income Summary report (*see [screenshot](https://github.com/DjangoCRM/django-crm/blob/main/docs/pics/income_summary_screenshot.png)*)
  - Sales funnel report
  - Lead source Summary report
  - ... (+ *5 more analytical reports*)
- **MASS MAIL app**:
  - Email Accounts
  - Email Messages (newsletters)
  - Email Signatures (user signatures)
  - Mailings

## Supporting Applications

The CRM package also contains **supporting applications** such as:

- Chat app (chat is available in every instance of a task, project, office memo and deal)
- VoIP app (contact clients from deals)
- Help app (dynamic help pages depending on user role)
- Common app:
  - 🪪 User profiles
  - ⏰ Reminders (for tasks, projects, office memos and deals)
  - 📝 Tags (for tasks, projects, office memos and deals)
  - 📂 Files (for tasks, projects, office memos and deals)

## Additional Functionality

- Web form integration: CRM contact form has built-in:
  - reCAPTCHA v3 protection
  - automatic geolocation
- User's email account integration and synchronization. Email messages are automatic:
  - saved in the CRM database
  - linked to the appropriate CRM objects (like: requests, leads, deals, etc.)
- VoIP callback to smartphone
- Sending messages via messengers (like: Viber, WhatsApp, ...)
- Excel Support: Import/export contact details with ease.

## Email Client

The Python CRM system includes a built-in email client that operates using **SMTP** and **IMAP** protocols.  
This enables Django-CRM to automatically store copies of all correspondence related to each request and deal within its database.  
The functionality ensures that even if communications occur through the user's external email account (outside the CRM).  
They are captured and organized within the system using a **ticketing mechanism**.

The CRM can integrate with email service providers (like Gmail) that require mandatory two-step authentication (using the **OAuth 2.0** protocol) for third-party applications.

## Mailing CRM

The CRM system includes a **bulk mailing** feature that allows users to send personalized newsletters to their contacts.  
Customer segmentation features allow you to create targeted email marketing campaigns, and these can be managed directly within the CRM interface.

## User Assistance  

- Each CRM page includes a link <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/question-mark.svg" alt="question-mark icon" style="vertical-align: bottom" width="25" height="25"> to a context-aware help page, with content dynamically tailored to the user's role for more relevant guidance.  
- Tooltips are available throughout the interface, providing instant information when hovering over elements like icons, buttons, links, or table headers.  
- A comprehensive [user guide](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_user_guide.md) file is also included for in-depth reference and support.  

## Elevate Your Team's Productivity with Collaborative CRM Solutions

This CRM is designed to enhance collaboration within teams and streamline project management processes.  
As a collaborative CRM, it allows users to create and manage memos, tasks, and projects with ease.  
[Office memos](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_memo_features.md) can be directed to department heads or company executives, who can then transform these memos into tasks or projects, assigning responsible persons or executors.  
[Tasks](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_task_features.md) can be individual or collective.  
Tasks provide features such as chat discussions, reminders, file sharing, creating subtasks, and sharing results.  
Users receive notifications directly in the CRM and via email, ensuring they stay informed.  
Each user has a clear view of their task stack, including priorities, statuses, and next steps, thereby enhancing productivity and accountability in collaborative customer relationship management.

## Project Localization

<img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/languages.svg" alt="django logo" width="30" height="30" style="vertical-align: bottom"> Customer service software is now available in **many languages:**  

`ar, cs, de, el, en, es, fr, he, hi, id, it, ja, ko, nl, pl, pt-br, ro, ru, tr, uk, vi, zh-hans`

Django CRM has full support for translation of interface, formatting of dates, times, and time zones.  

## Why Choose Django-CRM?

- **Self-Hosting**: The CRM application software is designed to be self-hosted, allowing you to have full control over your CRM data and environment. By self-hosting, you can customize the CRM to fit your specific business needs and ensure that your data remains private and secure.
- **Collaborative CRM**: Boost team productivity with tools for task management, project collaboration, and internal communication.
- **Automated email system**: Email marketing CRM integration and automatically saving copies of all correspondence associated with each request and deal in its database.
- **Analytical CRM**: Gain actionable insights with built-in reports like sales funnel, income summary, and lead source analysis.
- **Python and Django-Based**: No learning of a proprietary framework is required - all built on Django with an intuitive admin interface. The frontend and backend, based on Django Admin, make it much easier customization and development projects, as well as deploy and maintain a production server.

## Getting Started

Django-CRM can be easily deployed as a regular Django project.

📚 Please refer to:

- [Installation and Configuration Guide](https://github.com/DjangoCRM/django-crm/blob/main/docs/installation_and_configuration_guide.md)
- [User Guide](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_user_guide.md)
- or visit [Read The Docs](https://django-crm-admin.readthedocs.io)
- For unreleased changes, see [CHANGELOG](https://github.com/DjangoCRM/django-crm/blob/main/CHANGELOG.md)

If you find Django-CRM helpful, please ⭐️ **star** this repo on GitHub to support its growth!

### Compatibility

- <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/django-logo.svg" alt="django logo" width="30" height="30" style="vertical-align: middle"> Django 5.1.x, 5.2.1+ (LTS - long-term support release)
- <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/python-logo.svg" alt="python logo" width="30" height="30" style="vertical-align: middle"> Python 3.10+
- <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/mysql_logo.svg" alt="mysql logo" width="30" height="30" style="vertical-align: middle"> MySQL 8.0.11+
- <img src="https://github.com/DjangoCRM/django-crm/raw/main/docs/site/icons/postgresql_logo.svg" alt="postgresql logo" width="30" height="30" style="vertical-align: middle"> PostgreSQL 14+  

## Contributing

Contributions are welcome! There is room for improvements and new features.  
Check out our [Contributing Guide](https://github.com/DjangoCRM/django-crm/blob/main/CONTRIBUTING.md) to learn how to get started.  
Every contribution, big or small, makes a difference.

## License

Django-CRM is released under the AGPL-3.0 license - see the [LICENSE](https://github.com/DjangoCRM/django-crm/blob/main/LICENSE) file for details.

## Credits

- Google material [icons](https://fonts.google.com/icons).
- [NicEdit](https://nicedit.com) - WYSIWYG Content Editor.
- All resources used under other licenses.
