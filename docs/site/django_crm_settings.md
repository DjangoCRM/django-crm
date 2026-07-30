## Settings of Django CRM

Django-CRM configuration is supplied through **environment variables** (or secret files), not by editing credential literals in tracked `settings.py` files.

### Quick start

1. Copy the template:

```cmd
cp .env.example .env
```

2. Generate a signing key and paste it into `.env`:

```cmd
python manage.py generate_secret_key
```

3. Fill in the remaining values in `.env` using the comments in `.env.example` as a guide.

4. Verify what the process will load (secrets are masked):

```cmd
python manage.py show_config
```

If a mandatory variable is missing, Django aborts at startup with an `ImproperlyConfigured` error naming the variable. Fix the value in `.env` (or provide a secret file) and restart.

### Mandatory variables

| Variable | Required when | Default |
|----------|---------------|---------|
| `DJANGO_SECRET_KEY` | Always (except the test runner) | none |

All other variables are optional for local development with `DJANGO_DEBUG=true`. Production deployments must also supply mail settings when outbound email is enabled, and database settings when not using the default SQLite file.

See `.env.example` for the full list grouped by concern (core Django, database, mail, integrations, URL prefixes).

### Secret files instead of `.env`

Set `DJANGO_SECRETS_DIR` (default `/run/secrets`) and create one file per variable using the lowercase variable name (for example `/run/secrets/django_secret_key`). Environment variables take precedence over secret files.

`show_config` reports the source tier for each key: `environment`, `secret_file`, or `default`.

### Database configuration

Use either:

- `DATABASE_URL` (for example `postgresql://user:pass@localhost/dbname`), or
- discrete `DJANGO_DB_*` variables (see `.env.example`).

The default development configuration uses SQLite (`DJANGO_DB_ENGINE=sqlite3`, `DJANGO_DB_NAME=crm_db`).

For MySQL and PostgreSQL tuning notes, see the [installation guide](../installation_and_configuration_guide.md).

### Mail configuration

Configure outbound mail through `.env`:

| Variable | Purpose |
|----------|---------|
| `EMAIL_HOST` | SMTP server hostname |
| `EMAIL_HOST_USER` | SMTP username |
| `EMAIL_HOST_PASSWORD` | SMTP password (secret) |
| `EMAIL_PORT` | SMTP port (default `587`) |
| `EMAIL_USE_TLS` | Enable TLS (default `true`) |
| `DEFAULT_FROM_EMAIL` | From address |
| `SERVER_EMAIL` | Server error address |
| `DJANGO_ADMINS` | Admin notifications (`Name <email>`) |

When `DJANGO_DEBUG=false` and any mail variable is set, all mail variables must be supplied together.

### Integrations

Optional integration variables (VoIP, reCAPTCHA, Google OAuth2, URL prefixes) are documented in `.env.example`.

### CRM email marketing

This is the **mailing CRM**, so email campaigns are allowed by default.  
If you do not intend to use them, set the `MAILING` parameter to `False` (recommended).  
Learn more about this [CRM and email marketing](https://djangocrm.github.io/info/features/massmail-app-features/){target="_blank"}.

## Upgrade note (environment-variable migration)

If you previously edited `webcrm/settings.py`, `voip/settings.py`, or related files for credentials, migrate to environment variables:

| Legacy location | New variable(s) |
|-----------------|-----------------|
| `SECRET_KEY` | `DJANGO_SECRET_KEY` |
| `DEBUG` | `DJANGO_DEBUG` |
| `ALLOWED_HOSTS` | `DJANGO_ALLOWED_HOSTS` |
| `CSRF_TRUSTED_ORIGINS` | `DJANGO_CSRF_TRUSTED_ORIGINS` |
| `DATABASES` block | `DATABASE_URL` or `DJANGO_DB_*` |
| `EMAIL_*`, `ADMINS` | `EMAIL_*`, `DJANGO_ADMINS` |
| `CRM_IP`, `CRM_HOST` | `CRM_IP`, `CRM_HOST` |
| `CLIENT_ID`, `CLIENT_SECRET` | `GOOGLE_OAUTH2_CLIENT_ID`, `GOOGLE_OAUTH2_CLIENT_SECRET` |
| `GOOGLE_RECAPTCHA_*` | `GOOGLE_RECAPTCHA_SITE_KEY`, `GOOGLE_RECAPTCHA_SECRET_KEY` |
| Zadarma literals in `voip/settings.py` | `ZADARMA_KEY`, `ZADARMA_SECRET`, `ZADARMA_PROVIDER_ALLOWLIST` |
| `SECRET_*_PREFIX` | `SECRET_CRM_PREFIX`, `SECRET_ADMIN_PREFIX`, `SECRET_LOGIN_PREFIX` |

Copy `.env.example` to `.env`, transfer your values, run `python manage.py show_config`, then remove any credential literals from local overrides such as `local_settings.py`.

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
Two users with roles will also be created: **superuser** and **sales manager** (*new in v2.0*). You will be able to modify these accounts and add new ones.  

!!! Note
    Save the credentials of these users from the output data. They will be needed to log in to the CRM website and the website for administrators, respectively.

If you have any difficulties, get [support](https://djangocrm.github.io/info/support/){target="_blank"}.
