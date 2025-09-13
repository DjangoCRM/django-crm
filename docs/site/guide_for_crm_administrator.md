# Django CRM Administrator's Guide

In order for users to be successful in [CRM and task management software](https://djangocrm.github.io/info/){target="_blank"},
the administrator must do a good job as well as help other users with their work.
To do this, the administrator must study all the previous sections of this guide,
as well as the CRM software [installation](installation.md) and configuration guide.

## Admin site

The Admin site is intended for experienced administrators and developers.
Use this site only in cases where the action cannot be performed on the CRM site.
This allows you to see the CRM work on behalf of ordinary users, which helps in solving their problems.

### Adding users

Users receive the CRM address and login data from the Administrator.
The Administrator must assign the appropriate roles to each user and,
if necessary, specify the department and set up additional permissions.  
The administrator must also ensure that the sales manager user has access to the email account from which he will send messages to clients.
See instructions for [adding CRM users](adding_crm_users.md).

### Deleted object history

In some cases, users may need to see the history of deleted objects.  
This can be done here (available from v1.5):  
`(ADMIN site) Home › Administration › Log entries`

### Mass transfer of companies to another sales manager

This can be done using the action drop-down menu on the company's page.
The contact persons will be transferred automatically.

### Mass contacts objects

To ensure that recipients always receive mailing messages from the same email account,
mass contact objects are automatically created.
These objects correspond to the recipient of the mailing and the mail account from which the messages are sent to him.
