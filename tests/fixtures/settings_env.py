"""Reusable environment dictionaries for settings integration tests."""

_PRODUCTION_MAIL = {
    'EMAIL_HOST': 'smtp.example.com',
    'EMAIL_HOST_USER': 'crm@example.com',
    'EMAIL_HOST_PASSWORD': 'placeholder-mail-password',
    'EMAIL_PORT': '587',
    'EMAIL_USE_TLS': 'true',
    'DEFAULT_FROM_EMAIL': 'test@example.com',
    'SERVER_EMAIL': 'test@example.com',
}

VALID_PRODUCTION_ENV = {
    'DJANGO_SECRET_KEY': 'test-production-secret-key-not-for-production-use',
    'DJANGO_DEBUG': 'false',
    'DJANGO_ALLOWED_HOSTS': 'crm.example.com,www.crm.example.com',
    'DJANGO_CSRF_TRUSTED_ORIGINS': 'https://crm.example.com,https://www.crm.example.com',
    'DJANGO_DB_ENGINE': 'sqlite3',
    'DJANGO_DB_NAME': ':memory:',
    **_PRODUCTION_MAIL,
}

DEBUG_ENV = {
    'DJANGO_SECRET_KEY': 'test-debug-secret-key-not-for-production-use',
    'DJANGO_DEBUG': 'true',
    'DJANGO_ALLOWED_HOSTS': 'localhost,127.0.0.1',
    'DJANGO_CSRF_TRUSTED_ORIGINS': 'http://localhost,http://127.0.0.1',
    'DJANGO_DB_ENGINE': 'sqlite3',
}

INCOMPLETE_ENV = {
    'DJANGO_DEBUG': 'false',
    'DJANGO_ALLOWED_HOSTS': 'localhost',
}

PRODUCTION_STARTUP_ENV = {
    'DJANGO_SECRET_KEY': 'test-production-secret-key-not-for-production-use',
    'DJANGO_ALLOWED_HOSTS': 'localhost',
    **_PRODUCTION_MAIL,
}
