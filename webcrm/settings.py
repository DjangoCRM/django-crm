import sys
from pathlib import Path
from decouple import config
from django.utils.translation import gettext_lazy as _

from crm.settings import *          # NOQA
from massmail.settings import *     # NOQA
from common.settings import *       # NOQA
from tasks.settings import *        # NOQA
from voip.settings import *         # NOQA

# ---- Django settings ---- #

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
# To get new value of key use code:
# from django.core.management.utils import get_random_secret_key
# print(get_random_secret_key())
SECRET_KEY = config('SECRET_KEY', 'j1c=6$s-dh#$ywt@(q4cm=j&0c*!0x!e-qm6k1%yoliec(15tn')

# Add your hosts to the list.
ALLOWED_HOSTS = config('ALLOWED_HOSTS',
                       '*',
                       cast=lambda v: [s.strip() for s in v.split(',')])

# Database
DATABASES = {
    'default': {
        'ENGINE': config('DATABASES_ENGINE', 'django.db.backends.mysql'),
        'PORT': config('DATABASES_PORT', '3306', cast=int),
        'NAME': config('DATABASES_NAME', 'crm_db'),
        'USER': config('DATABASES_USER', 'crm'),
        'PASSWORD': config('DATABASES_PASSWORD', 'crm'),
        'HOST': config('DATABASES_HOST', 'localhost'),
    }
}

EMAIL_HOST = config('EMAIL_HOST', '')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', '')
EMAIL_HOST_USER = config('EMAIL_HOST_USER', 'crm@example.com')
EMAIL_PORT = config('EMAIL_PORT', '587', cast=int)
EMAIL_SUBJECT_PREFIX = config('EMAIL_SUBJECT_PREFIX', 'CRM: ')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', True, cast=bool)
SERVER_EMAIL = config('SERVER_EMAIL', 'crm@example.com')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', 'crm@example.com')

ADMINS = [("<Admin1>", "<admin1_box@example.com>")]   # specify admin

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', 'True', cast=bool)

FORMS_URLFIELD_ASSUME_HTTPS = True

# Internationalization
LANGUAGE_CODE = 'en'
LANGUAGES = [
    ('en', _('English')),
]

TIME_ZONE = 'UTC'   # specify your time zone

USE_I18N = True

USE_TZ = True

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

LOGIN_URL = '/admin/login/'

# Application definition
INSTALLED_APPS = [
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crm.apps.CrmConfig',
    'massmail.apps.MassmailConfig',
    'analytics.apps.AnalyticsConfig',
    'help',
    'tasks.apps.TasksConfig',
    'chat.apps.ChatConfig',
    'voip',
    'common.apps.CommonConfig',
    'settings'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'common.utils.usermiddleware.UserMiddleware'
]

ROOT_URLCONF = 'webcrm.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'webcrm.wsgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

FIXTURE_DIRS = ['tests/fixtures']

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

SITE_ID = 1

SECURE_HSTS_SECONDS = 0  # set to 31536000 for production server
# set to True for production server
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_PRELOAD = False


# ---- CRM settings ---- #

# For more security, replace the url prefixes
# with your own unique value.
SECRET_CRM_PREFIX = '123/'
SECRET_ADMIN_PREFIX = '456-admin/'
SECRET_LOGIN_PREFIX = '789-login/'

# Specify ip of host to avoid importing emails sent by CRM
CRM_IP = "127.0.0.1"

CRM_REPLY_TO = ["'Do not reply' <crm@example.com>"]

# List of addresses to which users are not allowed to send mail.
NOT_ALLOWED_EMAILS = []

TESTING = sys.argv[1:2] == ['test']
if TESTING:
    SECURE_SSL_REDIRECT = False

# List of applications on the main page and in the left sidebar.
APP_ON_INDEX_PAGE = [
    'tasks', 'crm', 'analytics',
    'massmail', 'common', 'settings'
]
MODEL_ON_INDEX_PAGE = {
    'tasks': {
        'app_model_list': ['Task', 'Memo']
    },
    'crm': {
        'app_model_list': [
            'Request', 'Deal', 'Lead', 'Company',
            'CrmEmail', 'Payment', 'Shipment'
        ]
    },
    'analytics': {
        'app_model_list': [
            'IncomeStat', 'RequestStat'
        ]
    },
    'massmail': {
        'app_model_list': [
            'MailingOut', 'EmlMessage'
        ]
    },
    'common': {
        'app_model_list': [
            'UserProfile', 'Reminder'
        ]
    },
    'settings': {
        'app_model_list': [
            'PublicEmailDomain', 'StopPhrase'
        ]
    }
}

# Country VAT value
VAT = 0    # %

# 2-Step Verification Credentials for Google Accounts.
#  OAuth 2.0
CLIENT_ID = ''
CLIENT_SECRET = ''
OAUTH2_DATA = {
    'smtp.gmail.com': {
        'scope': "https://mail.google.com/",
        'accounts_base_url': 'https://accounts.google.com',
        'auth_command': 'o/oauth2/auth',
        'token_command': 'o/oauth2/token',
    }
}
# Hardcoded dummy redirect URI for non-web apps.
REDIRECT_URI = config('REDIRECT_URI','')

# Credentials for Google reCAPTCHA.
GOOGLE_RECAPTCHA_SITE_KEY = config('GOOGLE_RECAPTCHA_SITE_KEY','')
GOOGLE_RECAPTCHA_SECRET_KEY = config('GOOGLE_RECAPTCHA_SECRET_KEY','')

GEOIP = False
GEOIP_PATH = MEDIA_ROOT / 'geodb'

# For user profile list
SHOW_USER_CURRENT_TIME_ZONE = False

NO_NAME_STR = _('Untitled')

# For automated getting currency exchange rate
LOAD_EXCHANGE_RATE = False
LOADING_EXCHANGE_RATE_TIME = "6:30"
LOAD_RATE_BACKEND = config('LOAD_RATE_BACKEND', 'crm.backends.basebackend.BaseBackend')  # "crm.backends.<specify_backend>.<specify_class>"

# Ability to mark payments through a representation
MARK_PAYMENTS_THROUGH_REP = False


# Site headers
SITE_TITLE = 'CRM'
ADMIN_HEADER = "ADMIN"
ADMIN_TITLE = "CRM Admin"
INDEX_TITLE = _('Main Menu')


# This is copyright information. Please don't change it!
COPYRIGHT_STRING = "Django-CRM. Copyright (c) 2024 Vadym Kharchenko"
PROJECT_NAME = "Django-CRM"
PROJECT_SITE = "https://github.com/DjangoCRM/django-crm/"
