from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

DYNAMIC_PREFERENCES = {
    'ENABLE_CACHE': False,
}
