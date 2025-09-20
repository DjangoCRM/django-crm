<p align="right">
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/crm_system_overview.md">English</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/crm_system_overview-spanish.md">Español</a>
</p>

# Django-CRM Overview

Free CRM management [software](https://github.com/DjangoCRM/django-crm/) is designed to optimize the management of customer interactions, streamline processes, and enhance data-driven decision-making.  
The customer crm software leverages the Django framework, ensuring ease of development, customization, and deployment.

Below is a comprehensive overview of its key features and functionalities:

## Key Features of all Applications in the CRM software package

The **CRM app** in Django-CRM is the central hub for managing customer interactions, commercial requests, and sales processes.  
Its features are designed to streamline operations and provide actionable insights for sales managers, operators, and administrators.

### User Access and Roles

- **Role-Based Access Control to Sections and Objects**: Users' access to various sections and objects within the CRM is determined by their assigned roles.  
  These roles come with specific rights (permissions), which can be either permanent or dynamic.  
  For example, the author of a memo can view it but may lose the right to edit or delete it after it has been reviewed by a superior.
- **Custom Role Management**: Administrators can create new user roles with tailored permissions, allowing for highly customized access control based on the organization's hierarchy.

### Filters and Sorting

- **Filter Panel**: The filter panel, located on the right side of each object list page, allows users to narrow down the displayed data.  
  Some filters come with default values (e.g., only showing active tasks). Filters can be customized and saved for future use.
- **Advanced Sorting**: In addition to basic sorting by column headers, users can apply multi-level sorting for more complex data views.  
  For instance, tasks can be sorted first by due date and then by priority level.
  
### Object Identification and Search

- **ID-Based Search**: Objects can be quickly located by entering "ID" followed by the object's number (e.g., ID1234).
- **Ticket-Based Search**: Commercial requests and related objects as Emails, Deals, etc. can be found by their unique ticket identifier by typing "ticket:" followed by the value (e.g., ticket:tWRMaat3n8Y).
- **Automatic Search Algorithms**: The CRM uses several identifiers (e.g., first name, email, phone number) to match and link objects, such as requests to companies and contact persons.  
  The system automatically suggests related entities during searches.

### Internal Chat Integration

Facilitate communication within the team through integrated chat.

## Navigation and Usability

- **Home Page**: The CRM's home page provides access to various sections and functionalities based on the user's role.  
  CRM System notifications are displayed to provide a snapshot of recent activities and tasks.
- **Tooltips and Help Pages**: Built-in help pages and tooltips guide users through unfamiliar features.  
  Tooltips appear when hovering over elements like icons or buttons, offering immediate explanations. A detailed **user manual** is also accessible within the system.
- **Reminders**: Users can set personal reminders for critical tasks, meetings, or upcoming deadlines.  
  These reminders can be linked to specific objects within the CRM, ensuring no important task is missed.

## The CRM Application in Django-CRM software package

The **CRM app** in the Django-CRM system is designed to manage customer relationships effectively.  
It provides a comprehensive suite of features to handle various business objects such as requests, leads, companies, contact persons, deals, email messages, products, payments and  twelve others.

### Commercial Request Management

- Automates the creation of requests from website forms or emails.
- Allows manual entry of phone call requests.
- Ensures all requests are linked to relevant Companies, Leads, or Contacts.
- Provides tools for verifying and completing missing client details.

### Lead and Company Management

- Automatically identifies duplicate Leads or Companies to maintain database integrity.
- Simplifies conversion of Leads to Companies and Contacts upon validation.
- Links all associated data, including Requests, Deals, and Emails, to the correct entities.

### Deal Lifecycle Management

- Supports tracking Deals from creation to closure.
- Offers customizable stages and closing reasons to suit business needs.
- Integrates with email communication, tagging, and reminders for seamless deal handling.
- Provides real-time status updates through intuitive icons.

### Integrated Communication Tools

- Centralizes email correspondence by linking emails to relevant Requests and Deals.
  - Sync emails automatically with CRM objects.
    - Generates unique tickets for tracking email threads.
- Supports VoIP calls and messaging via platforms like WhatsApp, Viber and others.
- Includes an internal chat feature for collaboration among team members.

### Advanced Search and Filtering

- Enables object search by IDs, tickets, or other identifiers.
- Offers robust filtering options for Deals, Requests, and Companies.

### Currency and Payment Handling

- Supports multiple currencies for payment tracking and reporting.
- Allows manual or automated exchange rate updates for accurate financial data.
- Tracks payments directly from Deals or Payments list.
- Integrates payment data into CRM analytics for comprehensive reporting.

Read more detailed [CRM app features](https://github.com/DjangoCRM/django-crm/blob/main/docs/crm_app_features.md)

## The Tasks Application in Django-CRM software suite

### Memo (*Office Memo*)

**Memos**: Memos can be created by any user and are subject to role-based access.

- **User Roles**: Roles related to memos include owner, recipient, subscribers, and task operators.
- **States of a Memo**: draft, pending, reviewed, postponed
- **Recipient of a Memo**: The recipient can be the user himself, the head of a department or company. Memo recipient can take action or create tasks from memos.
- **Automatic CRM Notifications**: Participants are automatically notified of memo creation and review in CRM and via email, ensuring quick follow-up actions.
- **Draft**: Memos saved as drafts are only visible to their owners and CRM administrators.
- **Memo Chat**: Participants can exchange messages and files in the memo chat.
- **Visual Control of Tasks Created from Memos**: A "view task" button appears next to memos that resulted in tasks, with color indicating task status to track the task's progress.

Read more detailed [memo features](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_memo_features.md)

### Task Management

- **Types of Tasks**: Tasks can be personal or team, with options for creating subtasks under main tasks.  
  The CRM tracks the progress of tasks and sends notifications to all participants.
  - **Working in a Team Task**: Collective tasks involve creating subtasks for oneself, with stages updated automatically as task's progress.
- **User Roles**: Roles related to tasks include owners, responsible, subscribers, and task operators.
- **Set Tasks for Subordinates**: Tasks can be created for oneself or subordinates, with department heads having oversight.
  - **Why Set Tasks for Ourselves**: Self-created tasks provide a ToDo list and record of completed work, visible to managers.
- **Task Workflow:** Each task moves through stages such as "pending," "in progress," and "completed," with next steps tracked in the "Next Step" and "Step Date" fields.  
  Automatic notifications and chat functionalities support task management.
  - **"Next Step" Field**: Enter the planned action and its date in the "Next Step" and "Step Date" fields. This is automatically saved in the "Workflow" field.
  - **Task Chat**: Task participants can discuss the task’s progress, share documents, and communicate within the task chat.
  - **Task Filters**: Tasks can be filtered by various criteria (e.g., due date, priority, assigned user), and users can assign tags to tasks for better organization.
  - **Tags**: Users can tag tasks and filter them by tags.
  - **Sorting Tasks**: New tasks are sorted at the top of the list by default but can be sorted by next step date.

  Read more detailed [task features](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_task_features.md)

## Email and Mailings

- **Email Integration:** The CRM software app stores emails linked to specific deals, requests, or contacts.  
  - The system imports emails containing CRM tickets automatically and thus synchronizes with mailboxes on the service providers' servers.
  - The CRM system can integrate with email service providers that require OAuth2 setup (two-factor authentication), such as Gmail.
- **Mailing Campaigns**: Users can create targeted email campaigns, track their success, and manage subscriber lists.  
  Mailings are sent from sales managers’ accounts with limitations to avoid spam filters.

## The Analytics Application in Django-CRM customer software

The Django-CRM system includes analytical features that provide various reports to help you make informed business decisions:

- **Income Summary Report**: Overview of income and its forecast. 
  - Provides a summary of income and forecast based on payment statuses.
- **Sales Funnel Report**: Visual representation of the sales process.
- **Lead Source Summary Report**: Analysis of lead sources and their effectiveness.
- **Lead Conversion Report**: Overview of lead conversion rates.
- **Deal Summary Report**: Summary of deals and their statuses.

### Sales Funnel

- **Sales Funnel Analysis**: The CRM provides a visual sales funnel that shows the percentage of deals remaining after each stage, helping identify where deals are most often lost and where improvements are needed.
  A built-in sales funnel visually represents the conversion of commercial requests into closed deals.  
  This helps sales teams understand where they are losing potential clients and take actions to improve.

## Deployment and Use

- Easy to deploy as a regular Django project.
- Comprehensive documentation available for installation, configuration, and user guidance.
- Active community support and contributions are encouraged.

### Technical Aspects:

- **Localization:**  Supports multiple languages  
  (currently: ar, cs, de, el, en, es, fr, he, hi, id, it, ja, ko, nl, pl, pt-br, ro, ru, tr, uk, vi, zh-hans)
- **Technology Stack:** Built on Django 5.1.x, Python 3.10+, MySQL 8.0.11+ or PostgreSQL 12+.
- **License:** Released under the AGPL-3.0 open source license.

## Conclusion

The Django-CRM system is a powerful and flexible solution for managing customer relationships.  
It offers a wide range of features to handle various business objects, automate email marketing, and gain insights through analytics.  
By leveraging these features, businesses can enhance their customer relationship management processes and make informed decisions.

(***The content is being supplemented.***)

You can get more detailed information from [**the user manual**](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_user_guide.md).
