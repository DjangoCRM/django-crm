## Translating Django CRM interface into another language

Users can choose the language of the [Django CRM](https://github.com/DjangoCRM/django-crm/){target="_blank"} interface.  
The list of available languages `LANGUAGES` and the default language `LANGUAGE_CODE` are defined in the file:
`webcrm/settings.py`

Add the desired language, e.g., German:  

```cmd
LANGUAGES = [
    ("de", _("German")),
    ("en", _("English")),
]
```

Save the file.  
Run the following command in the terminal in the root directory of the project:

```cmd
python manage.py makemessages -l de
```

In the directory  
`locale/de/LC_MESSAGES`  
django.po file will appear.  
Use the po file editor to translate its contents and create a mo file.  
Put the mo file in the same directory.

The CRM remembers the user's language choice, so there is no need to change the default language.

Restart CRM.

If the objects you added, such as deal stages, reasons for closing deals, have names in English, these names can also be translated. To do this, perform the above steps again, starting with the `makemessages` command.

More details [here](https://docs.djangoproject.com/en/5.0/topics/i18n/translation/){target="_blank"}.
