## Settings of Django CRM

Project settings are contained in files `settings.py`.  
The main project settings are contained in the file  
`webcrm/settings.py`  

!!! Note
    The syntax of the data in these files must match the syntax of the Python language.

Most of the project settings are Django framework settings.
Their full list is [here](https://docs.djangoproject.com/en/dev/ref/settings/){target="_blank"}.  
The settings missing in this list are [Django CRM](https://github.com/DjangoCRM/django-crm/){target="_blank"} specific settings. Explanations can be found in the comments to them.  
Most of the settings can be left at their default values.

The default settings are for running the project on a development server.
Change them for the production server.  

To start the project for the first time, it is enough to specify the `DATABASES` settings in the file  
`webcrm/settings.py`  
But in the following, you will need to specify at least the `EMAIL_HOST` and `ADMINS` settings.

### DATABASES settings

Provide data to connect to the database.  
Detailed instructions [here](https://docs.djangoproject.com/en/dev/ref/settings/#std-setting-DATABASES){target="_blank"}.  
Configure the `USER` specified in the `DATABASES` setting to have the right to create and drop databases.  
Running tests will create
and then destroy a separate [test database](https://docs.djangoproject.com/en/dev/topics/testing/overview/#the-test-database){target="_blank"}.

#### For MySQL database, it is recommended to  

- setup the timezone table;  
- set the extended encoding:
  - charset `utf8mb4`
  - collation  `utf8mb4_general_ci`

And also if an aggregation or annotation error occurs when running the tests, you need to change sql_mode to `ONLY_FULL_GROUP_BY`.

#### Optimizing PostgreSQL's configuration

You'll need the [psycopg](https://www.psycopg.org/psycopg3/){target="_blank"} or [psycopg2](https://www.psycopg.org/){target="_blank"} package.
Set the timezone to 'UTC' (when USE_TZ is True),
default_transaction_isolation: 'read committed'.  
You can configure them directly in postgresql.conf `(/etc/postgresql/<version>/main/)`

### EMAIL_HOST settings

Specify details for connecting to an email account through which CRM will be able to send notifications to users and administrators.  

- `EMAIL_HOST` (smtp server)
- `EMAIL_HOST_PASSWORD` (password)
- `EMAIL_HOST_USER` (login)

### ADMINS settings

Add the addresses of CRM administrators to the list, so they can receive error logs.  
`ADMINS = [("<Admin1 name>", "<admin1_box@example.com>"), (...)]`

## CRM and database testing

Run the built-in tests:  

```cmd
python manage.py test tests/ --noinput
```

## Installing the initial data

To fill CRM with initial data, you need to execute the command "setupdata" in the root directory of the project:  

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
