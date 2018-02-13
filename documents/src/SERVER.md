# Instructions for p3s server maintenance

## Installation

Clone the p3s repo from GitHub. The directory
**p3s/promptproc** will contain the server code.

## The "local" configuration file

Inspect the directory p3s/promptproc. On a machine
which hosts a working instance of p3s service it should contain
a file named "local.py" which is created by the installer
and is not version controlled so sensitive information
may not be gleaned from the repository. A template
is provided below. Most important settings are:

* definition of the DB backend
* time zone

```
SITE = {
    'dirpath':          '/home/maxim/p3sdata',
    'p3s_users':        'All,maxim,mxp,dladams',
    'p3s_input':        '/home/maxim/p3sdata/input',
    'p3s_output':       '/home/maxim/p3sdata/output',
    'p3s_users':        'All,maxim,mxp,dladams',
    'p3s_jobtypes':     'All,type1,type2,type3,sleep,noop',
    'p3s_services':     'All,TO,purge',
    'dqm_domain':       'serenity.local:8000',
    'dqm_host':         'serenity',
    'tz':		'America/New_York'
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '***',
        'USER': '***',
        'PASSWORD': '***',
        'HOST': '',
        'PORT': '',
    }
}

```