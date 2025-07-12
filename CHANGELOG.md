# Changelog of Django CRM software

All notable changes to the [Django CRM project](https://github.com/DjangoCRM/django-crm) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- Types of changes: Added, Changed, Deprecated, Improve, Fixed, Removed, -->
<!-- ## Unreleased -->

## [1.5.0] - 2025-07-12

### Added

- Added visualization of mailing messages:
  - on the list page of these messages
  - on mailing list page
- The site for administrators has been expanded to provide access to logs of user actions on CRM objects. In addition to searching and filtering by many parameters, this allows administrators to see the history of all objects, including deleted ones.
- Added the URL of the page "you have unsubscribed successfully" to the context of the preview of messages for the mailing.
- The ability to rewrite the date and time format for a more compact data presentation.  
  This can be done in the `webcrm/datetime_settings.py` file.
- Added functionality to exclude recipients from created mailing.
- New translations.

### Fixed

- Added a delay to ensure Django starts before executing massmail and avoid a RuntimeWarning.
- Added distinct() to `get_queryset` in MemoAdmin to eliminate duplicate results.

#### Full Changelog: [v1.4.0...v1.5.0](https://github.com/DjangoCRM/django-crm/compare/v1.4.0...v1.5.0)

## [1.4.0] - 2025-06-21

### Added

- The ability to create a new commercial request based on an existing one.
- An icon has been added to the memos on the list page, displaying the presence of new messages in  
  the memos chat and the ability to immediately go to the selected chat.
- Dynamic tooltip for task sorting toggle.
- The number of Request fields available for modification via the administrators' site has been expanded.
- Validation for mailing status and dynamic user hints.
- Flag for mass mailing only during business hours.
- Search field on the email accounts list page.
- Expand newsletter mailing documentation with detailed usage instructions.

### Changed

- To improve the performance of the CRM and reduce peak RAM consumption,  
  annotation is now performed not on the entire queryset, but only on the objects of the current changelist page.
- Moved Massmail settings from settings.py to Admin web UI by @Ishubhammohole in #229  
  (**Update your settings:** `(ADMIN site) Home > Settings > Massmail Settings`).

#### Full Changelog: [v1.3.1...v1.4.0](https://github.com/DjangoCRM/django-crm/compare/v1.3.1...v1.4.0)

## [1.3.1] - 2025-05-23

### Changed

- Removed Skype Support from the CRM software as it is no longer supported by Microsoft.
- Enhance currency rate backend error handling and update tests accordingly.
- Refactor currency rate backend tests for clarity and efficiency
- Changed the company query counter to not show dashes if the value is missing

### Added

- Add scrollable wrapper for long mailing error notifications by @MULTidll in #217
- Add dynamic tooltip for deal sorting toggle

### Fixed

- Fix some translations

#### Full Changelog: [v1.3.0...v1.3.1](https://github.com/DjangoCRM/django-crm/compare/v1.3.0...v1.3.1)

## [1.3.0] - 2025-05-11

### Added

- Compatibility with Django 5.2.1 (LTS - long-term support release)
- Matching of a company in the database by the contents of the alternative names field.
- Action menu to remove stop phrases that are no longer used.
- Visual marking of duplicate commercial requests.
- Translations of CRM software into the following languages:
  - Romanian
  - Hebrew
- Warning message “Specify products” if a Request is saved without specifying products.

### Improve

- The algorithm for creating mailings has been simplified.
- Setting the reminder time check interval is now available through the admin site instead of using a settings file.
- Improve the test of the current backend for loading currency rates.

### Fixed

- Some minor fixes

#### Full Changelog: [v1.2.2...v1.3.0](https://github.com/DjangoCRM/django-crm/compare/v1.2.2...v1.3.0)

## [1.2.2] - 2025-03-22

### Added

- Added installation and configuration guide in Spanish

### Improved

- Improved help text in the `Reminder` model

### Fixed

- Removed duplicate notification texts
- Fixed Portuguese translation
- Fixed Vietnamese translation
- Fixed Turkish translation
- Fixed Nederlands translation
- Fixed Polish translation

#### Full Changelog: [v1.2.1...v1.2.2](https://github.com/DjangoCRM/django-crm/compare/v1.2.1...v1.2.2)

## [1.2.1] - 2025-03-01

### Fixed

- Fixed display of help page in English if it is not available in the current language.
- Fixed translations of CRM software## Unreleased
  - Spanish
  - German
  - French
  - Hindi
  - Chinese

### Added

Django-CRM user guide in Spanish

#### Full Changelog: [v1.2.0...v1.2.1](https://github.com/DjangoCRM/django-crm/compare/v1.2.0...v1.2.1)

## [1.2.0] - 2025-02-21

### Added

- Translations of CRM software into the following languages:
  - Hindi
  - Turkish
  - Polish
  - Arabic
  - Chinese
  - Japanese
  - Korean
  - Czech
  - Vietnamese
  - Greek
  - Indonesian

- ["Task-board & road map"](https://github.com/users/DjangoCRM/projects/1/views/1) project

### Fixed

- Correct the arguments of the filter for payments received in the previous period.
- Fix some typos in text messages.

#### Full Changelog: [v1.1.0...v1.2.0](https://github.com/DjangoCRM/django-crm/compare/v1.1.0...v1.2.0)

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
