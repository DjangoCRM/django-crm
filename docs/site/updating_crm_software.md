## Updating Django CRM software

Django CRM open source system is actively developing: existing functionality is being improved, new functionality is being added, and bugs are being fixed.
In addition, the versions of software used by CRM are updated.
Therefore, it is important to set up system updates based on new releases of [CRM softwares](https://github.com/DjangoCRM/django-crm/){target="_blank"}.
Here are some tips on how to do it better:

- To prevent your system settings from being overwritten when you upgrade CRM software, it is recommended that you save them in a separate settings file, such as `local_settings.py`.
In this file, add the line `from .settings import *` and save all your settings. In this way, the default project settings contained in the settings.py file will be overwritten by your settings.
In the future, specify your settings file when launching CRM system.

```cmd
python manage.py runserver --settings=webcrm.local_settings
```

- The new release may contain database migration files, so you need to run the migration command.

```cmd
python manage.py migrate --settings=webcrm.local_settings
```

- A new release may contain new or modified static files. Therefore, the static files collection command must be run on the production server.

```cmd
python manage.py collectstatic --settings=webcrm.local_settings
```

!!! Tip
    Provide meaningful comments on the code you are modifying. This will help in case of conflict when merging your project with a new [Django-CRM releases](https://github.com/DjangoCRM/django-crm/releases){target="_blank"}.
