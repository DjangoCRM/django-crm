
# [<img src="img/django-crm_logo.png" alt="Django CRM Screenshot" width="50px" align="center" style="float: center"/>](https://github.com/DjangoCRM/django-crm/){target="_blank"} Welcome to Django-CRM Documentation

[Django CRM](https://github.com/DjangoCRM/django-crm/){target="_blank"} (client relationship software) is an open source application with web interface.  
This CRM is based on the [Django Admin site](https://docs.djangoproject.com/en/dev/ref/contrib/admin/){target="_blank"} and is written in the [Python](https://www.python.org/){target="_blank"} programming language.

[<img src="img/django-crm_deals_screenshot_2x1v2.png" alt="Django CRM Screenshot" align="center" style="float: center"/>](img/django-crm_deals_screenshot_2x1v2.png){target="_blank"}

Django CRM offers a comprehensive CRM solution and consists of the following core applications:

- __TASKS__
- __CRM__
- __ANALYTICS__
- __MASS MAIL__

The TASKS application does not require CRM configuration and allows individual users or teams to work with the following objects:

- [Tasks](tasks_section.md#tasks) -> Subtasks
- Projects -> Tasks -> Subtasks
- [Memos](tasks_section.md#memos) (office memos) -> Projects or Tasks 

Each instance of these objects also has integration with:

- [<span style="vertical-align: baseline"><img src="icons/chat-left-text.svg" alt="Chat icon" width="17" height="17"></span> Chat](tasks_section.md#chat-in-objects)
- <span style="vertical-align: baseline"><img src="icons/tags.svg" alt="tag icon" width="17" height="17"></span>  Tags
- <span style="vertical-align: baseline"><img src="icons/alarm.svg" alt="alarm icon" width="17" height="17"></span> Remainders
- [<span style="vertical-align: baseline"><img src="icons/paperclip.svg" alt="paperclip icon" width="17" height="17"></span> Files](introduction.md#file-object)



Notifications within CRM system and to Email are also available.  
All CRM users have access to this application by default.

Access to the rest of the Django CRM applications is only available to users with the appropriate [roles](adding_crm_users.md#user-groups-roles), such as [sales managers](guide_for_sales_manager.md), [company executives](guide_for_company_executives.md), etc.  
To use all the features of these applications, you need to set up __CRM software integration__:

- with your company's websites
- with your company's mailboxes and sales managers' mailboxes
- if necessary:
    - with the service of receiving [currency](currencies.md) exchange rates
    - with VoIP telephony service 

<button type="button"  style="margin-left: 20%">[CRM Software installation](installation.md)</button> <button type="button" style="float: right; margin-right: 30%">[User guide](introduction.md)</button>