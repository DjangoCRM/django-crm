# Django-CRM Overview 

Free CRM management [software](https://github.com/DjangoCRM/django-crm/) is designed to optimize the management of customer interactions, streamline processes, and enhance data-driven decision-making.  
Below is a comprehensive overview of its key features and functionalities:

## Features of the CRM software package

### User Access and Roles

- **Role-Based Access Control to Sections and Objects**: Users' access to various sections and objects within the CRM is determined by their assigned roles.  
  These roles come with specific rights (permissions), which can be either permanent or dynamic.  
  For example, the author of a memo can view it but may lose the right to edit or delete it after it has been reviewed by a superior.
- **Custom Role Management**: Administrators can create new user roles with tailored permissions, allowing for highly customized access control based on the organization's hierarchy.

### Navigation and Usability

- **Home Page**: The CRM's home page provides access to various sections and functionalities based on the user's role.  
  CRM System notifications are displayed to provide a snapshot of recent activities and tasks.
- **Tooltips and Help Pages**: Built-in help pages and tooltips guide users through unfamiliar features.  
  Tooltips appear when hovering over elements like icons or buttons, offering immediate explanations. A detailed **user manual** is also accessible within the system.
- **Reminders**: Users can set personal reminders for critical tasks, meetings, or upcoming deadlines.  
  These reminders can be linked to specific objects within the CRM, ensuring no important task is missed.

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

### Commercial Requests Management

- **Creation and Processing**: Request objects can be automatically created from website forms, emails, or manually within the CRM.  
  Requests contain essential details and receive a "pending" status until verified.  
  The CRM system automatically searches the database for related entities like Company, Contact Person, or Lead when a request is saved and links the request to them.
  - **Request Handling**: Requests are processed and verified, potentially leading to the creation of Deals.
  - **Handling Invalid Requests**: Requests that do not match the company's offerings and cannot be fulfilled are marked as irrelevant and should be deleted.
  - **Commercial request Filtering:** Public email domains are filtered out to avoid misidentification of contacts from common email service providers like Gmail.
  - **Request Counter**: The CRM displays the number of pending requests in the list, with a distinction between those received today and earlier.
- **Geolocation of Counterparty**: The CRM can determine the country and city of the counterparty based on their IP address, which helps sales teams tailor communication and manage territory-specific requests.
- **Banned Company Names and Stop Phrases**: To prevent spam-based Requests, users can add repetitive spam company names to a banned list and define stop phrases to filter out unwanted emails and contact form data.

### Management of Companies, Contact Persons and Leads

- **Company and Contact Person Management**: When a new request is received, the system checks the database for existing companies and contact persons.  
  If no match is found, a new Lead is created.  
- **Lead Conversion**: Leads can be converted into companies and contact persons after validation. It also prevents duplicates by cross-checking new entries against existing data.

### Deals Management

- **Creating and Managing Deal Objects** (like Opportunity):  
  A Deal object is created from a Request and serves as the primary working area where sales managers work towards concluding a successful deal.  
  They can be sorted by default settings or customized according to user preference.
  Details of the work done are stored within the Deal object. Icons provide visual cues about the deal status and required actions.
  - **Deal Lifecycle:** [Deals](pics/deals_screenshot.png) are managed through various customizable stages (e.g., proposal, negotiation, closing), with each stage tracked visually in the CRM until closed.
    Managers can monitor the progress and ensure timely action.
  - **Closing a Deal**: Once work on a deal is finished, it should be closed with a reason selected from a dropdown menu (e.g., won, lost).  
    Closed deals will be hidden from the active deals list but will remain in the database and can be accessed by adjusting the activity filters.
- **Default Sorting of Deals**: New deals are sorted by default at the top of the list, but sorting by the next step date is recommended.

### Sales Funnel

- **Sales Funnel Analysis**: The CRM provides a visual sales funnel that shows the percentage of deals remaining after each stage,  
- helping identify where deals are most often lost and where improvements are needed.
- **Sales Funnel Analysis**: A built-in sales funnel visually represents the conversion of leads into closed deals.  
  This helps sales teams understand where they are losing potential clients and take actions to improve.

### Currency and Payment Handling

- **Currency Setup**: The CRM supports multiple currencies required for payments, including those used for marketing reports, allowing users to manage international clients seamlessly.  
  Currencies and their exchange rates can be updated manually or via integration with external services.
- **The National Currency and Currency for Marketing Reports**: These can be different or the same.
  The CRM uses exchange rate values for generating analytical reports and converting payments, ensuring accurate financial data representation.
- **Payment Tracking**: Payments can be created directly on the Deals page or from the Payments list. All payment data is used in generating analytical CRM reports.

### Shipments

- **Shipments Management**: The CRM allows users to track shipments by specifying contract ship dates.  
  Shipment statuses are linked to deals and displayed in real-time to the relevant sales managers.

### Memo (*Office Memo*)

**Memos**: Memos can be created by any user and are subject to role-based access.
  - **User Roles**: Roles related to memos include owner, recipient, subscribers, and task operators.
  - **States of a Memo**: draft, pending, reviewed, postponed
  - **Recipient of a Memo**: The recipient can be the user himself, the head of a department or company. Memo recipient can take action or create tasks from memos.
  - **Automatic CRM Notifications**: Participants are automatically notified of memo creation and review in CRM and via email, ensuring quick follow-up actions.
  - **Draft**: Memos saved as drafts are only visible to their owners and CRM administrators.
  - **Memo Chat**: Participants can exchange messages and files in the memo chat.
  - **Visual Control of Tasks Created from Memos**: A "view task" button appears next to memos that resulted in tasks, with color indicating task status to track the task's progress.
  - Read more detailed [info](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_memo_features.md)

### Task Management

- **Types of Tasks**: Tasks can be personal or collective, with options for creating subtasks under main tasks.  
  The CRM tracks the progress of tasks and sends notifications to all participants.
  - **Working in a Collective Task**: Collective tasks involve creating subtasks for oneself, with stages updated automatically as task's progress.
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

### Email and Mailings

- **Email Integration:** The CRM software app stores emails linked to specific deals, requests, or contacts.  
  The system imports emails containing CRM tickets automatically and thus synchronizes with mailboxes on the service providers' servers.
- **Email Integration**: The CRM system can integrate with email service providers that require OAuth2 setup (two-factor authentication), such as Gmail.
- **Mailing Campaigns**: Users can create targeted email campaigns, track their success, and manage subscriber lists.  
  Mailings are sent from sales managers’ accounts with limitations to avoid spam filters.

(***The content is being supplemented.***)

You can get more detailed information from [**the user manual**](https://github.com/DjangoCRM/django-crm/blob/main/docs/django-crm_user_guide.md).
