# CRM Models Directory

This directory contains the core data models for the [CRM application](https://djangocrm.github.io/info/features/crm-app-features/) of a modular Django-based customer relationship management app. The CRM app is the foundation of the system and is designed for extensibility, multi-database compatibility, and integration with other modules such as Analytics, Tasks, and Massmail.

## Overview

The models in this directory define the main business entities and relationships for the [CRM free software](https://github.com/DjangoCRM/django-crm/). They are implemented using Django's ORM and avoid database-specific fields to ensure compatibility with PostgreSQL and MySQL.

This CRM in Python is suitable for organizations seeking a robust, open-source customer relationship management solution.

## Key Features

- **Multi-database compatibility:** No use of database-specific fields or constraints.
- **Ownership and Assignment:** Most models include an `owner` field (the user responsible for the object). Some models, such as `Request` and `Deal`, also have a `co_owner` field for collaboration and shared responsibility.
- **Extensible Relationships:** Models use ForeignKey, ManyToManyField, and GenericRelation for flexible linking between entities.
- **Internationalization:** All verbose names and help texts are translatable using Django's i18n framework.
- **Integration Ready:** Models are designed to work with other CRM modules ([Analytics](https://github.com/DjangoCRM/django-crm/blob/main/analytics/README.md), [Tasks](https://github.com/DjangoCRM/django-crm/blob/main/tasks/README.md), [Massmail](https://github.com/DjangoCRM/django-crm/blob/main/massmail/README.md), etc.).

## Main Models

### Company

Represents a client or partner organization. Includes fields for name, alternative names, website, contact details, registration number, and links to country, city, type, and industry.

### Contact

Represents an individual contact person, linked to a company. Stores personal details, email addresses, phone numbers, and location.

### Deal

Tracks business opportunities or sales. Includes fields for name, next steps, stage, amount, currency and links to related company, contact, lead, and request.

### Lead

Represents a potential client or opportunity. Stores personal and company information, qualification status, and links to related contacts and companies. In some cases, a Lead can be converted into a Company and a Contact person.

### Request

Captures incoming requests or inquiries. Includes information about the requester, their company, products/services of interest, and assignment fields (`owner`, `co_owner`).

### Product & ProductCategory

Defines products and their categories, including pricing, description, and classification as goods or services.

### Tag

Allows categorization and filtering of objects using user-defined tags.

### Country & City

Stores geographic information for companies and contacts.

### Payment, Output, Shipment

Handles financial transactions, product outputs, and shipments related to deals.

### Supporting Models

- **ClientType:** Types of clients (e.g., reseller, end customer).
- **Industry:** Industry classification for companies.
- **Stage:** Sales or deal stages.
- **LeadSource:** Source of leads (e.g., website, exhibition).
- **ClosingReason:** Reasons for closing deals.

When installing CRM software, the database is automatically populated with default auxiliary model instances. In the future, these instances can be changed, deleted or added. For example, you can change the set of reasons for closing deals in accordance with a specific type of business.

## Ownership Fields

- `owner`: The primary user responsible for the object ("appointed to").
- `co_owner`: (Optional) A secondary user sharing responsibility (used in models like `Request` and `Deal`).

These fields support assignment, permissions, and workflow features throughout the CRM.

## Internationalization

All model fields use `gettext_lazy` for verbose names and help texts, supporting multi-language deployments.

## File Structure

- `base_contact.py`: Abstract base classes for contacts and counterparties.
- `company.py`, `contact.py`, `deal.py`, `lead.py`, `request.py`: Main business entities.
- `country.py`: Country and city models.
- `product.py`, `tag.py`, `payment.py`, `output.py`: Supporting models for products, tags, payments, and outputs.
- `others.py`: ClientType, Industry, Stage, LeadSource, ClosingReason.
- `crmemail.py`: Email integration for CRM objects.
- `__init__.py`: Imports all models for easy access.

## Usage

These models are used throughout the CRM application to manage customer relationships, track sales and leads, handle requests, and categorize products. They provide a structured way to store and retrieve data related to customers, contacts, deals, and other business entities.
They form the basis of all analytics, task management and mass mailing functions.
