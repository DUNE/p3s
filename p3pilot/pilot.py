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
def logfail(msg, logger):
    error = ''
    try:
        error	= msg['error'] # if the server told us what the error was, log it
        logger.error('exiting, received FAIL status from server, error:%s' % error)
    except:
        logger.error('exiting, received FAIL status from server, no error returned')
    exit(1)
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

################# THE PILOT CLASS #######################
class Pilot(dict):
    def __init__(self, cycles=1, period=5):
        self['state']	= 'active' # start as active
        self['status']	= '' # status of server comms
        self['host']	= socket.gethostname()
        self['site']	= 'default' # FIXME - will need to get from env
        self['ts']	= str(timezone.now())
        self['uuid']	= uuid.uuid1()
        self.cycles	= cycles
        self.period	= period
#########################################################

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

parser.add_argument("-c", "--cycles",
                    type=int,
                    default=1,
                    help="how many cycles (with period in seconds) to stay alive")

parser.add_argument("-p", "--period",
                    type=int,
                    default=5,
                    help="period of the pilot cycle, in seconds")



########################### Parse all arguments #########################
args = parser.parse_args()

# strings
server	= args.server
url	= args.url
workdir = args.workdir

# misc
verb	= args.verbosity

# scheduling
period	= args.period
cycles	= args.cycles

# testing (pre-emptive exit with print)
tst	= args.test


##################### CREATE A PILOT ###################################
# NB. Need uuid for the logfile etc, so do it now
p = Pilot(cycles=cycles, period=period)

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

logger.info('starting pilot %s on host %s with period %s and %s cycles' % (str(p['uuid']), p['host'], period, cycles))

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

msg = {}
try:
    msg		= json.loads(data)
    p['status']	= msg['status']
    p['state']	= msg['state']
except:
    logger.error('exiting, failed to parse the server message: %s' % data)
    exit(1)

# By now the pilot MUST have some sort of status set by the server's message
if(p['status']=='FAIL'): logfail(msg, logger)

# if(p['status']=='FAIL'):
#     error = ''
#     try:
#         error	= msg['error'] # if the server told us what the error was, log it
#         logger.error('exiting, received FAIL status from server, error:%s' % error)
#     except:
#         logger.error('exiting, received FAIL status from server, no error returned')
#     exit(1)
    
################ REGISTERED, ASK FOR JOB DISPATCH ######################
url	= "pilots/request/?uuid=%s" % p['uuid']
fullurl	= server+url

# Lifecycle
cnt = p.cycles
while(cnt>0):
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
    

