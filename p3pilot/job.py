#!/usr/bin/python

from django.conf import settings
from django.utils import timezone

import argparse
import uuid
import socket
import time
import datetime

import urllib
from urllib import request
from urllib import error
from urllib.error import URLError

#########################################################
settings.configure(USE_TZ = True)

#-------------------------
class Job(dict):
    def __init__(self):
        self['uuid']	= uuid.uuid1()
        self['stage']	= 'default'
        self['priority']= 0
        self['subhost']	= socket.gethostname() # submission host
        self['ts']	= str(timezone.now()) # ts = str(datetime.datetime.now()): problems with DB due to TZ
        

#-------------------------
parser = argparse.ArgumentParser()

parser.add_argument("-s", "--server",
                    type=str,
                    default='http://localhost:8000/',
                    help="the server address, defaults to http://localhost:8000/")

parser.add_argument("-t", "--test",
                    action='store_true',
                    help="when set, forms a request but does not contact the server")

parser.add_argument("-u", "--url", type=str, default='jobs/addjob')

parser.add_argument("-v", "--verbosity", type=int, default=0, choices=[0, 1, 2],
                    help="increase output verbosity")

########################### Parse all arguments #########################
args = parser.parse_args()

server	= args.server
url	= args.url
verb	= args.verbosity
tst	= args.test
########################################################################

# create and serialize job
j = Job()
jobData = urllib.parse.urlencode(j)
jobData = jobData.encode('UTF-8')

if(verb>0):
    print(jobData)

if(tst): # if in test mode simply bail
    exit(0)


try:
    response = urllib.request.urlopen(server+url, jobData)
except URLError:
    exit(1)
    
data = response.read()

if(verb >0):
    print (data)
    
exit(0)

