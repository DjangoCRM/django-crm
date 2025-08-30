
## Renaming CRM fields

If you have a desire or need to rename any fields, you can do it without changing the code.  
Here are two alternatives:

1. If you do not use English as the CRM interface language, then use [translation system](translate_django_crm.md) to change field names without modifying the code.  
For example, when translating "Region/State" you can use the corresponding name of the administrative-territorial unit of your country.  

2. Change the value of the verbose_name field attribute.  
   For example, in the file `crm/models/base_contact.py`:
   ```python
   class BaseContact(models.Model):
       first_name = models.CharField(
           max_length=100,
           verbose_name="Given Name"  # Change "First Name" to "Given Name"
       )
   ```
!!! Note 
    
    In both of these cases, the functionality of the CRM will not be impaired and the CRM software will not need to be changed.