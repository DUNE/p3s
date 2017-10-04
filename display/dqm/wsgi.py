"""
WSGI config for display project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os
import sys

sys.path.append("/home/mxp/projects/p3s/display/")
sys.path.append("/home/maxim/projects/p3s/display/dqm/")

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dqm.settings")

application = get_wsgi_application()
