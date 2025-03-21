## Introduction

📈 The use of CRM by companies allows them to improve the sales performance of their products and services.  
The more complex and time-consuming the sales process, the greater the improvement.  

[Django-CRM](https://github.com/DjangoCRM/django-crm/){target="_blank"} is an application with a web interface. Therefore, you can use an internet browser on your computer, tablet and smartphone to work with it.

To make your work easier, CRM provides help pages and tooltips when you hover your mouse over certain page elements such as icons, buttons, etc.  
Many pages have an <span style="vertical-align: baseline"><img src="../icons/question-mark.svg" alt="Question-mark icon" width="25" height="25"></span> icon in the upper right corner. Clicking on it will open the help page.

Django CRM is a powerful software package that requires customization and integration with other services. If something does not work as expected - report it to your CRM administrator.

The CRM database can contain a large amount of business information.
Therefore, a user's abilities and access to CRM sections are determined by a set of permissions (roles) assigned to the user by the CRM administrator.

!!! Note

    To gain access to the CRM system, please contact your CRM administrator.

Many **objects** are created and stored in CRM database. Such as [**Tasks**](tasks_section.md#tasks), [**Memos**](tasks_section.md#memos), [**Leads**](operator_and_sales_manager_roles.md#lead-object), [**Deals**](guide_for_sales_manager.md#deal-object), **Emails**, etc.
The CRM home page lists the sections and frequently used objects available to the user. To see all the available objects you need to click on the section title.

In relation to specific objects, a user may have all or only some of the following [permissions](adding_crm_users.md#permissions-for-users):

- add 
- change
- delete
- view

These permissions can be permanent and dynamic (dependent on conditions).  
For example, the owner (author) of a memo can always see it.  
But he loses the permissions to modify it and the permissions to delete it after it has been reviewed by the manager.  
Most objects have an owner. As a rule, it is the user who created this object. But some objects can be transferred to another user (another owner is assigned).

All objects have an ID. It is indicated on the object page.  
You can search for an object by its ID.  
To do this, write "ID" and its value together in the search bar.

Objects can have a link to other objects. For example, a memo object will have a relationship with the created task and attached files.  
When you delete a memo, all linked objects will be deleted.  
The list of deleted objects will be shown on the deleting confirmation page.

### History of the object

All objects retain their modification history. By clicking the HISTORY button, you can see who changed what and when.

### File object

The file object does not contain the file itself, but only a link to it. There can be many objects of the same file in the CRM system.  
Therefore, when deleting a file object, only the reference to the file will be deleted.
The file will be deleted when the last link to it is deleted in CRM.  
For example, a office memo has an attached file. An object from this file will also be attached to a task created from it. If you delete a task, the file object will also be deleted, but not the file itself. Because there is still a file object attached to the memo. If this last file object is also deleted, then the file will be deleted.
