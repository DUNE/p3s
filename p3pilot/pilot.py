#!/usr/bin/python
'''This is a stub for the p3s pilot'''

from django.conf import settings
from django.utils import timezone

import os
import argparse
import uuid
import socket
import time
import datetime
import logging

import urllib
from urllib import request
from urllib import error
from urllib import parse

from urllib.error import URLError

#########################################################
settings.configure(USE_TZ = True)
# NB. wec ould use ts = str(datetime.datetime.now())
# but in Django this will cause problems with DB due to being
# not TZ-aware

#-------------------------
class Pilot(dict):
    def __init__(self):
        self['state']	= 'active' # FIXME
        self['host']	= socket.gethostname()
        self['site']	= 'default' # FIXME - will need to get from env
        self['ts']	= str(timezone.now())
        self['uuid']	= uuid.uuid1()
        self.timeout	= 3
        self.period	= 1
        
#-------------------------
parser = argparse.ArgumentParser()

parser.add_argument("-S", "--server",
                    type=str,
                    default='http://localhost:8000/',
                    help="the server address, defaults to http://localhost:8000/")

parser.add_argument("-w", "--workdir",
                    type=str,
                    default='/tmp',
                    help="(defaults to /tmp) the path for all pilots keep their logs etc")

parser.add_argument("-U", "--url",
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
workdir = args.workdir
# numbers
verb	= args.verbosity
# Boolean
tst	= args.test

# dummy for now
register= args.register
########################################################################


# create and serialize pilot
p = Pilot()

# Check if we can create a working directory
# Example: /tmp/p3s/"pilot uuid"

if not os.path.exists(workdir):
    exit(-1)

allpilotdir = workdir+'/p3pilot'
if not os.path.exists(allpilotdir):
    try:
        os.mkdir(allpilotdir)
    except:
        exit(-1)

logfilename = allpilotdir+'/'+str(p['uuid'])+'.log'

if(verb>0):
    print(logfilename)

logger = logging.getLogger('p3pilot')
logger.setLevel(logging.DEBUG)
logfile = logging.FileHandler(logfilename)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logfile.setFormatter(formatter)

logger.addHandler(logfile)
logger.info('starting pilot %s' % str(p['uuid']))


# the pilot is a dict, so encoding is automatic:
pilotData = urllib.parse.urlencode(p)
pilotData = pilotData.encode('UTF-8')

if(verb>0):
    print(pilotData)


if(tst): # if in test mode simply bail
    exit(0)

url	= "pilots/addpilot"
fullurl	= server+url
try:
    response = urllib.request.urlopen(fullurl, pilotData)
except URLError:
    logger.error('when contacting the server at %s' % fullurl)
    exit(1)
    

logger.info("contact with server successful")

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
    time.sleep(10)
    cnt-=1

logger.info('exiting normally')
exit(0)



# bits for later
#    if(register):	# POST
#else:		# GET

      

# headers		= response.info()
# data		= response.read()

# response_url	= response.geturl()
# response_date	= headers['date']
