"""Reusable VoIP, reCAPTCHA and URL prefix environment dictionaries for tests."""

VALID_VOIP_ENV = {
    'DJANGO_SECRET_KEY': 'test-voip-secret-key-not-for-production-use',
    'DJANGO_DEBUG': 'false',
    'DJANGO_ALLOWED_HOSTS': 'crm.example.com',
    'DJANGO_DB_ENGINE': 'sqlite3',
    'DJANGO_DB_NAME': ':memory:',
    'EMAIL_HOST': 'smtp.example.com',
    'EMAIL_HOST_USER': 'crm@example.com',
    'EMAIL_HOST_PASSWORD': 'placeholder-mail-password',
    'DEFAULT_FROM_EMAIL': 'test@example.com',
    'SERVER_EMAIL': 'test@example.com',
    'ZADARMA_KEY': 'placeholder-zadarma-key',
    'ZADARMA_SECRET': 'placeholder-zadarma-secret',
    'ZADARMA_PROVIDER_ALLOWLIST': '185.45.152.42,203.0.113.10',
    'GOOGLE_RECAPTCHA_SITE_KEY': 'placeholder-recaptcha-site-key',
    'GOOGLE_RECAPTCHA_SECRET_KEY': 'placeholder-recaptcha-secret-key',
}

CHARACTERIZATION_VOIP_ENV = {
    'DJANGO_SECRET_KEY': 'test-voip-secret-key-not-for-production-use',
    'DJANGO_DEBUG': 'true',
    'DJANGO_ALLOWED_HOSTS': 'localhost,127.0.0.1',
    'DJANGO_DB_ENGINE': 'sqlite3',
    'ZADARMA_KEY': '123',
    'ZADARMA_SECRET': 'secret',
    'ZADARMA_PROVIDER_ALLOWLIST': '185.45.152.42',
    'SECRET_CRM_PREFIX': '123/',
    'SECRET_ADMIN_PREFIX': '456-admin/',
    'SECRET_LOGIN_PREFIX': '789-login/',
}

UNCONFIGURED_VOIP_ENV = {
    'DJANGO_SECRET_KEY': 'test-voip-secret-key-not-for-production-use',
    'DJANGO_DEBUG': 'true',
    'DJANGO_ALLOWED_HOSTS': 'localhost,127.0.0.1',
    'DJANGO_DB_ENGINE': 'sqlite3',
}

CUSTOM_PREFIX_ENV = {
    'DJANGO_SECRET_KEY': 'test-voip-secret-key-not-for-production-use',
    'DJANGO_DEBUG': 'true',
    'DJANGO_ALLOWED_HOSTS': 'localhost,127.0.0.1',
    'DJANGO_DB_ENGINE': 'sqlite3',
    'SECRET_CRM_PREFIX': '/custom-crm/',
    'SECRET_ADMIN_PREFIX': 'custom-admin',
    'SECRET_LOGIN_PREFIX': 'custom-login/',
}

WEBHOOK_VOIP_ENV = {
    **VALID_VOIP_ENV,
    'ZADARMA_PROVIDER_ALLOWLIST': '185.45.152.42',
}
