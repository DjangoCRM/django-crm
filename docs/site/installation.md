## CRM Software installation

To deploy the CRM, you will need: [Python](https://www.python.org/) and database.  
This [Python CRM software](https://github.com/DjangoCRM/django-crm/) is developed taking into account compatibility with [MySQL](https://www.mysql.com/) and [PostgreSQL](https://www.postgresql.org) databases.


### Fork the Repository

Click the Fork button in the upper right corner of the [Django CRM GitHub](https://github.com/DjangoCRM/django-crm/) repository's home page.  
You now have a copy of the repository in your personal GitHub account.

### Clone the project

To clone a repository, you must have [Git](https://git-scm.com/downloads) installed on your system and use terminal or cmd.  
Clone this GitHub repository:

```cmd
git clone https://github.com/DjangoCRM/django-crm.git
```

Or clone your forked GitHub repository:

```cmd
git clone https://github.com/<YOUR ACCOUNT NAME>/django-crm.git
```

The project will be cloned into the 'django-crm' folder.

### Install the requirements

It is recommended to first create a virtual environment:

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

If the project is deployed on a production server, a website server will also be required
(for example, [Apache](https://httpd.apache.org/)).  
Full tutorial [here](https://docs.djangoproject.com/en/dev/topics/install/).