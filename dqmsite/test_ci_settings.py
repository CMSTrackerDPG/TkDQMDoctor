from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'testdb',
        'USER': 'postgres',
        'HOST': 'localhost'
    }
}

# Disable static files server when testing
MIDDLEWARE.remove('whitenoise.middleware.WhiteNoiseMiddleware')


DYNAMIC_PREFERENCES = {
    'ENABLE_CACHE': False,
}
