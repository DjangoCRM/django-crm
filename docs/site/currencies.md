## Currencies

<span style="font-size: 25px; color: #23949f">$, €, £, ₴ ...</span>

[Django CRM](https://github.com/DjangoCRM/django-crm/){target="_blank"} supports multiple currencies used in payments and marketing reports.  
It is necessary to specify the national currency and the currency for marketing (these can be different or the same). This will allow users to quickly change the currency of the [analytical reports](guide_for_company_executives.md#crm-analytics).  

Since CRM uses currencies for marketing purposes, users can change the exchange rates themselves. But it is also possible to configure the CRM software to automatically receive accurate exchange rates from a bank or other service in your country <span style='font-size:25px;'>&#128177;</span>.  
To do this, you need to create a backend file, put it in the directory  
`crm/backends`  
You can use already existing backends as a basis.  
Then in the settings file, specify the name of the backend class in the setting  
`LOAD_RATE_BACKEND`
