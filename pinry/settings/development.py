from .base import *


# SECURITY WARNING: this is a development-only secret key
# Generate a proper key for production with:
# python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
SECRET_KEY = 'django-insecure-dev-key-not-for-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Development mode: allow localhost and common dev hostnames
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'production.db'),
    }
}

INSTALLED_APPS += [
    'django_extensions',
]

try:
    from .local_settings import *
except ImportError:
    pass
