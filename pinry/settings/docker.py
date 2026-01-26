import logging

from .base import *


# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY must be set via environment variable or local_settings.py
# Generate a secure key with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
_secret_key = os.environ.get('SECRET_KEY', '')
if not _secret_key or _secret_key in ('PLEASE_REPLACE_ME', 'REPLACE-ME', 'secret_key_place_holder'):
    logging.warning(
        "No valid SECRET_KEY provided in environment. "
        "This will fail in production unless set in local_settings.py"
    )
    # Set a placeholder that will be overridden by local_settings or cause a clear error
    SECRET_KEY = 'INSECURE-DEVELOPMENT-KEY-CHANGE-IN-PRODUCTION'
else:
    SECRET_KEY = _secret_key

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# SECURITY WARNING: use your actual domain name in production!
# Set ALLOWED_HOSTS via environment variable (comma-separated list)
# Example: ALLOWED_HOSTS=example.com,www.example.com
_allowed_hosts = os.environ.get('ALLOWED_HOSTS', '')
if _allowed_hosts:
    ALLOWED_HOSTS = [host.strip() for host in _allowed_hosts.split(',') if host.strip()]
else:
    # Default to localhost only - must be configured for production
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'db',
        'PORT': 5432,
    }
}

USE_X_FORWARDED_HOST = True

REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [
    'rest_framework.renderers.JSONRenderer',
]

# Production security settings
# Enable SSL redirect if behind a trusted proxy or directly serving HTTPS
# Set SECURE_SSL_REDIRECT via environment variable if needed
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'false').lower() == 'true'

# If behind a proxy, trust X-Forwarded-Proto header
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Secure cookies in production (override in local_settings if not using HTTPS)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# should not ignore import error in production, local_settings is required
from .local_settings import *
