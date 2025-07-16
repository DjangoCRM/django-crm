# Analytics App for Django CRM

Welcome to the **Analytics** app, a core component of [Django CRM](https://github.com/DjangoCRM/django-crm/), the open-source analytical CRM. This module provides powerful [crm analytics software](https://djangocrm.github.io/info/features/analytics-app-features/) capabilities, enabling managers and sales teams to make data-driven decisions with comprehensive reports and visualizations.

## Overview

The Analytics app is bundled with Django CRM and enabled by default. It leverages proxy models of the original core CRM models to generate analytical reports. All users with the appropriate role (company manager, sales manager, CRM administrator) can access the Analytics section on the CRM website.

**Key features include:**

- **Income Summary Report:** Detailed breakdown of deals, products, and payment volumes, with forecasts and historical comparisons.
- **Sales Funnel Report:** Visualization of sales stages to identify bottlenecks and opportunities.
- **Sales Report:** Summarizes sales performance, including total sales and average deal size.
- **Requests Summary:** Overview of commercial inquiries and conversion rates.
- **Lead Source Summary:** Analysis of lead sources and their effectiveness.
- **Conversion Summary:** Tracks conversion rates and highlights areas for improvement.
- **Closing Reason Summary:** Summarizes reasons for deal closure, both successful and unsuccessful.
- **Deal Summary:** Comprehensive overview of all deals, their status, and associated products/services.

## Filters and Customization

A wide range of filters are available on report pages, allowing users to generate reports by:

- Departments
- Sales managers
- Products
- Lead sources
- Custom time intervals
- And more

This flexibility ensures that users can focus on the metrics most relevant to their business needs.

## 📊 Visualization

To simplify customization and eliminate external dependencies, **bar charts** are used for graphical visualization of reports. All diagrams and tables are rendered using built-in templates, making it easy to adapt the look and feel to your requirements.

## 📂 Directory Structure

The **analytics** directory contains the code and resources for the built‑in analytics CRM features:

- `/site/` — Admin classes for each report type on the CRM site
- `/templates/` — HTML templates for analytics reports and visualizations
- `/utils/` — Helper functions and snapshot management
- `/migrations/` — Database migrations for analytics models
- `models.py` — Proxy models for CRM analytics
- `admin.py` — Admin site configuration for analytics models

## 🔗 Integration

The Analytics app is tightly integrated with other CRM modules, ensuring all relevant data is captured and analyzed. No additional installation steps are required—just ensure the CRM is installed and configured.  
All analytics models are implemented as proxy models of the core CRM:  
`Deal`, `Lead`, `Request`, `Contact`, etc.  
This ensures that the analytics CRM layer remains in sync with primary data schema while allowing you to extend or override report logic without altering core tables.

## Access and Permissions

Access to analytics reports is controlled by user roles. By default, company managers, sales managers, and CRM administrators have access. Access can also be granted to individual users regardless of their role.

## Contributing

We welcome contributions to improve the **crm analytical tools** and expand the range of **crm sales analytics** features. To contribute:

1. Fork the repository and clone your fork.
2. Create a new branch for your feature or bugfix.
3. Write clear, well-documented code and tests.
4. Submit a pull request with a detailed description of your changes.

**Areas for contribution:**

- New report types and visualizations
- Additional filters and customization options
- Performance improvements
- Documentation and translations

### Adding New Analytical Reports

To add a new report:

1. Create a new proxy model if you need custom CRM data aggregation.
2. Define the report logic in a new Python file within the `/site/` directory.
3. Create a corresponding HTML template in the `/templates/analytics/` directory.
4. Wire up URLs in `urls.py`.

## Support

For questions, issues, or feature requests, please use the [GitHub Issues](https://github.com/DjangoCRM/django-crm/issues) page.

---

For more information, see the [Analytics App Overview](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_analytics_app_overview.md) and the [Django CRM documentation](https://django-crm-admin.readthedocs.io).
