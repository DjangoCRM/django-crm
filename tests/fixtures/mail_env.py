"""Reusable mail environment dictionaries for settings tests."""

COMPLETE_MAIL_ENV = {
    'DJANGO_SECRET_KEY': 'test-mail-secret-key-not-for-production-use',
    'DJANGO_DEBUG': 'false',
    'DJANGO_ALLOWED_HOSTS': 'crm.example.com',
    'DJANGO_DB_ENGINE': 'sqlite3',
    'DJANGO_DB_NAME': ':memory:',
    'EMAIL_HOST': 'smtp.example.com',
    'EMAIL_HOST_USER': 'crm@example.com',
    'EMAIL_HOST_PASSWORD': 'placeholder-mail-password',
    'EMAIL_PORT': '587',
    'EMAIL_USE_TLS': 'true',
    'EMAIL_USE_SSL': 'false',
    'DEFAULT_FROM_EMAIL': 'test@example.com',
    'SERVER_EMAIL': 'test@example.com',
    'DJANGO_ADMINS': 'Admin1 <admin1_box@example.com>',
    'CRM_IP': '127.0.0.1',
    'CRM_HOST': 'my_crm_host_name',
    'GOOGLE_OAUTH2_CLIENT_ID': 'placeholder-client-id',
    'GOOGLE_OAUTH2_CLIENT_SECRET': 'placeholder-client-secret',
}

CHARACTERIZATION_MAIL_ENV = {
    'DJANGO_SECRET_KEY': 'test-mail-secret-key-not-for-production-use',
    'DJANGO_DEBUG': 'true',
    'DJANGO_ALLOWED_HOSTS': 'localhost,127.0.0.1',
    'DJANGO_DB_ENGINE': 'sqlite3',
    'EMAIL_HOST': 'smtp.example.com',
    'EMAIL_HOST_USER': 'crm@example.com',
    'EMAIL_HOST_PASSWORD': 'placeholder-mail-password',
    'EMAIL_PORT': '587',
    'EMAIL_USE_TLS': 'true',
    'DEFAULT_FROM_EMAIL': 'test@example.com',
    'SERVER_EMAIL': 'test@example.com',
    'DJANGO_ADMINS': 'Admin1 <admin1_box@example.com>',
}

DEBUG_NO_MAIL_ENV = {
    'DJANGO_SECRET_KEY': 'test-mail-secret-key-not-for-production-use',
    'DJANGO_DEBUG': 'true',
    'DJANGO_ALLOWED_HOSTS': 'localhost,127.0.0.1',
    'DJANGO_DB_ENGINE': 'sqlite3',
}

INCOMPLETE_MAIL_ENV = {
    'DJANGO_SECRET_KEY': 'test-mail-secret-key-not-for-production-use',
    'DJANGO_DEBUG': 'false',
    'DJANGO_ALLOWED_HOSTS': 'crm.example.com',
    'DJANGO_DB_ENGINE': 'sqlite3',
    'DJANGO_DB_NAME': ':memory:',
    'EMAIL_HOST': 'smtp.example.com',
}

LOC_MEM_MAIL_ENV = {
    'DJANGO_SECRET_KEY': 'test-mail-secret-key-not-for-production-use',
    'DJANGO_DEBUG': 'false',
    'DJANGO_ALLOWED_HOSTS': 'crm.example.com',
    'DJANGO_DB_ENGINE': 'sqlite3',
    'DJANGO_DB_NAME': ':memory:',
    'EMAIL_HOST': 'smtp.example.com',
    'EMAIL_HOST_USER': 'crm@example.com',
    'EMAIL_HOST_PASSWORD': 'placeholder-mail-password',
    'EMAIL_PORT': '587',
    'EMAIL_USE_TLS': 'true',
    'DEFAULT_FROM_EMAIL': 'noreply@example.com',
    'SERVER_EMAIL': 'noreply@example.com',
    'DJANGO_ADMINS': 'Ops Team <ops@example.com>, Admin <admin@example.com>',
}
