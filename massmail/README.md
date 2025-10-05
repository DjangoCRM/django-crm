# Massmail Module - Email Marketing Software

The **Massmail** module is a core component of the [Mailing CRM](https://github.com/DjangoCRM/django-crm/) platform, providing advanced email marketing and newsletter capabilities directly within your CRM system. This module transforms Django CRM into a powerful solution for businesses seeking a **CRM with email integration**, enabling both individual and bulk communications with clients, leads, and companies.

## Overview

The Massmail module is designed for organizations that require a **CRM and email marketing software** solution. It allows users to:

- Create, manage, and send marketing emails and newsletters to contacts, leads, and companies.
- Use multiple email accounts, including integration with services like Gmail and other SMTP providers.
- Track the progress and status of mailings within the CRM interface.
- Ensure compliance with best practices by supporting unsubscribe functionality and business hour restrictions.

With Massmail, Django CRM becomes a [CRM with email](https://djangocrm.github.io/info/features/massmail-app-features/) capabilities, supporting both day-to-day client communication and large-scale marketing campaigns.

## Key Features

- **Automated Email System**: Schedule and send bulk emails to selected recipients or filtered groups.
- **Recipient Management**: Target contact persons, leads, or companies stored in the CRM database.
- **VIP Handling**: Send mailings from the main sales manager account only to VIP recipients to improve deliverability.
- **Multiple Email Accounts**: Assign and use different email accounts for various sales managers.
- **Business Hours Control**: Restrict mailings to working hours and avoid sending on weekends.
- **Unsubscribe Support**: Provide recipients with an unsubscribe link, redirecting them to a custom company web page.
- **Admin Settings**: Configure all massmail settings via the Django Admin interface (no code changes required).
- **Integration**: Works with any email service provider, making it a flexible CRM and email marketing solution.

## Directory Structure

- `admin.py`, `admin_actions.py`: Admin interface and custom actions for managing mailings.
- `backends/`: OAUTH2 Email backend implementations for getting access token.
- `forms/`: Forms for user input and configuration.
- `models/`: Data models for email accounts, messages, signatures, and recipient queues.
- `site/`: Admin customizations for massmail-related models.
- `templates/`: HTML templates for email content and admin UI.
- `templatetags/`: Custom template tags for email building.
- `utils/`: Utility functions for filtering, sending, and managing emails.
- `views/`: Views for handling file uploads, message previews, recipient selection, and more.

## Settings

All massmail settings are managed via the Django Admin interface.  
Home > Settings > Massmail Settings
(This was moved from settings.py in v1.4.0)

- **Business Hours**: Enable or disable sending during working hours.
- **Unsubscribe URL**: Specify the URL to which recipients are redirected when unsubscribing.
- **Email Account Assignment**: Assign email accounts to sales managers for targeted mailings.

## Unsubscribe Functionality

To comply with email marketing standards, every message should include an unsubscribe link. Configure the unsubscribe URL in the admin settings, and ensure your email templates use the `{{ unsubscribe_url }}` tag.

## Best Practices

- Only send mailings to recipients who have opted in.
- Use the VIP feature to protect your main email account reputation.
- Regularly update your recipient lists and email templates.

## Why Use Massmail?

- Integrates CRM and email marketing in one platform.
- Flexible CRM with email capabilities for both transactional and marketing communications.
- Works with any email provider, supporting CRM with email integration for your business.
- Empowers your team with an automated email system for efficient outreach.

## Documentation

For detailed usage instructions, see the [official documentation](https://django-crm-admin.readthedocs.io/en/latest/newsletter_mailing/.

## Related core modules

- [CRM module](https://github.com/DjangoCRM/django-crm/blob/main/crm/README.md)
- [Analitics module](https://github.com/DjangoCRM/django-crm/blob/main/analytics/README.md)
- [Tasks module](https://github.com/DjangoCRM/django-crm/blob/main/tasks/README.md)

---

Massmail makes Django CRM a complete CRM and email marketing software solution, ready to power your business communications and campaigns.
