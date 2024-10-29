## Currencies

Since CRM uses currencies for marketing purposes, users can change the exchange rates themselves.  
But it is also possible to configure CRM to automatically receive accurate exchange rates from a bank or other service in your country.  
To do this, you need to create a backend file, put it in the directory  
`crm/backends`  
You can use already existing backends as a basis.  
Then in the settings file, specify the name of the backend class in the setting  
`LOAD_RATE_BACKEND`
