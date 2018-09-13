from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable static files server when testing
MIDDLEWARE.remove('whitenoise.middleware.WhiteNoiseMiddleware')


DYNAMIC_PREFERENCES = {
    'ENABLE_CACHE': False,
}
