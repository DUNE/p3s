#!/usr/bin/python

'''This is a stub for the p3s pilot'''
#!/usr/bin/python
from django.conf import settings

import argparse
import uuid
import socket
import datetime

from django.utils import timezone

import urllib
from urllib import request
from urllib import error
from urllib import parse

from urllib.error import URLError

#-------------------------
parser = argparse.ArgumentParser()

parser.add_argument("-s", "--server",
                    type=str,
                    default='http://localhost:8000/',
                    help="the server address, defaults to http://localhost:8000/")

parser.add_argument("-u", "--url",
                    type=str,
                    default='',
                    help="url of the query to be added, defaults to empty string")

parser.add_argument("-t", "--test",
                    action='store_true',
                    help="when set, forms a request but does not contact the server")

parser.add_argument("-r", "--register",
                    action='store_true',
                    help="when set, the pilot will attempt to register with the server")

parser.add_argument("-v", "--verbosity",
                    type=int,
                    default=0, choices=[0, 1, 2],
                    help="increase output verbosity")

settings.configure(USE_TZ = True)

########################### Parse all arguments #########################
args = parser.parse_args()

# strings
server	= args.server
url	= args.url
# numbers
verb	= args.verbosity
# Boolean
tst	= args.test
register= args.register
########################################################################

# find pilot parameters

pilotID	= uuid.uuid1()
host	= socket.gethostname()

# This will work but it's not TZ aware so there will be runtime warnings
# from the backend DB on the server side: ts = str(datetime.datetime.now())

ts	= str(timezone.now())

pilotData= urllib.parse.urlencode({'uuid' : pilotID, 'host' : host, 'ts' : ts})

pilotData = pilotData.encode('UTF-8')

if(verb>0):
    print(pilotData)

# if in test mode simply bail
if(tst):
    exit(0)

# contact the server
try:
    if(register):	# POST
        response = urllib.request.urlopen(server+url, pilotData)
    else:		# GET
        response = urllib.request.urlopen(server+url)
        
except URLError:
    exit(1)		# silent exit with an error code set
    
# get the reponse from the server    
headers		= response.info()
data		= response.read()

response_url	= response.geturl()
response_date	= headers['date']

if(verb >0):
    print (data)
    
exit(0)

