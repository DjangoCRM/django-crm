# Django CRM Administrator's Guide

In order for users to be successful in [CRM and task management software](https://djangocrm.github.io/info/){target="_blank"},
the administrator must do a good job as well as help other users with their work.
To do this, the administrator must study all the previous sections of user guide,
as well as the CRM software [installation](installation.md) and configuration guide.

## Admin site

The Admin site is intended for experienced administrators and developers.
Use this site only in cases where the action cannot be performed on the CRM site.
This allows you to see the CRM work on behalf of ordinary users, which helps in solving their problems.

## Adding users

Users receive the CRM address and login data from the Administrator.
The Administrator must assign the appropriate roles to each user and,
if necessary, specify the department and set up additional permissions.  
The administrator must also ensure that the sales manager user has access to the email account from which he will send messages to clients.
See instructions for [adding CRM users](adding_crm_users.md).

## Deleting user accounts in a CRM

Deleting user accounts in a Customer Relationship Management system is generally not recommended because it permanently removes the user's entire history, including emails, tasks, and deal records. This practice is discouraged for the following reasons:

- **Loss of Audit Trail:** The CRM serves as a record of who did what and when. Deleting a user erases this accountability, making it difficult to track the history of specific accounts or deals.
- **Data Integrity:** Deleting a user often deletes the "owner" of the data, which can break relationships between records and lead to orphaned data.
- **Reinstatement Difficulties:** If a user returns to the company, you cannot simply reactivate a deleted account. You would have to recreate the profile and manually re-enter all their historical data.
- **Compliance and Legal Requirements:** Many industries are subject to data retention laws (such as GDPR or HIPAA) that require keeping records of user activity, even after an employee leaves.

### The Recommended Alternative

Instead of deleting a user account, administrators should simply deactivate it.
This keeps the user's profile and history intact in the system while preventing them from logging in or creating new records.  
Administrators can do it via the admin website, or they can turn the account off directly from the individual user’s profile page inside the CRM interface.

## Deleted object history

In some cases, users may need to see the **history of deleted objects**.  
This can be done here (available from v1.5):  
`(ADMIN site) Home › Administration › Log entries`

## Mass transfer of companies to another sales manager

This can be done using the action drop-down menu on the company's page.
The contact persons will be transferred automatically.

## Resolving Country Mismatch Notifications

If you receive notifications indicating that a specific country does not exist in the CRM,
it is often due to a discrepancy between the name stored in the system and the name provided by external data sources. Common causes include:

- **Name Changes:** The official name of the country has changed  
(e.g., “Republic of Macedonia” → “Republic of North Macedonia”).
- **Geolocation Services:** Connected geolocation services may use abbreviated versions  
(e.g., "USA" instead of "United States") rather than the legally full name.

### Using the Alternative Names Field

To ensure accurate country matching during automatic query additions, administrator should utilize the **Alternative Names** field within the **Country object**.

**How to configure:**  
Navigate to the **Country object** in the CRM configuration.  
`(Admin site) Home > CRM > Countries`

**Example Configuration:**

- **Name:** United States
- **Alternative Names:** USA, US, United States of America

### Supporting Local Languages and Translations

Administrators can also use the Alternative Names field to support localization. 
You may populate the primary Name field in the local language and provide English or other language translations in the Alternative Names field.

- **Name:** Deutschland
- **Alternative Names:** Germany

## Mass contacts objects

To ensure that recipients always receive mailing messages from the same email account,
mass contact objects are automatically created.
These objects correspond to the recipient of the mailing and the mail account from which the messages are sent to him.
