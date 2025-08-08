
## Guidelines for users with the roles "operator" and "sales manager"

The operator's duties include creating and processing commercial requests in [the CRM](https://github.com/DjangoCRM/django-crm/){target="_blank"}.
In smaller companies, sales managers fulfill this role as well.  
In addition to Requests, operators also work with [Lead](#lead-object), [Company](#company-object) and [Contact person](#object-of-company-contact-persons) objects.  
Operators must be granted rights to company mailboxes that receive commercial requests.

### Working with requests

Requests coming through contact forms of your company's websites create objects in Django CRM automatically.  
Requests coming to your company's email should be imported.  
To do this, click the "Import request from mail" button in the upper right corner of the "Requests" page.  
  `Home > Crm > Requests`
 
The list of incoming emails of your company's email account or the list of email accounts if there is more than one.  
Check the emails on the basis of which you want to create requests in CRM and click the import button.  
Contact your CRM administrator if any of this does not work.

You can also create a request by filling out a form. To get the form, click the "Add Request" button.

Newly created requests receive the status "pending" (pending processing).  
When a request is created, it is assigned a unique ticket.  
This ticket is subsequently assigned to the deal and all emails.

When processing a request, it is important to check that the contact details are correct and complete. It is necessary to request missing data from the client.  
When creating a request, as well as each time you save its changes, CRM performs a comparison of all contact details specified in the request with the data accumulated in the database. This is done to link the request to the company and contact person or lead already created in the database. The result will be reflected in the "Relations" section.
You can set the links by yourself. To do this, you should press the magnifying glass <span style="vertical-align: baseline"><img src="../icons/magnifying-glass.svg" alt="Magnifying glass icon" width="17" height="17"></span> icon near the corresponding field and select an object from the list that appears. Or you can specify the ID of this object.

After the request processing is completed, you should select a sales manager who will work with the deal object created on the basis of this request. This can be done in the drop-down menu of the "owner" field.  
Then create the [Deal](guide_for_sales_manager.md#deal-object) object by pressing the corresponding button.
If at this point the links to the objects: company, contact person or lead are not set, a new lead will be created. The request and deal will be linked to this lead. And the sales manager will be notified about the new deal.

!!! Note
    The object of the deal is not a sign of concluding an agreement with the counterparty.  
    It contains information for concluding an agreement with the counterparty and displays the progress of work on this.  

Deals should be created for all requests excluding requests with the status "duplicate."  
The request status "pending" is removed automatically when a deal is created or when the request status is set to "duplicate."

Requests are used in marketing analysis. Therefore, only irrelevant requests should be deleted.  
CRM operators and administrators have the permissions to delete requests.

### Geolocation of the counterparty's country and city by its IP

In Django CRM can be configured and activated geolocation of the country and city of the counterparty by its IP. In this case, the country and city will be automatically filled in the requests. But in cases where VPN is used, this data may be unreliable.

### <span style="vertical-align: baseline"><img src="../icons/magnifying-glass.svg" alt="Magnifying glass icon" width="17" height="17"></span> Search for objects by ticket

You can search for requests, deals, and emails by ticket.  
To do this, in the search bar you need to enter, for example:  
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

- create an email and send it to the company,
- contact the company by phone,
- go to the company's website,
- add the object of a new contact person.

It is important to avoid creating duplicate objects of the same company.
This happens when the data specified in the request does not match the data in the company object.  
If a duplicate object is detected, it can be easily deleted using the "correctly delete duplicate object" button. All links will be reconnected to the specified original object.

### Object of company contact persons

A contact person object is needed to store information about the contact person, as well as visualize your interaction with the contact person.  
This object provides the same capabilities as the [company](#company-object) object and is associated with it.

### Lead object

Sometimes when a request is received, it does not contain information about the company or contact person.  
In this case, a lead object is created.  
This object provides the same features as the company object.  
Later, when the missing data is received, the lead object can be converted into company and contact person objects. In this case, the lead object will be deleted and all connections will be reconnected to the company and contact person.

If necessary, objects of companies, contacts and leads can be exported to Excel files. Using similar files, it is possible to upload existing data to CRM for automatic creation of objects in the database.

### Email Object

<span style="vertical-align: baseline"><img src="../icons/envelope-check.svg" alt="Envelope icon" width="25" height="25"></span> In CRM you can create and send emails.  
To do this, the administrator must configure CRM access to user mailboxes.  
Django CRM scans the mailboxes of operators and sales managers and automatically imports emails containing a ticket but not in the CRM database.  
Therefore, it is enough to send the first letter (with a ticket) from the CRM. The user can conduct further correspondence from his mailbox.

For a number of reasons, CRM imports and saves emails in text format (the same format in which it receives them from the email provider).  
Therefore, some letters, for example, those containing tables, may be difficult to read. Use the button with the eye <span style="vertical-align: baseline"><img src="../icons/eye.svg" alt="Eye icon" width="25" height="25"></span> icon. The letter will be downloaded from the mail server and shown in the original.  
Emails from clients that do not contain a ticket will not be uploaded to CRM automatically.  
They can be downloaded and associated with the request and deal using the "Import letter" button. This can be done on the request or deal page.

!!! Note 
    An Email sent from CRM cannot be imported into CRM because it is already in the CRM database.  

If you try to do this, protection will be triggered.  
In this case, you can link the email to objects by specifying their IDs in the "Links" section of the email.

!!! Tip
    Before a user starts working with mail, it is recommended to create one or more user signatures. One of them should be selected as the default signature.  
    `Home > Mass mail > Signatures`
