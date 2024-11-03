## CRM Software installation

To deploy the customer CRM software, you will need: [<img src="../icons/python-logo.svg" alt="python logo" width="30" height="30"> Python](https://www.python.org/){target="_blank"} and database.  
This [Python CRM software](https://github.com/DjangoCRM/django-crm/){target="_blank"} is developed taking into account compatibility with databases:

- [<img src="../icons/mysql_logo.svg" alt="mysql logo" width="30" height="30"> MySQL](https://www.mysql.com/){target="_blank"}
- [<img src="../icons/postgresql_logo.svg" alt="postgresql logo" width="30" height="30"> PostgreSQL](https://www.postgresql.org){target="_blank"}

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

### Install the requirements

It is recommended to first create a virtual environment:

#### on Ubuntu
```cmd
python3 -m venv myvenv
```

and activate it:

```cmd
source /myvenv/bin/activate
```

then install the project requirements:

```cmd
pip install -r requirements.txt
```

#### on Windows

```cmd
py -3.12 -m venv myvenv
```
_('-3.12' is the Python version, change it to yours)_

and activate it:

```cmd
myvenv\Scripts\activate
```

#### Then install the project requirements:

```cmd
pip install -r requirements.txt
```

If the project is deployed on a production server, a website server will also be required
(for example, [Apache](https://httpd.apache.org/){target="_blank"}). Full tutorial [here](https://docs.djangoproject.com/en/dev/topics/install/){target="_blank"}.

!!! Important

    __Give this CRM project a star ⭐️ to support its developers!__  
    Click the "Starred" button in the upper right corner of the [Django CRM GitHub](https://github.com/DjangoCRM/django-crm/){target="_blank"} repository.  
