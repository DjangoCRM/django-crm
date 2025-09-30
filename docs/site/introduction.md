## Introduction

📈 Django CRM offers [powerful tools](guide_for_company_executives.md): the [**CRM Task management solution**](https://djangocrm.github.io/info/features/tasks-app-features/){target="_blank"} for company-wide task tracking and office memos,
the **CRM Module** for managing customer data and launching targeted email campaigns, and [**CRM analytics software**](https://github.com/DjangoCRM/django-crm/){target="_blank"} for insights into sales and business performance.
The use of CRM by companies allows them to improve the sales performance of their products and services.
The more complex and time-consuming the sales process, the greater the improvement.  

[Django-CRM](https://github.com/DjangoCRM/django-crm/){target="_blank"} is an application with a web interface. Therefore, you can use an internet browser on your computer, tablet and smartphone to work with it.

To make your work easier, CRM provides help pages and tooltips when you hover your mouse over certain page elements such as icons, buttons, etc.  
![CRM tooltip screenshot](https://github.com/DjangoCRM/django-crm/raw/main/docs/site/img/crm_tooltip_screenshot.png)

Many pages have an <span style="vertical-align: baseline"><img src="../icons/question-mark.svg" alt="Question-mark icon" width="25" height="25"></span> icon in the upper right corner. Clicking on it will open the help page.

CRM is a powerful software package that requires customization and integration with other services. If something does not work as expected - report it to your CRM administrator.

The CRM database can contain a large amount of business information.
Therefore, a user's abilities and access to CRM sections are determined by a set of permissions (roles) assigned to the user by the administrator.

!!! Note

    To gain access to the CRM system, please contact your administrator.

Many **objects** are created and stored in database. Such as [**Tasks**](tasks_section.md#tasks), [**Memos**](tasks_section.md#memos), [**Leads**](operator_and_sales_manager_roles.md#lead-object), [**Deals**](guide_for_sales_manager.md#deal-object), **Emails**, etc.
The CRM home page lists the sections and frequently used objects available to the user. To see all the available objects you need to click on the section title.

In relation to specific objects, a user may have all or only some of the following [permissions](adding_crm_users.md#permissions-for-users):

- *add*
- *change*
- *delete*
- *view*

These permissions can be permanent and dynamic (*dependent on conditions*).  
For example, the owner (*author*) of a memo can always see it.  
But he loses the permissions to change it and the permissions to delete it after it has been reviewed by the manager.  
Most objects have an owner. As a rule, it is the user who created this object. But some objects can be transferred to another user (*another owner is assigned*).

All objects have an **ID**. It is indicated on the object page.  
You can search for an object by its ID.  
To do this, write "ID" and its value together in the search bar.

Objects can have a link to other objects. For example, a memo object will have a relationship with the created task and attached files.  
When you delete a memo, all linked objects will be deleted.  
The list of deleted objects will be shown on the deleting confirmation page.

### History of the object

The history of changes to objects is saved. By clicking the "HISTORY" button (*see screenshot above*), you can see who changed what and when.
The history of an object is retained even after it has been deleted.

!!! Note

    To view the history of a deleted object, contact the administrator (available from v1.5).

### File object

📎 Many objects (such as: Deal, Email, Task, Memo) allow you to attach files. In CRM, files are also stored as objects.
The file object does not contain the file itself, but only a link to it. There can be many objects of the same file in the CRM system.  
Therefore, when deleting a file object, only the reference to the file will be deleted.
The file will be deleted when the last link to it is deleted in CRM.  
For example, an office memo has an attached file. An object from this file will also be attached to a task created from it.
If you delete a task, the file object will also be deleted, but not the file itself.
Because there is still a file object attached to the memo. If this last file object is also deleted, then the file will be deleted.
