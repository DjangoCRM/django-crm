<p align="right">
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/crm_app_features.md">English</a> |
<a href="https://github.com/DjangoCRM/django-crm/blob/main/docs/crm_app_features-spanish.md">Español</a>
</p>

# Comprehensive Overview of the CRM App in Django-CRM software suite

The **CRM app** in Django-CRM is the central hub for managing customer interactions, commercial requests, and sales processes.  
Its features are designed to streamline operations and provide actionable insights for sales managers, operators, and administrators.
Features role-based access control, ensuring users only see data relevant to their roles.
The CRM app’s data integrates seamlessly into the Analytics app for generating insights like sales funnels, income summaries, and conversion rates.  
These reports empower businesses to refine strategies and achieve better outcomes.

## Commercial Requests Management

- **Creation and Processing**: Request objects can be automatically created from website forms, emails, or manually within the CRM.  
  Requests contain essential details and receive a "pending" status until verified.  
  The CRM system automatically searches the database for related entities like Company, Contact Person, or Lead when a request is saved and links the request to them.
  - **Request Handling**: Requests are processed and verified, potentially leading to the creation of Deals.
  - **Handling Invalid Requests**: Requests that do not match the company's offerings and cannot be fulfilled are marked as irrelevant and should be deleted.
  - **Commercial request Filtering:** Public email domains are filtered out to avoid misidentification of contacts from common email service providers like Gmail.
  - **Request Counter**: The CRM displays the number of pending requests in the list, with a distinction between those received today and earlier.
- **Geolocation of Counterparty**: The CRM can determine the country and city of the counterparty based on their IP address, which helps sales teams tailor communication and manage territory-specific requests.
- **Banned Company Names and Stop Phrases**: To prevent spam-based Requests, users can add repetitive spam company names to a banned list and define stop phrases to filter out unwanted emails and contact form data.

## Management of Companies, Contact Persons and Leads

- **Company and Contact Person Management**: When a new request is received, the system checks the database for existing companies and contact persons.  
  If no match is found, a new Lead is created.  
- **Lead Conversion**: Leads can be converted into companies and contact persons after validation. It also prevents duplicates by cross-checking new entries against existing data.

## Deals Management

- **Creating and Managing Deal Objects** (like Opportunity):  
  A Deal object is created from a Request and serves as the primary working area where sales managers work towards concluding a successful deal.  
  They can be sorted by default settings or customized according to user preference.
  Details of the work done are stored within the Deal object. Icons provide visual cues about the deal status and required actions.
  - **Deal Lifecycle:** [Deals](https://github.com/DjangoCRM/django-crm/raw/main/docs/pics/deals_screenshot.png) are managed through various customizable stages (e.g., proposal, negotiation, closing), with each stage tracked visually in the CRM until closed.
    Managers can monitor the progress and ensure timely action.
  - **Closing a Deal**: Once work on a deal is finished, it should be closed with a reason selected from a dropdown menu (e.g., won, lost).  
    Closed deals will be hidden from the active deals list but will remain in the database and can be accessed by adjusting the activity filters.
- **Default Sorting of Deals**: New deals are sorted by default at the top of the list, but sorting by the next step date is recommended.

## Currency and Payment Handling

- **Currency Setup**: The CRM supports multiple currencies required for payments, including those used for marketing reports, allowing users to manage international clients seamlessly.  
  Currencies and their exchange rates can be updated manually or via integration with external services.
- **The National Currency and Currency for Marketing Reports**: These can be different or the same.
  The CRM uses exchange rate values for generating analytical reports and converting payments, ensuring accurate financial data representation.
- **Payment Tracking**: Payments can be created directly on the Deals page or from the Payments list. All payment data is used in generating analytical CRM reports.

## Integration and Extensibility

- **Web Form Integration**: Automates data entry with built-in reCAPTCHA and geolocation.  
  - Web forms can be customized to match the company's branding and data requirements.
  - Ensures data integrity and accuracy by validating form entries before creating requests.
- **Email Integration**: Allows users to send and receive emails directly from the CRM.
- **Email Synchronization**: Manages emails using SMTP and IMAP protocols.
  - Automatically generates unique tickets for tracking email threads.
  - Manually import emails related to Deals using the "Import letter" button.
- **Excel Support**: Streamlines data import/export for Companies, Contacts, and Leads.

## Shipments

- **Shipments Management**: The CRM allows users to track shipments by specifying contract ship dates.  
  Shipment statuses are linked to deals and displayed in real-time to the relevant sales managers.
