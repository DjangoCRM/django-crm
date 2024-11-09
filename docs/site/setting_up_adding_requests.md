# Setting up adding commercial requests in Django CRM

In [Django CRM](https://github.com/DjangoCRM/django-crm/){target="_blank"} you can add commercial requests (Request objects) in manual, automatic and semi-automatic mode.
In manual mode, you must press the "ADD REQUESTS" button at:  
  `Home > Crm > Requests`  
and fill out the form.

Requests coming from forms on your company's website are automatically created (if configured accordingly).  
In a semi-automatic mode, requests are created by sales managers or operators when importing emails received to their mail into CRM.  
To do this, you need to specify the details of their [mail accounts](setting_up_email_accounts.md) to ensure CRM access to these accounts.
CRM automatically assigns the owner of the imported request to the owner of the email account.

### Sources of Leads

`(ADMIN) Home > Crm > Lead Sources`  
For marketing purposes, each [Request](operator_and_sales_manager_roles.md#working-with-requests), [Lead](operator_and_sales_manager_roles.md#lead-object), [Contact](operator_and_sales_manager_roles.md#object-of-company-contact-persons) and [Company](operator_and_sales_manager_roles.md#company-object) object has a link to the corresponding "Lead Source" object.  
Each Lead Source is identified by the value of its UUID field, which is generated automatically when a new Lead Source is added to the CRM.  
For convenience, CRM has a number of pre-defined "Leads Sources". These can be edited.
Each "Lead Source" has a link to a "Department". Therefore, each department can have its own set of lead sources.  
The "Form template name" and "Success page template name" fields are only populated when [adding a custom iframe form](#adding-a-custom-crm-form-for-iframe).  
The "Email" field is only specified in the "Lead Source" of your website. You need to specify the Email value indicated on your site.

### Contact forms

CRM can automatically receive data from contact forms on your company's websites and, based on it, create commercial requests in the database.
To do this, you need to configure the site to send POST form data via a request to CRM. Or use CRM forms by adding them to sites via iframe.

#### Submitting form data with a POST request

Your site can pass the values of the following form fields to CRM by POST request:  

| Form field         | Description                                       |
|--------------------|---------------------------------------------------|
| `name`             | CharField (max_length=200, required)              |
| `email`            | EmailField / CharField (max_length=254, required) |
| `subject`          | CharField (max_length=200, required)              |
| `phone`            | CharField (max_length=200, required)              |
| `company`          | CharField (max_length=200, required)              |
| `message`          | TextField                                         |
| `country`          | CharField (max_length=40)                         |
| `city`             | CharField (max_length=40)                         |
| `leadsource_token` | UUIDField (required, hidden input)                |

The value of the "leadsource_token" field must match the value of the "UUID" field of the corresponding (selected by you) "Leadsource".  
`(ADMIN site) Home > Crm > Lead Sources`

Url for POST request:  
`https://<yourCRM.domain>/<language_code>/add-request/`

#### Embedding CRM form in an iframe of a website page

Place an iframe string in the HTML code of a website page.  
Here is an example of a simple string:

```HTL
<iframe src="<url>" style="width: 600px;height: 450px;"></iframe>
```

url must follow the format:  
`https://<yourCRM.domain>/<language_code>/contact-form/<uuid>/`  
where uuid is the values of the "UUID" field of the selected "Lead Source".

#### Activate form protection with Google's reCAPTCHA v3

CRM form has built-in reCAPTCHA v3 protection.  
To activate it, specify the values of keys received during registration on this service:  

```
GOOGLE_RECAPTCHA_SITE_KEY = "<your site key>"  
GOOGLE_RECAPTCHA_SECRET_KEY = "<your secret key>"
```

#### Activation of geolocation of the country and city of the counterparty by its IP

CRM form has a built-in ability to geolocate the country and city of the leads (site visitor) by its IP.  
For this purpose, GeoIP2 module is used.  
To activate its work:

- save the [MaxMind](https://dev.maxmind.com/geoip/docs/databases){target="_blank"} files of the city and country databases (GeoLite2-Country.mmdb and GeoLite2-City.mmdb) to the `media/geodb` directory;
- set `GEOIP = True` in the file

#### Adding a custom CRM form for iframe

You can change the style of a preset form or add forms with different styles to fit on different pages of the site or on different sites.  
To add a new form, place the HTML template for that form and the successful form submission message template at the following location:  
`<crmproject>/crm/templates/crm/`

Save the names of these files in the "Form template name" and "Success page template name" fields of the selected "Lead Source" in the following format:  
 `"crm/<file name>.html"`
