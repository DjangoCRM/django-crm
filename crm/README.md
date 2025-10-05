# CRM Module

This directory contains the core implementation of the [customer relationship management app](https://DjangoCRM.github.io/info/) for the Django CRM project.  
Django CRM is a [free crm management software](https://github.com/DjangoCRM/django-crm/) solution designed to help businesses manage leads, contacts, companies, deals, payments, and communications efficiently.
As the foundation of this CRM application software, it enables teams to effectively process leads, track deals, and stay informed through integrated reporting and communication tools.

## Overview

The `/crm` directory provides the main logic for the CRM application software.  
It is responsible for handling all essential operations related to client management, sales processes, and communication tracking.  
While Django CRM includes additional modules such as Analytics, Tasks, and Email Marketing, the CRM module is the foundation of the system.

## 🔑 Key Features

### 📨 Commercial Requests Handling

* Automatically create requests from web forms or incoming emails.
* Detect and associate related companies or contacts.
* Use filters to exclude generic domains (e.g., Gmail) and spam via stop phrases or banned names.
* Group and count pending requests for daily task prioritization.
* Geolocation support for request sources based on IP address.
* Filter out spam or irrelevant requests.

This functionality transforms the CRM into a responsive crm email management system, especially effective for high-volume client intake teams.

---

### 👥 Lead, Contact, and Company Management

* Detect existing entities in the database to avoid duplicates.
* Convert new Leads into formal Companies and Contacts.
* Maintain detailed records of interactions, relationships, and status changes.

The CRM supports structured handling of business relationships, making it an effective client relationship software for B2B environments.

---

### 💼 Deal Lifecycle and Sales Management

* Create Deal (oportunity) objects from validated Requests.
* Track deal progress through custom pipeline stages (e.g., qualification, proposal, negotiation).
* Visual status indicators, logs, and default sorting make the system intuitive.
* Close deals with outcome classification (won/lost) for future reporting.

Deals form the core workflow for sales teams using this free CRM management software.

---

### 💵 Payments and Currency Support

* Manage multiple currencies with exchange rate tracking.
* Distinguish between national and reporting currencies.
* Link payments directly to Deals and include them in analytics.

---

### 📧 Email Integration

* Send, receive, and associate emails with Requests and Deals.
* SMTP and IMAP support for complete crm email management.
* Unique ticket IDs for threading email conversations.
* Manual and automated import of letters, including attachments.

---

### 📦 Shipment Tracking

* Specify shipment details and associate with Deals.
* Keep real-time visibility of shipping status for all stakeholders.

---

### 🔌 Integrations and Automation

* Web form integration with CAPTCHA and geolocation.
* Excel support for import/export of core CRM entities.
* All CRM data is fully accessible to other modules (e.g., [Analytics](https://github.com/DjangoCRM/django-crm/blob/main/analytics/README.md), [Tasks](https://github.com/DjangoCRM/django-crm/blob/main/tasks/README.md), [Email Marketing](https://github.com/DjangoCRM/django-crm/blob/main/massmail/README.md)).

---

## 🔐 Access Control

The CRM module supports role-based access, ensuring users only interact with data relevant to their responsibilities. This protects sensitive information while making the UI more relevant for each user.

---

## 📚 Documentation

For full documentation, visit the [official CRM manual](https://django-crm-admin.readthedocs.io/) or explore the [CRM features overview](https://github.com/DjangoCRM/django-crm/blob/main/docs/crm_app_features.md).

---

## 📁 Directory Structure

The `/CRM` directory includes Django models, views, templates, and logic for:

- `admin.py` — Admin interface customizations for the CRM models.
- `apps.py` — App configuration.
- `settings.py` — App-specific settings.
- `urls.py` — URL routing for CRM views.
- `backends/` — Integrations with external data sources and services.
- `fixtures/` — Initial data for CRM entities (e.g., countries, currencies, deal stages).
- `forms/` — Django forms for data entry and validation.
- `migrations/` — Database schema migrations.
- `models/` — Core data models: Company, Contact, Lead, Deal, Payment, Product, Tag, etc.
- `site/` — Custom admin site classes and admin logic.
- `templates/` — HTML templates for admin and CRM views.
- `utils/` — Utility functions for data processing, email handling, permissions, and more.
- `views/` — Business logic for handling requests, forms, and user actions.


## Contributing

- To contribute to the CRM application software, edit or add files in this directory.
- Follow Django best practices for models, views, and forms.
- Add fixtures for new data types in the `fixtures/` directory.
- Write tests for new features and bug fixes.
- Submit pull requests using the provided template.


