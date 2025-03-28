# Welcome to Django-CRM!

## Thank you for your interest in contributing to the project! 

### Contribution opportunities
Code contributions are not the only way to help the project. There are many opportunities to support and contribute:

- Just add a star ⭐️ and fork the repository, this will already be a valuable help for the project.
- Submit GitHub issues about bugs or desired new features.
  - Please follow the <a href="https://github.com/DjangoCRM/django-crm?tab=security-ov-file#security-ov-file" target="_blank">security policy</a>.
- Improving <a href="https://django-crm-admin.readthedocs.io/" title="Django CRM documentation" target="_blank">Documentation</a> and help pages.
- Taking part in creating the project website on the GitHub pages.
  - Localization - the creation of a new or improvement of an existing translation (in context) of the CRM interface:

    <details>
      <summary>How to add a new language or improve the existing translation?</summary>
      Activate a virtual environment (if used) and install the necessary package:  
  
      - Install Rosetta:

        ```cmd
        pip install django-rosetta
        ```

      - Add the following to the `INSTALLED_APPS` list in the `local_settings.py` (if used) or `settings.py` file:

        ```python
        'rosetta',
        ```
      
        Add a new language (if necessary).

        ```python
        LANGUAGES = [
            ("<locale_name>", _("<language_name>")),
            ("en", _("English")),
        ]
        ```
        A locale name, either a language specification of the form **ll** or a combined language and country specification of the form **ll_CC**.  
    
       - Run the following command to create a new language file or update an existing one:
    
        ```cmd
        python manage.py makemessages -l <locale_name>
        ```

      - Run Django server:
          ```cmd
        python manage.py runserver --settings=webcrm.local_settings
        ```
        or 
        ```cmd
        python manage.py runserver 
        ```
      - Open the http://localhost:8000/rosetta/files/project/ in your browser.
      - Select a language and edit the translation.
      - Save the changes (to see the result on the CRM website, you need to restart the server).
      - Create a pull request with the modified files.
    </details>

### Writing Code

The <a href="https://github.com/DjangoCRM/django-crm" title="Client relationship software" target="_blank">Django-CRM project</a> aims to deliver high-level CRM software while keeping it easy to customize, develop, and maintain.  
To achieve this, it follows a key principle: leverage Django's built-in capabilities whenever possible.  
There are at least two good reasons to do so:

- Developers familiar with Django framework will find the CRM code understandable.
- Developers new to Django will benefit from Django's excellent documentation.

We are focused on improving the functionality that has already been created. 
Making it more convenient and understandable for a wide audience of users.  
But now we are also ready to add new features.

- It's easier to start by working with issues marked with a <a href="https://github.com/DjangoCRM/django-crm/labels/good%20first%20issue" target="_blank">“good first issue”</a> label. They are supplied with instructions.
- Create a draft PR when starting work on bigger changes for discussion and assistance.
- A **Task-board** and **Roadmap** are available for **contributors** to obtain additional information.

> [!IMPORTANT]
> **Run tests before creating a Pull Request!**  
> 
> ```cmd
>   python manage.py test tests/ --noinput
> ```

😎👌🔥 We appreciate any contribution!