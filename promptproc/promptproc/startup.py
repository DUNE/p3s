# Startup definitions. A placeholder for now.

#from django.conf	import settings
#from django.db	import connection

def run():
    print('*** Starting the p3s server on host "%s" ***' % 'p3s') #settings.HOSTNAME)
    
#    sqliteTO = 'PRAGMA busy_timeout = 2000;'
    
#    cursor = connection.cursor()
#    cursor.execute(sqliteTO)

#The following is blocked by Django (security reasons?):
#import sys
#import os.path
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
#import module_in_parent_dir
