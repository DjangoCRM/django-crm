# Changelog of Django CRM software

All notable changes to the [Django CRM project](https://github.com/DjangoCRM/django-crm) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- Types of changes: Added, Changed, Deprecated, Improve, Fixed, Removed, -->
<!-- ## Unreleased -->

## [1.1.0] - 2025-01-25

### Added

Translations of CRM software into the following languages:

- Brazilian Portuguese
- Dutch
- French
- German
- Italian (by @anselmix80)
- Russian
- Spanish
- Ukrainian

### Improve

- `settings.py` to ensure stable execution of tests when language settings are overridden

### Fixed

- Test for receiving email notifications about subtask completion (#134)

#### Full Changelog: [v1.0.0...v1.1.0](https://github.com/DjangoCRM/django-crm/compare/v1.0.0...v1.1.0)

## [1.0.0] - 2025-01-11

### Added

- The ability to exclude some currencies from auto-update
- Recipient/sender names in CRM workflow messages and system notifications about sending/receiving emails.
- Draft field for Memo `fieldsets` in admin
- Allow the current user to be assigned to memo
- The ability to search for a company by its alternative name

### Fixed

- translation of the Email receipt notification.
- exception caused by chat in user profile.

### Changed

- The "add reminder" button on the main page has been removed.
- The display of the "massmail" field in the "Company," "Contact" and "Lead" models has been changed depending on its value.

### Full Changelog: [v0.99...v1.0](https://github.com/DjangoCRM/django-crm/compare/v0.93...v1.0.0)

## [0.93] - 2024-10-20

### Added

- Visualization of the counterparty (Lead, Company, Company Contact) status as a recipient of newsletters: 'subscribed' / 'unsubscribed'
- A filter by a custom date range has been added to the Payments, Shipments and Sales Report views
- The `get_crm_url` method to `BaseContact` model
- A detailed guide on how to update Django CRM software
- The 'disqualified' and 'massmail' fields to the counterparty models as well as to the export settings
- New public email domains to database (fixture)
- The filtering logic to exclude disqualified massmail recipients. Introduced new warning and error messages for handling excluded recipients and cases where no valid recipients remain.


### Changed

- Visualization of the status (pending / processed) of a commercial request in the Requests view
- The verbose name of the "owner" field of the Lead, Company, Company Contact models from "Owner" to "Assigned to"
- The logic for adding a tag filter in CRM application views
- The URL method from `get_absolute_url` to `get_crm_url` to correctly generate the counterparty's link in the CRM interface
- The tag `fieldsets` in Deal change view
- Bump requirements

### Improve

- Request owner change logic to check if the owner is part of the sales managers group before updating related objects (Lead, Company, Company Contact)
- The unsubscribe function to handle cases where the recipient does not exist.

### Fixed

- Fix for creating email notification subject for office memo received
- Fix `queryset` method of TagFilter class

### Full Changelog: [v0.92...v0.93](https://github.com/DjangoCRM/django-crm/compare/v0.92...v0.93)

## [0.92] - 2024-09-22

### Added

#### Translation

- Personal messages to non-current users are translated into the language specified in their profile
- Messages available to a user group are translated into the default language if at least one member of the group has chosen a language different from other members of the group

### Changed

- The algorithm for translating CRM system messages

### Full Changelog: [v0.91...v0.92](https://github.com/DjangoCRM/django-crm/compare/v0.91...v0.92)

## [0.91] - 2024-07-30

### Full Changelog: [v0.90...v0.91](https://github.com/DjangoCRM/django-crm/compare/v0.90...v0.91)

## [0.90] - 2024-07-21

### Initial public release
