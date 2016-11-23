#!/usr/bin/python
#########################################################
# TZ-awarewness:					#
# The following is not TZ-aware: datetime.datetime.now()#
# so we are using timzone.now() where needed		#
#########################################################
# General Python:
import os
import argparse
import uuid
import socket
import time
import datetime
import logging
import json

# Django
from django.conf	import settings
from django.utils	import timezone


import urllib
from urllib		import request
from urllib		import error
from urllib		import parse
from urllib.error	import URLError

# local import, requires PYTHONPATH to be set
from comms import data2post

#########################################################
settings.configure(USE_TZ = True) # see the above note on TZ


# simple utilities
#-------------------------
def rdec(r):
    return r.read().decode('utf-8')

#-------------------------
def communicate(url, data=None):
    try:
        if(data):
            return urllib.request.urlopen(url, data)
        else:
            return urllib.request.urlopen(url)
    except URLError:
        logger.error('exiting, error at URL: %s' % url)
        exit(1)

#-------------------------
class Pilot(dict):
    def __init__(self):
        self['state']	= 'active' # start as active
        self['status']	= '' # status of server comms
        self['host']	= socket.gethostname()
        self['site']	= 'default' # FIXME - will need to get from env
        self['ts']	= str(timezone.now())
        self['uuid']	= uuid.uuid1()
        self.cycles	= 1
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

##################### CREATE A PILOT ###################################
p = Pilot() # need uuid for the logfile etc, so do it now
################### BEGIN: PREPARE LOGGER ##############################
# Check if we can create a working directory
# Example: /tmp/p3s/"pilot uuid"

if not os.path.exists(workdir): exit(-1)

allpilotdir = workdir+'/p3pilot'
if not os.path.exists(allpilotdir):
    try:
        os.mkdir(allpilotdir)
    except:
        exit(-1)

logfilename = allpilotdir+'/'+str(p['uuid'])+'.log'

if(verb>0): print("Logfile: %s" % logfilename)

logger = logging.getLogger('p3pilot')
logger.setLevel(logging.DEBUG)
logfile = logging.FileHandler(logfilename)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logfile.setFormatter(formatter)

logger.addHandler(logfile)
##################### END: PREPARE LOGGER ##############################

logger.info('starting pilot %s' % str(p['uuid']))

# Serialize in UTF-8
pilotData = data2post(p).utf8()

if(verb>0): print(pilotData) # UTF-8
if(verb>1): logger.info('pilot data: %s' % pilotData)

# !if in test mode simply bail!
if(tst): exit(0)

################ CONTACT SERVER TO REGISTER THE PILOT ##################
fullurl	= server+"pilots/addpilot"
response = communicate(fullurl, pilotData) # will croak if unsuccessful

logger.info("contact with server established")

data = rdec(response) # .read().decode('utf-8')
if(verb>0): print(data)
if(verb>1): logger.info('server response: %s' % data)


try:
    msg		= json.loads(data)
    p['status']	= msg['status']
    p['state']	= msg['state']
except:
    logger.error('exiting, failed to parse the server message: %s' % data)
    exit(1)

if(p['status']=='FAIL'):
    error = ''
    try:
        error	= msg['error']
        logger.error('exiting, received FAIL status from server, error:%s' % error)
    except:
        logger.error('exiting, received FAIL status from server, no error returned')
    exit(1)
    
    


cnt = p.cycles
url	= "pilots/request/?uuid=%s" % p['uuid']
fullurl	= server+url
while(cnt>0):
    print(cnt)
    response = communicate(fullurl)
    data = rdec(response) # .read()
    print('-->',data)
    cnt-=1
    if(cnt==0): break
    time.sleep(10)

logger.info('exiting normally')
exit(0)



# headers		= response.info()
# data		= response.read()

# response_url	= response.geturl()
# response_date	= headers['date']
# response = urllib.request.urlopen(fullurl)

# try:
#     response = urllib.request.urlopen(fullurl, pilotData)
# except URLError:
#     logger.error('when contacting the server at %s' % fullurl)
#     exit(1)
    

