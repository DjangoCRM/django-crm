
# Django CRM Documentation Directory

This directory contains all documentation-related resources for the [CRM application software](https://DjangoCRM.github.io/info/).  
Whether you're a new user looking for installation instructions or a contributor preparing a pull request, this folder provides the structured documentation and supporting materials needed to work with Django CRM effectively.

## Directory Structure

- `/README/`  
  Translations of the repository's main `README.md` file into multiple languages.

- `/pics/`  
  Screenshot assets used in the translated README files and user documentation.

- `/site/`  
  Source files for the official [Django CRM documentation](https://django-crm-admin.readthedocs.io) site.  
  Built with **Markdown** using the **Material for MkDocs** theme and hosted on **Read the Docs**.

## Markdown Documentation Files

The following guides are available in Markdown format:

- **`installation_and_configuration_guide.md`**  
  Step-by-step guide for installing and configuring Django CRM for local development or production deployment:

    - [CRM software installation](https://github.com/DjangoCRM/django-crm/blob/main/docs/installation_and_configuration_guide.md#project-installation)
    - [Configuration of the CRM application](https://github.com/DjangoCRM/django-crm/blob/main/docs/installation_and_configuration_guide.md#settings-of-django-crm)

- **`django-crm_user_guide.md`**  
  Comprehensive user manual for working with core CRM features such as leads, contacts, opportunities, and pipelines:

    - [User guide for CRM](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_user_guide.md)
    - [CRM Administrator's Guide](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_user_guide.md#table-of-contents#django-crm-administrators-guide)

- **`crm_system_overview.md`**  
  A [general overview of Django CRM](https://github.com/DjangoCRM/django-crm/blob/main/docs/crm_system_overview.md): its goals, main components, and how they integrate.

- **`django-crm_analytics_app_overview.md`**  
  Description of the built-in [Analytics application](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_analytics_app_overview.md): what it does and how it supports CRM reporting.

- **`crm_app_features.md`**  
  In-depth explanation of the primary [CRM app features](https://github.com/DjangoCRM/django-crm/blob/main/docs/crm_app_features.md), including lead and contact management.

- **`django-crm_task_features.md`**  
  Overview of [CRM Tasks](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_task_features.md) capabilities in Django CRM.

- **`django-crm_memo_features.md`**  
  Description of [memo/note-taking](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_memo_features.md) features integrated into the CRM.

- **`pull_request_template.md`**  
  Template to guide contributors in submitting effective pull requests to the repository.

## For Contributors

We welcome contributions! Here's how you can get involved:

### Improving Documentation

If you spot inaccuracies, unclear sections, or missing information, feel free to edit the appropriate Markdown files. All documentation updates should be consistent with the existing tone and structure.

When editing or adding pages under `/site/`, make sure your changes render properly using MkDocs. To preview locally:

```bash
# Install dependencies
pip install -r docs/site/requirements.txt

# Serve the documentation site locally
mkdocs serve
````
Then, open your browser and navigate to:  
`http://127.0.0.1:8000/`

### Adding Screenshots or Visual Aids

Place all visual assets (screenshots, diagrams) into the `/pics/` subdirectory. Use relative paths when embedding them in documentation files.

### Translating the README

If you'd like to contribute a translation of the project’s main README, copy the original file into the `/README/` directory and follow the naming convention used for other translations. Include your language code in the filename (e.g., `README.fr.md` for French).

## Hosting and Build Information

* The documentation site is hosted on [Read the Docs](https://readthedocs.org/).
* The site is generated using [MkDocs](https://www.mkdocs.org/) with the [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) theme.

---

Thank you for helping us improve Django CRM’s documentation!
