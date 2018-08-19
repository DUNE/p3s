import os

LIMITS = {
    'purity': {
        'min':	'2.7',
        'max':	'10000.0'
        },
    'sn': {
        'min':	'4.0',
        'max':	'10000.0'
        },
}


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'p3s',
        'USER': 'p3s',
        'PASSWORD': 'mxp',
        'HOST': '',
        'PORT': '',
    }
}
