## Settings of Django CRM

Project settings are contained in files `settings.py`.  
The main project settings are contained in the file  
`webcrm/settings.py`  (*view on [GitHub](https://github.com/DjangoCRM/django-crm/blob/main/webcrm/settings.py){target="_blank"}*). 

!!! IMPORTANT

    The syntax of the data in these files must match the syntax of the [<img src="../icons/python-logo.svg" alt="python logo" width="30" height="30"> Python](https://www.python.org/){target="_blank"} language.

The settings file is divided into two parts:

- Django settings
- CRM settings

Most of the project settings are Django framework settings (full list is [here](https://docs.djangoproject.com/en/dev/ref/settings/){target="_blank"}).  
Explanations for CRM [settings](https://github.com/DjangoCRM/django-crm/blob/main/webcrm/settings.py){target="_blank"} are in the comments to them.  
Most of the settings can be left at their default values.

The default settings are for running the project on a development server.
Change them for the production server.  

To start the project for the first time, you can use the default settings (the built-in SQLite3 database will be used).
To continue using the CRM, please specify other `DATABASES` settings in the file  
`webcrm/settings.py`  
and at least specify the `EMAIL_HOST` and `ADMINS` settings.

### DATABASES settings

Check the `DATABASES` settings to connect to the database (detailed instructions [here](https://docs.djangoproject.com/en/dev/ref/settings/#std-setting-DATABASES){target="_blank"}).  
Configure the `USER` (specified in the `DATABASES`) in your database backend to have the right to create and drop databases.  
Running tests will create
and then destroy a separate [test database](https://docs.djangoproject.com/en/dev/topics/testing/overview/#the-test-database){target="_blank"}.

#### MySQL database

<img src="../icons/mysql_logo.svg" alt="mysql logo" width="30" height="30"> For MySQL database, it is recommended to:

- setup the timezone table
- set the extended encoding:
    - charset `utf8mb4`
    - collation  `utf8mb4_general_ci`

And also if an aggregation or annotation error occurs when running the tests, you need to change sql_mode to `ONLY_FULL_GROUP_BY`.

#### PostgreSQL

<img src="../icons/postgresql_logo.svg" alt="postgresql logo" width="30" height="30"> Optimizing PostgreSQL's configuration:

- Install the [psycopg](https://www.psycopg.org/install/){target="_blank"} package  
    ```cmd
    pip install psycopg[binary]
    ```
- Set the timezone to 'UTC' (when USE_TZ is True)
- `default_transaction_isolation`: 'read committed'

You can configure them directly in postgresql.conf `(/etc/postgresql/<version>/main/)`

### EMAIL_HOST settings

Specify details for connecting to an email account through which CRM will be able to send notifications to users and administrators.

| setting               | description   |
|-----------------------|---------------|
| `EMAIL_HOST`          | *smtp server* |
| `EMAIL_HOST_PASSWORD` | *password*    |
| `EMAIL_HOST_USER`     | *user login*  |

### ADMINS settings

Add the addresses of CRM administrators to the list, so they can receive error logs.  
`ADMINS = [("<Admin1 name>", "<admin1_box@example.com>"), (...)]`

### CRM email marketing

This is the **mailing CRM**, so email campaigns are allowed by default.  
If you do not intend to use them, set the `MAILING` parameter to `False` (recommended).  
Learn more about this [CRM and email marketing](https://djangocrm.github.io/info/features/massmail-app-features/){target="_blank"}.

## CRM and database testing

Run the built-in tests:  

```cmd
python manage.py test tests/ --noinput
```

!!! Tip
    Execute commands in the activated virtual environment.

## Installing the initial data

To fill CRM with initial data, run the "setupdata" command in the root directory of the project: 

```cmd
python manage.py setupdata
```

This command will execute `migrate`, `loaddata` and `createsuperuser`.  
As a result, the database will be populated with objects such as  
countries, [currencies](currencies.md), [departments](adding_crm_users.md#departments), industries, etc.  
Also the superuser will be created.
You will be able to modify them or add your own.  

!!! Note
    Use the superuser credentials from the output to log into the CRM site.

If you have any difficulties, get [support](https://djangocrm.github.io/info/support/){target="_blank"}.