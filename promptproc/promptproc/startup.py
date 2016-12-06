# Startup definitions. A placeholder for now.

from django.conf import settings

def run():
    print('*** Starting the p3s server on host "%s" ***' % settings.HOSTNAME)

# The following is blocked by Django:
#import sys
#import os.path
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
#import module_in_parent_dir
