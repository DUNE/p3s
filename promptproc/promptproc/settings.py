"""
Django settings for promptproc project.

Generated by 'django-admin startproject' using Django 1.10.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

# -mxp-
import socket

import databases # from same dir as "manage"

try:
    HOSTNAME = socket.gethostname()
except:
    HOSTNAME = 'localhost'


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'y!m33zq-79&%-!r=e!&+jd2cq&ca85e(4q-9dsgsb4xx)g5p*+'

#DEBUG = False
DEBUG = True # WARNING: don't run with debug turned on in production

# -mxp- Please note this is for strictly development enviroment
# and wiill be meaningless elsewhere
# ALLOWED_HOSTS = ['localhost',
#                  'tranquility.local',
#                  'serenity.local',
#                  'felicity.local',
#                  'ferocity.local',
#                  'sagacity.local',]
ALLOWED_HOSTS = ['*']
# -mxp- common time format
TIMEFORMAT = '%Y%m%d %H:%M:%S'

# -------------------------------------
# Application definition

INSTALLED_APPS = [
    'sites.apps.SitesConfig',
    'workflows.apps.WorkflowsConfig',
    'jobs.apps.JobsConfig',
    'pilots.apps.PilotsConfig',
    'data.apps.DataConfig',
    'logic.apps.LogicConfig',
#
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_tables2'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'promptproc.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR + '/templates/',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.static',
            ],
        },
    },
]

WSGI_APPLICATION = 'promptproc.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases


# Look at the bottom for (previously) working examples

DATABASES = databases.DB


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'


STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "promptproc/static"),
    '/var/www/static/',
# For illustration:
#    '/home/maxim/projects/p3s/promptproc/promptproc/static',
]

############################## LOGGING #########################################

user = ''

# environment variable may not be set for the system-specific
# userID of the Apache server, so add some boilerplate to handle this
# Same as "getpass" but allows us to tweak the behavior of needed.


try:
    user = os.environ['LOGNAME']
except:
    pass
try:
    user = os.environ['USER']
except:
    pass
try:
    user = os.environ['LNAME']
except:
    pass
try:
    user = os.environ['USERNAME']
except:
    pass

if(user==''):
    LOG_DIR = '/tmp/p3s/'
else:
    LOG_DIR = '/tmp/'+user+'/p3s/'

if(not os.path.exists(LOG_DIR)):
    os.makedirs(LOG_DIR)
    
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': LOG_DIR+'server.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'pilots': {
            'handlers': ['file'],
            'level': 'INFO',
        },
        'workflows': {
            'handlers': ['file'],
            'level': 'INFO',
        },
        'logic': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}
################################################################################
# DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#        'OPTIONS': {'timeout': 1000,},
#    }
#}


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': '',
#         'USER': '',
#         'PASSWORD': '',
#         'HOST': '',
#         'PORT': '',
#     }
# }
