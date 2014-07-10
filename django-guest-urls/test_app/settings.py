"""Test app settings."""
from os import environ

# set the django DEBUG option
DEBUG = environ.get('DJANGO_DEBUG', 'true').lower() == 'true'

ROOT_URLCONF = 'test_app.urls'

TIME_ZONE = 'UTC'
USE_TZ = True

# this isn't used, but Django likes having something here for running the tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'delme'
    }
}

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'guest_urls',
    'test_app',
)

SECRET_KEY = "something really, really hard to guess goes here."

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG',
        },
    }
}
