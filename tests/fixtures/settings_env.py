"""Reusable environment dictionaries for settings integration tests."""

VALID_PRODUCTION_ENV = {
    'DJANGO_SECRET_KEY': 'test-production-secret-key-not-for-production-use',
    'DJANGO_DEBUG': 'false',
    'DJANGO_ALLOWED_HOSTS': 'crm.example.com,www.crm.example.com',
    'DJANGO_CSRF_TRUSTED_ORIGINS': 'https://crm.example.com,https://www.crm.example.com',
    'DJANGO_DB_ENGINE': 'sqlite3',
    'DJANGO_DB_NAME': ':memory:',
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
