#!/usr/bin/python
'''This is a stub for the p3s pilot'''

from django.conf import settings

import argparse
import uuid
import socket
import time
import datetime

from django.utils import timezone

import urllib
from urllib import request
from urllib import error
from urllib import parse

from urllib.error import URLError

settings.configure(USE_TZ = True)

#-------------------------
class Pilot(dict):
    def __init__(self):
        self['host']	= socket.gethostname()
        self['ts']	= str(timezone.now())	# This will work but it's not TZ aware
        					# so there will be runtime warnings
						# from the backend DB on the server side:
                                                # ts = str(datetime.datetime.now())
        self['uuid']	= uuid.uuid1()
        self.timeout	= 10
        self.period	= 1
        
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


# create and serialize pilot
p = Pilot()
pilotData = urllib.parse.urlencode(p)
pilotData = pilotData.encode('UTF-8')

if(verb>0):
    print(pilotData)


if(tst): # if in test mode simply bail
    exit(0)

try:
    url = "pilots/addpilot"
    response = urllib.request.urlopen(server+url, pilotData)
except URLError:
    exit(1)		# silent exit with an error code set
    

data = response.read()
if(verb >0):
    print (data)


cnt = p.timeout
url = "pilots/request/?uuid=%s" % p['uuid']
while(cnt>0):
    print(cnt)
    response = urllib.request.urlopen(server+url)
    data = response.read()
    print('-->',data)
    time.sleep(1)
    cnt-=1
exit(0)



# bits for later
#    if(register):	# POST
#else:		# GET

      

# headers		= response.info()
# data		= response.read()

# response_url	= response.geturl()
# response_date	= headers['date']
