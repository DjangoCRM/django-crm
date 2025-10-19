## installation of CRM Software 

To deploy the customer CRM software, you will need
[<img src="../icons/python-logo.svg" alt="python logo" width="30" height="30"> Python](https://www.python.org/){target="_blank"} 3.10+.  
For initial familiarization with the CRM, you can use the built-in SQLite3 database (default settings),
but it is not suitable for regular use.  
This [Python CRM software](https://github.com/DjangoCRM/django-crm/){target="_blank"} is developed taking into account compatibility with databases:

- [<img src="../icons/mysql_logo.svg" alt="mysql logo" width="30" height="30"> MySQL](https://www.mysql.com/){target="_blank"} 8.0.11+
- [<img src="../icons/postgresql_logo.svg" alt="postgresql logo" width="30" height="30"> PostgreSQL](https://www.postgresql.org){target="_blank"} 14+

You can __fork__, __clone__ or __download__ the project __software__.

### Fork the Repository

Click the Fork button in the upper right corner of the [Django CRM GitHub](https://github.com/DjangoCRM/django-crm/){target="_blank"} repository's home page.  
You now have a copy of the repository in your personal GitHub account.

### Clone the project

To clone a repository on your computer or server, you must have [Git](https://git-scm.com/downloads){target="_blank"} installed on your system and use terminal or cmd.  
Clone the GitHub repository:

```cmd
git clone https://github.com/DjangoCRM/django-crm.git
```

Or clone your forked GitHub repository:

```cmd
git clone https://github.com/<YOUR ACCOUNT NAME>/django-crm.git
```

The project will be cloned into the "django-crm" folder.

### Free CRM software download

You can download the CRM software as a zip file and then unzip it to a directory of your choice.

<a class="btn button" href="https://github.com/DjangoCRM/django-crm/archive/refs/heads/main.zip" style="margin-left: 20%">Download CRM Software</a>

### Install the requirements

To run CRM software on your computer/server, you need to install certain dependencies.  
It is recommended to first create and activate a Python virtual environment:

| Action   | Unix/macOS                    | Windows                   |
|----------|-------------------------------|---------------------------|
| create   | `python3 -m venv myvenv`      | `py -m venv myvenv`       |
| activate | `source /myvenv/bin/activate` | `myvenv\Scripts\activate` |

#### Then install the project requirements

```cmd
pip install -r requirements.txt
```

__That's it!__

If the project is deployed on a production server, a website server will also be required
(for example, [Apache](https://httpd.apache.org/){target="_blank"}). Full tutorial [here](https://docs.djangoproject.com/en/dev/topics/install/){target="_blank"}.

!!! Important

    __Please give this CRM project a star ⭐️ to support its developments!__  
    Click the "Starred" button in the upper right corner of the [Django CRM GitHub](https://github.com/DjangoCRM/django-crm/){target="_blank"} repository.  
