# Django-CRM user guide

## Table of contents

- [Introduction](#introduction)
  - [History of the object](#history-of-the-object)
  - [File object](#file-object)

- [Working in the "Tasks" section (for all users)](#working-in-the-tasks-section-for-all-users)
  - [Chat in objects](#chat-in-objects)
  - [Reminders](#reminders)
  - [Tasks](#tasks)
  - [Memos](#memos)
- [A guide for company executives](#a-guide-for-company-executives)
  - [Analytics section](#analytics-section)
    - [Income Summary](#income-summary)
- [Guidelines for users with the roles "operator" and "sales manager"](#guidelines-for-users-with-the-roles-operator-and-sales-manager)
  - [Working with requests](#working-with-requests)
  - [Geolocation of the counterparty's country and city by its IP](#geolocation-of-the-counterpartys-country-and-city-by-its-ip)
  - [Search for objects by ticket](#search-for-objects-by-ticket)
  - [Company object](#company-object)
  - [Object of company contact persons](#object-of-company-contact-persons)
  - [Lead object](#lead-object)
  - [Email Object](#email-object)
- [Guide for sales manager](#guide-for-sales-manager)
  - [Deal object](#deal-object)
  - [Payment object](#payment-object)
  - [List of Deals](#list-of-deals)
  - [Company Newsletter](#company-newsletter)
  - [Transfer of company objects to another sales manager](#transfer-of-company-objects-to-another-sales-manager)

- [Django CRM Administrator's Guide](#django-crm-administrators-guide)
  - [Mass transfer of companies to another sales manager](#mass-transfer-of-companies-to-another-sales-manager)
  - [Mass contacts objects](#mass-contacts-objects)

## Introduction

[Django-CRM](https://github.com/DjangoCRM/django-crm/) is an application with a web interface. Therefore, you can use an internet browser on your computer, tablet and smartphone to work with it.

To make your work easier, CRM provides help pages and tooltips when you hover your mouse over certain page elements such as icons, buttons, etc.  
Many pages have an icon (?) in the upper right corner. Clicking on it will open the help page.

Django CRM is a powerful software package that requires customization and integration with other services. If something does not work as expected - report it to your CRM administrator.

The CRM database can contain a large amount of business information.
Therefore, a user's abilities and access to CRM sections are determined by a set of permissions (roles) assigned to the user by the CRM administrator.

Many **objects** are created and stored in CRM. Such as **tasks**, **memos**, **leads**, **deals**, **emails**, etc.
The CRM home page lists the sections and frequently used objects available to the user. To see all the available objects you need to click on the section title.

In relation to specific objects, a user may have all or only some of the following permissions:

- see,
- create (add),
- change,
- delete

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

All objects retain their modification history. By clicking the "History" button, you can see who changed what and when.

### File object

The file object does not contain the file itself, but only a link to it. There can be many objects of the same file in the CRM.  
Therefore, when deleting a file object, only the reference to the file will be deleted.
The file will be deleted when the last link to it is deleted in CRM.  
For example, a memo has an attached file. An object from this file will also be attached to a task created from it. If you delete a task, the file object will also be deleted, but not the file itself. Because there is still a file object attached to the memo. If this last file object is also deleted, then the file will be deleted.

## Working in the "Tasks" section (for all users)

In this section, users can work with memos, tasks, and projects (collections of tasks).
Participating users receive notifications about all events in CRM and by email.
Only users specified in them in any role and company managers have access to specific memos, tasks and projects. Other users will not see them.  
If it is necessary to regularly make edits or correct errors in these objects, the administrator can assign the "task operator" role to a user. This user will have the right to edit objects of other users.

### Chat in objects

Objects have chat. For example, in each task, all participants can discuss its implementation and share files in the chat. Accordingly, all messages will be tied to a specific task. To create a message, click the button "Message +".  
Messages are sent to users in CRM and by email.

### Reminders

In many objects, you can create a reminder associated with this object.  
You can set the date and time when the reminder will appear in CRM and be sent by email.  
In the general section, you can see a list of all created reminders. If necessary, you can deactivate reminders that have become irrelevant.

### Tasks

Tasks can be collective and individual, main and subtasks.  
The task can include subscribers. These are the users who should be notified when the task is created and completed. They can see the task.  
By default, only active tasks are displayed in the task list.

If several users (responsible) are assigned to perform a task, then this is a collective task. To work on a collective task, performers:

- must create subtasks for themselves;
- can create subtasks for each other.

Tasks can have the following status:

- pending;
- in progress;
- done;
- canceled.

Django CRM automatically marks a collective task as completed if each responsible person has at least one subtask and all subtasks are completed.  
In other cases, it is up to the owner (co-owner) of the task to change the status of the main task.

Users can create tasks for themselves. In this case, CRM automatically assigns a co-owner of the task to the head of the executor's department. This allows department heads to be aware of their employees' tasks.

### Memos

Users can create memos to department or company managers to inform them or to make decisions.  
If there are users who need to know about the memo and its content, they can be specified as subscribers of this task.  
The recipient of the memo and the subscribers will be notified and will have access to the memo.

You can save a memo with the status "draft". In this case, no notifications will be sent and only the author (owner) will have access to it.

The author can modify the memo until the recipient sets the status to "reviewed". The author will be notified of this.

A task or project can be created as a result of the memo. For convenience, information from the memo is copied into them. But the recipient can modify or add to it.  
The author of the memo and the subscribers automatically become subscribers of the created task or project.

Sales managers can create a memo from a deal. In this case, the "View Deal" button will appear in the memo.  
Chat is available in the memo for participants and company management.
Chat is also available in a task or project.  
It can be used, for example, to notify participants about changes that have occurred since the memo was reviewed.

In the list of memos, you can see the status of the task created for it. The color of the "View task" button reflects the status of the task. Also, if you put the mouse cursor over it, the status information appears.

## A guide for company executives

By default, company managers have access to all sections. If some sections or objects are not of interest, they can be hidden using individual settings - contact your Django CRM administrator.

### Analytics section

This section contains statistical and analytical reports. There are currently eight of them.

- Sales funnel;
- Sales report;
- Income Summary;
- Requests Summary;
- Lead source Summary;
- Conversion Summary (inquiries into successful deals);
- Closing reason Summary;
- Deal Summary;

Reports contain tables and diagrams.  
By default, company managers, sales managers and CRM administrator have access to this section.

#### Income Summary

The first table shows information on which deals, for which products and in what volume payments were received in the current month.

The following tables show the forecast for the current and two future months for guaranteed payments, payments with high and low probability.

The diagrams show:

- last 12 months' income;
- 12 months' income in the prior period;
- 12-month cumulative income.

## Guidelines for users with the roles "operator" and "sales manager"

The operator's duties include creating and processing commercial requests in the CRM.
In smaller companies, sales managers fulfill this role as well.  
In addition to requests, operators also work with lead, company and contact objects.  
Operators must be granted rights to company mailboxes that receive commercial requests.

### Working with requests

Requests coming through contact forms of your company's websites create objects in Django CRM automatically.  
Requests coming to your company's email should be imported.  
To do this, click the "Import request from mail" button in the upper right corner of the requests page.  
  `Home > Crm > Requests`
 
The list of incoming emails of your company's email account or the list of email accounts if there is more than one.  
Check the emails on the basis of which you want to create requests in CRM and click the import button.  
Contact your CRM administrator if any of this does not work.

You can also create a request by filling out a form. To get the form, click the "Add Request" button.

Newly created requests receive the status "pending" (pending processing).  
When a request is created, it is assigned a unique ticket.  
This ticket is subsequently assigned to the deal and all emails.

When processing a request, it is important to check that the contact details are correct and complete. It is necessary to request missing data from the client.  
When creating a request, as well as each time you save its changes, CRM performs a comparison of all contact data specified in the request with the data accumulated in the database. This is done to link the request to the company and contact person or lead already created in the database. The result will be reflected in the "Relations" section.
You can set the links by yourself. To do this, you should press the "magnifying glass" icon near the corresponding field and select an object from the list that appears. Or you can specify the ID of this object.

After the request processing is completed, you should select a sales manager who will work with the deal object created on the basis of this request. This can be done in the drop-down menu of the "owner" field.  
Then create the deal object by pressing the corresponding button.
If at this point the links to the objects: company, contact person or lead are not set, a new lead will be created. The request and deal will be linked to this lead. And the sales manager will be notified about the new deal.

The object of the deal is not a sign of concluding an agreement with the counterparty.  
It contains information for concluding an agreement with the counterparty and displays the progress of work on this.  
Deals should be created for all requests excluding requests with the status "duplicate".  
The request status "pending" is removed automatically when a deal is created or when the request status is set to "duplicate".

Requests are used in marketing analysis. Therefore, only irrelevant requests should be deleted.  
CRM operators and administrators have the permissions to delete requests.

### Geolocation of the counterparty's country and city by its IP

In Django CRM can be configured and activated geolocation of the country and city of the counterparty by its IP. In this case, the country and city will be automatically filled in the requests. But in cases where VPN is used, this data may be unreliable.

### Search for objects by ticket

You can search for requests, deals, and emails by ticket.
To do this, in the search bar you need to enter, for example,
 *ticket:lzeH07E8aHI* or *ticket lzeH07E8aHI*

### Company object

A company object is needed to store information about the company, your counterparty, as well as visualize your interaction with this company.
Many objects will have a connection with this object.  
This allows you to see the list:

- employees of this company with whom you are dealing (contact persons),
- correspondence with this company,
- all deals,
- a list of your company's sent newsletters.

On the company object page you can:

- create and send an email to the company,
- contact the company by phone,
- go to the company's website,
- add the object of a new contact person.

It is important to avoid creating duplicate objects of the same company.
This happens when the data specified in the request does not match the data in the company object.  
If a duplicate object is detected, it can be easily deleted using the "correctly delete duplicate object" button. All links will be reconnected to the specified original object.

### Object of company contact persons

A contact person object is needed to store information about the contact person, as well as visualize your interaction with the contact person.  
This object provides the same capabilities as the company object and is associated with it.

### Lead object

Sometimes when a request is received, it does not contain information about the company or contact person.  
In this case, a lead object is created.  
This object provides the same features as the company object.  
Later, when the missing data is received, the lead object can be converted into company and contact person objects. In this case, the lead object will be deleted and all connections will be reconnected to the company and contact person.

If necessary, objects of companies, contacts and leads can be exported to Excel files. Using similar files, it is possible to upload existing data to CRM for automatic creation of objects in the database.

### Email Object

In CRM you can create and send emails.  
To do this, the administrator must configure CRM access to user mailboxes.  
Django CRM scans the mailboxes of operators and sales managers and automatically imports emails containing a ticket but not in the CRM database.  
Therefore, it is enough to send the first letter (with a ticket) from the CRM. The user can conduct further correspondence from his mailbox.

For a number of reasons, imported emails are stored in CRM in text format.  
Therefore, some letters, for example, those containing tables, may be difficult to read. Use the button with the eye icon. The letter will be downloaded from the mail server and shown in the original.  
Emails from clients that do not contain a ticket will not be uploaded to CRM automatically.  
They can be downloaded and associated with the request and deal using the "Import letter" button. This can be done on the request or deal page.

Please note that an email sent from CRM cannot be imported into CRM because it is already in the CRM database. If you try to do this, protection will be triggered.  
In this case, you can link the email to objects by specifying their IDs in the "Links" section of the email.

Before a user starts working with mail, it is recommended to create one or more user signatures. One of them should be selected as the default signature.  
 `Home > Mass mail > Signatures`


## Guide for sales manager

### Deal object

A Deal object is created on the basis of a request as described in the section "[Working with requests](#working-with-requests)".  
A Deal object can be assigned to a co-owner - a second sales manager who can also work on this deal.

The object of the deal allows:

- see the customer's request;
- send and receive emails and see all correspondence related to this deal;
- contact the counterparty by phone and use messengers;
- store all files associated with this deal;
- create memos regarding the deal;
- exchange messages with company management, second sales manager and administrator.

The Deal object represents:

- contact details of the counterparty;
- all deals with the counterparty company;
- information on goods/services of the deal;
- payment information.

When you create an email, Django CRM injects a ticket into it. This allows CRM to find emails related to this deal in sales managers' email accounts and upload them to the CRM database. Therefore, at least the first letter must be sent from the CRM. Further correspondence can be carried out from email accounts if a ticket is saved in the emails.
If for some reason a letter was created related to a deal but without a ticket, then it can be imported and linked to the deal using the "Import letter" button.

The stages of the deal, reasons for closing, and much more can be customized to suit the specifics of your company - contact your CRM administrator.

The data specified in deals is used in analytics. For example, the stages of a transaction are used to build a "sales funnel" report. It can be viewed here:  
 `Home > Analytics > Sales funnel`


At the moment, there are eight different reports available in the "Analytics" section.

### Payment object

You can create payment objects in a deal.
In addition to the usual data, the payment can have one of the following statuses:

- received;
- guaranteed;
- high probability;
- low probability.

This is used to create a summary of income, including its forecast.  
The income summary is important for management decision-making by the company's executives.  
 `Home > Analytics > Income Summary


### List of Deals

By default, new Deals are placed at the top of the list. But by pressing the sort toggle trigger button, you can switch between this sort and sort by next step date. In this mode, transactions whose next step date is approaching will be pushed to the top of the list.

By default, only active deals are shown in the list. When work on the deal is completed, you need to select the reason for closing the deal in the drop-down menu of the deal. Then the deal will no longer be active and will not appear in the list by default.

To provide more information about deals, they are marked with different icons. To get a hint about the meaning of an icon, hover your mouse cursor over it.

### Company Newsletter

CRM allows you to automatically send out company news.
Recipients can be companies, contacts and leads from the CRM database.
Uninterested recipients have the opportunity to unsubscribe from receiving further mailings.

Mailing is performed through the main and additional mail accounts of sales managers. Additional email accounts should be created and configured by the CRM administrator to reduce the risk of spam filters blocking the main accounts of managers. For the same purpose, mailings from the main account are only sent to recipients marked as VIP. This can be done through the drop-down menu of actions on the recipient list pages (companies, contacts and leads).

If accounts that require two-step authentication for third-party applications are used for mailing, you should contact the administrator for assistance in passing it for the first time.

Prepare a message for the newsletter:  
 `Home > Mass mail > Email Messages`


To embed images in your message, you can use the button to upload an image file to the CRM server and the button to view uploaded images.  
Under each image, there is a html tag of the path to the file. It should be copied and pasted into the message template.

You can copy a finished message from another sales manager to yourself (the message does not contain a signature).  
You can use the "Send Test" button to check the message display. CRM will make a list of available email accounts of the sales manager and send the message from the first account to the other accounts.

The mailing object is created on the pages of the recipient lists (companies, contacts and leads). To do this, you can use the "Create mailing" button or the drop-down action menu.
Using the action menu, you can create a mailing to selected recipients on one page. If you have to create several mailing lists, you can combine them using the action menu on the mailing list page.  
In the created mailing object, specify the message to be sent, the desired signature and save the object with the status "active". To simulate a human being, CRM will send emails evenly throughout the work day at random intervals. The mailing will be automatically paused on Friday, Saturday and Sunday.

### Transfer of company objects to another sales manager

A sales manager can transfer a company object to another manager. Contact persons will be transferred automatically.  
But to change the owner of a group of companies, you must contact the administrator.

## Django CRM Administrator's Guide

In order for users to be successful in Django CRM, the administrator must do a good job as well as help other users with their work. To do this, the administrator must study all the previous sections of this guide, as well as the CRM installation and configuration guide.

### Mass transfer of companies to another sales manager

This can be done using the action drop-down menu on the company's page.
The contact persons will be transferred automatically.

### Mass contacts objects

To ensure that recipients always receive mailing messages from the same email account, mass contact objects are automatically created.
These objects correspond to the recipient of the mailing and the mail account from which the messages are sent to him.
