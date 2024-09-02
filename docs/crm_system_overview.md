# CRM System Overview

Free CRM management [software](https://github.com/DjangoCRM/django-crm/) is designed to optimize the management of customer interactions, streamline processes, and enhance data-driven decision-making. Below is a comprehensive overview of its key features and functionalities:

## CRM System Functions and Capabilities

### **User Access and Roles**

- **Role-Based Access Control to Sections and Objects**: Users’ access to various sections and objects within the CRM is determined by their assigned roles. These roles come with specific rights (permissions), which can be either permanent or dynamic. For example, the author of a office memo can view it but lose the right to modify or delete an office memo after it has been reviewed by a superior.

### **Navigation and Usability**

- **Home Page**: The CRM’s home page provides access to various sections and functionalities based on the user's role.
- **Tooltips and Help Pages**: The system includes built-in help pages and tooltips to guide users. Tooltips appear when the mouse hovers over certain elements like icons or buttons, offering immediate assistance.

### **Filters and Sorting**

- **Filter Panel**: Located on the right side of each object list page, the filter panel allows users to narrow down the displayed data. Some filters come with default values; for instance, the task list by default shows only active tasks. Adjust filters if needed.
- **Sorting**: Many tables in the CRM allow sorting by clicking on column headers, enabling users to organize data efficiently.

### **Object Identification and Search**

- **ID-Based Search**: Objects can be quickly located by entering "ID" followed by the object's number in the search bar (e.g., ID1234).
- **Ticket-Based Search**: Commercial requests and related objects can be found by their unique ticket identifier by typing "ticket:" followed by the ticket value (e.g., ticket:tWRMaat3n8Y).
- **Algorithm for Automatic Search**: The CRM uses several identifiers (e.g., first name, email, phone number, website) to match and link objects like request and company and contact persones within the database.

### **Commercial Requests Management**

- **Creation and Processing**: Requests can be automatically created from website forms, emails, or manually within the CRM. Requests contain essential details and receive a "pending" status until verified. The system automatically searches the database for related entities like Company, Contact Person, or Lead when a request is saved and links the request to them.
  - **Request Handling**: Requests are processed and verified, potentially leading to the creation of Deals. Requests that do not match the company’s offerings and cannot be fulfilled are marked as irrelevant and should be deleted.
  - **Commercial request Filtering:** Public email domains are filtered out to avoid misidentification of contacts from common email services like Gmail.
  - **Request Counter**: The CRM displays the number of pending requests in the list, with a distinction between those received today and earlier.
- **Banned Company Names and Stop Phrases**: To prevent spam-based Requests, users can add repetitive spam company names to a banned list and define stop phrases to filter out unwanted emails and contact form data.

### **Management of Companies, Contact Persons and Leads**

- **Company Management**: The CRM checks for the existence of companies in the database when new requests are received. If no match is found, a Lead is created, which can later be converted into a company and contact. Companies can be transferred between sales managers.
- **Lead Conversion**: Leads can be converted into companies and contact persons after validation. The system checks for existing entities to avoid duplicates and establish correct links.

### **Deals Management**

- **Creating and Managing Deal Objects**: A Deal object is created from a Request and serves as the primary working area where sales managers work towards concluding a successful deal. Details of the work done are stored within the Deal object. Icons provide visual cues about the deal status and required actions.
  - **Deal Lifecycle:** [Deals](docs/pics/deals_screenshot.png) are tracked through various stages until closed. They can be sorted by default settings or customized according to user preference.
  - **Closing a Deal**: Once work on a deal is finished, it should be closed with a reason selected from a dropdown menu. Closed deals will be hidden from the active deals list but will remain in the database and can be accessed by adjusting the activity filters.
- **Default Sorting of Deals**: New deals are sorted by default at the top of the list, but sorting by the next step date is recommended.

### **Sales Funnel**

- **Sales Funnel Analysis**: The CRM provides a visual sales funnel that shows the percentage of deals remaining after each stage, helping identify where deals are most often lost and where improvements are needed.

### **Currency and Payment Handling**

- **Currency Setup**: The CRM supports multiple currencies required for payments, including those used for marketing reports. Currencies and their exchange rates can be updated manually or automatically, with options for connecting additional software for real-time updates.
  - **The National Currency and Currency for Marketing Reports**: These can be different or the same.
  - **Exchange Rate Algorithm**: The CRM uses exchange rate values for generating analytical reports and converting payments, ensuring accurate financial data representation.
- **Payment Tracking**: Payments can be created directly on the Deals page or from the Payments list. All payment data is used in generating analytical CRM reports.

### **Shipments**

- **Shipments**: Only shipments with specified contract ship dates are managed within this section of the CRM.

### **Office Memo**

- **Office Memos**: Memos can be created by any user and are subject to role-based access. The system supports stages such as "pending," "postponed," and "reviewed." The recipient changes the status. Memos may lead to task creation, with the status of related tasks visible alongside the memo to track the task's progress.
  - **User Roles**: Roles related to memos include owners, recipients, subscribers, and task operators.
  - **Who Can Be the Recipient of a Memo**: Recipients are typically department heads or company executives.
  - **Automatic CRM Notifications**: Participants are notified of memo creation and review in CRM and via email.
  - **Draft**: Memos saved as drafts are only visible to their owners and CRM administrators.
  - **Memo Chat**: Participants can exchange messages and files in the memo chat.
- **Visual Control of Tasks Created from Memos**: A "view task" button appears next to memos that resulted in tasks, with color indicating task status.

### **Task Management**

- **Types of Tasks**: Tasks can be personal or collective, with options for creating subtasks under main tasks. The CRM tracks the progress of tasks and sends notifications to all participants.
  - **Working in a Collective Task**: Collective tasks involve creating subtasks for oneself, with stages updated automatically as tasks progress.
- **User Roles**: Roles related to tasks include owners, responsible parties, subscribers, and task operators.
- **Set Tasks for Subordinates**: Tasks can be created for oneself or subordinates, with department heads having oversight.
  - **Why Set Tasks for Ourselves**: Self-created tasks provide a record of completed work, visible to managers.
- **Task Workflow:** Tasks have stages such as "pending," "in progress," "completed," and "canceled." Automatic notifications and chat functionalities support task management.
  - **"Next Step" Field**: Enter the planned action and its date in the "Next Step" and "Step Date" fields. This is automatically saved in the "Workflow" field.
  - **Task Chat**: Task participants can discuss progress and results in the task chat.
  - **Task Filters**: Filters help search for tasks and are used by managers to view employees' tasks.
  - **Tags**: Users can tag tasks and filter them by tags.
  - **Sorting Tasks**: New tasks are sorted at the top of the list by default but can be sorted by next step date.

## Email and Mailings

- **Email Integration:** Emails are stored in the CRM and can be viewed in text format. The system imports emails containing CRM tickets automatically.
  - **Mail Account Setup:** Gmail accounts require two-step authentication and OAuth2 setup. Co-owners can be assigned to manage email accounts.

- **Mailings:** Users can create and manage email campaigns, with options to select recipients and track mailing progress. Mailings are sent through sales managers' accounts with limitations to prevent spam.
