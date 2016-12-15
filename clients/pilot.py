#!/usr/bin/env python3
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
import subprocess

# Django
from django.conf	import settings
from django.utils	import timezone

# HTTP comms
import urllib
from urllib		import request
from urllib		import error
from urllib		import parse
from urllib.error	import URLError

# local import, requires PYTHONPATH to be set
from comms import data2post

#########################################################
settings.configure(USE_TZ = True) # see the above note on TZ

logdefault	= '/tmp/p3s/pilots'

Usage		= '''Usage:

For command line options run the pilot with "--help" option.

* Error Codes *

NB. Positive error codes describe errors in communication
with the server, negative codes correspond to errors
which are local to the pilot, such as problematic
input and local file system problem.

 3	error parsing the server message
 2	FAIL status received from server
 1	URL Error
 0	normal completion
-1	problem in creation of log file or its directory
-2	pilot ID missing in operation that needs it

* Pilot States
active		registered on the server, no attempt at brokerage yet
no jobs		no jobs matched this pilot
dispatched	got a job and preparing its execution
running		running the payload job
finished	job has completed
stopped		stopped after exhausting all brokerage attempts.


'''

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
    exit(2)
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

########################### THE PILOT CLASS #############################
class Pilot(dict):
    def __init__(self, cycles=1, period=5):
        self['state']	= 'active' # start as active
        self['status']	= '' # status of server comms
        self['host']	= socket.gethostname()
        self['site']	= 'default' # FIXME - will need to get from env
        self['ts']	= str(timezone.now())
        self['uuid']	= uuid.uuid1()
        self['event']	= '' # what just happned in the pilot
        self.cycles	= cycles
        self.period	= period
        self.job	= '' # job to be yet received
        
#########################################################################

parser = argparse.ArgumentParser()

parser.add_argument("-S", "--server",	type=str,	default='http://localhost:8000/',
                    help="the server address, defaults to http://localhost:8000/")

parser.add_argument("-U", "--url",	type=str,	default='',
                    help="url of the query to be added, defaults to empty string")

parser.add_argument("-g", "--usage",	action='store_true',
                    help="print usage notes and exit")

parser.add_argument("-l", "--logdir",	type=str,	default=logdefault,
                    help="(defaults to "+logdefault+") the path for all pilots keep their logs etc")

parser.add_argument("-t", "--test",	action='store_true',
                    help="when set, forms a request but does not contact the server")

parser.add_argument("-v", "--verbosity",	type=int,
                    default=0, choices=[0, 1, 2],
                    help="increase output verbosity")

parser.add_argument("-c", "--cycles",	type=int,	default=1,
                    help="how many cycles (with period in seconds) to stay alive")

parser.add_argument("-p", "--period",	type=int,	default=5,
                    help="period of the pilot cycle, in seconds")

parser.add_argument("-d", "--delete",	action='store_true',
                    help="deletes a pilot (for dev purposes). Needs uuid.")

parser.add_argument("-u", "--uuid",	type=str,	default='',
                    help="uuid of the pilot to be modified")

########################### Parse all arguments #########################
args = parser.parse_args()

# strings
server	= args.server
url	= args.url
logdir	= args.logdir

# misc
verb	= args.verbosity
delete	= args.delete
p_uuid	= args.uuid
usage	= args.usage

# scheduling
period	= args.period
cycles	= args.cycles

# testing (pre-emptive exit with print)
tst	= args.test

## This will eventually need to be factored out into a proper module ###
reportURL	= server+'pilots/report'
registerURL	= server+'pilots/register'
deleteallURL	= server+'pilots/deleteall'
deleteURL	= server+'pilots/delete'

###################### USAGE REQUESTED? ################################
if(usage):
    print(Usage)
    exit(0)

###################### PILOT DELETE ####################################
# Check if it was a deletion request
if(delete):
    response = None
    if(p_uuid==''): exit(-2) # check if we have the key

    # DELETE ALL!!!DANGEROUS!!!TO BE REMOVED IN PROD, do not document "ALL"
    if(p_uuid=='ALL'):
        response	= communicate(deleteallURL)
        data		= response.read()
        if(verb >0): print (data)
        exit(0)

    pilotList = []    # Normal delete, by key(s)
    if ',' in p_uuid: # assume we have a CSV list
        pilotList = p_uuid.split(',')
    else:
        pilotList.append(p_uuid)

    for pid in pilotList:
        delData		= data2post(dict(uuid=pid)).utf8()
        response	= communicate(deleteURL, delData)
    
        if(verb >0):
            data = response.read()
            print (data)

    exit(0)

##################### CREATE A PILOT ###################################
# NB. Need uuid for the logfile etc, so do it now
p = Pilot(cycles=cycles, period=period)

################### BEGIN: PREPARE LOGGER ##############################
# Check if we have a log directory, example: /tmp/p3s/pilots

if(not os.path.exists(logdir)):
    try:
        os.makedirs(logdir)
    except:
        exit(-1) # we can't log it

logfilename = logdir+'/'+str(p['uuid'])+'.log'

if(verb>0): print("Logfile: %s" % logfilename)

logger = logging.getLogger('p3pilot')
logger.setLevel(logging.DEBUG)
logfile = logging.FileHandler(logfilename)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logfile.setFormatter(formatter)

logger.addHandler(logfile)
##################### END: PREPARE LOGGER ##############################

logger.info('START %s on host %s, talking to server %s with period %s and %s cycles' % (str(p['uuid']), p['host'], server, period, cycles))

# Serialize in UTF-8
pilotData = data2post(p).utf8()

if(verb>1): print(pilotData) # UTF-8
if(verb>1): logger.info('pilot data: %s' % pilotData)

# !if in test mode simply bail!
if(tst): exit(0)

################ CONTACT SERVER TO REGISTER THE PILOT ##################
response = communicate(registerURL, pilotData) # will croak if unsuccessful

logger.info("contact with server established")

data = rdec(response)
if(verb>1): print('REGISTER: server response: %s' % data)
if(verb>1): logger.info('REGISTER: server response: %s' % data)

msg = {}
try:
    msg		= json.loads(data)
    p['status']	= msg['status']
    p['state']	= msg['state']
except:
    logger.error('exiting, failed to parse the server message: %s' % data)
    exit(3)

# By now the pilot MUST have some sort of status set by the server's message
if(p['status']=='FAIL'): logfail(msg, logger)



#########################################################################
################ REGISTERED, ASK FOR JOB DISPATCH #######################
#########################################################################

jobcount=0
url	= "pilots/request/?uuid=%s" % p['uuid']
jobRequestURL	= server+url

cnt = p.cycles # Lifecycle
####################### MAIN LOOP #######################################
while(cnt>0):     # "Poll the server" loop.

    if(verb>1): print('Attempts left: %s' % str(cnt))
    if(verb>1): logger.info('PILOT: brokering attempts left: %s' % str(cnt))

    response	= communicate(jobRequestURL)
    data	= rdec(response)

    if(verb>1): logger.info('BROKER: server response: %s' % data)
    if(verb>1): print('BROKER: server response: %s' % data)

    msg = {} # Message from the server
    
    try:
        msg = json.loads(data)
        p['status'], p['state']	= msg['status'], msg['state']
    except:
        logger.error('exiting, failed to parse the server message: %s' % data)
        exit(3)

    # Failure reported from brokerage on the server, will log and exit
    if(p['status']=='FAIL'): logfail(msg, logger)

    if(p['state']=='no jobs'): # didn't get a job, skip the cycle.
        logger.info("No jobs on the server")
        cnt-=1
        if(cnt==0): # EXHAUSTED ATTEMPTS TO GET A JOB
            break
        time.sleep(period)
        continue # NEXT ITERATION of "Poll the server" loop.
    ###################### GOT A JOB TO DO ###############################
    payload = ''
    if(p['state']=='dispatched'): # means pilot was matched with a job
        try:
            p['job']	= msg['job'] # uuid of the job
            payload	= msg['payload']
        except:
            logger.error('exiting, failed to parse the server message: %s' % data)
            exit(3)

        logger.info('JOB received: %s %s' % (p['job'], payload))
    

    p['state']='running'
    p['event']='jobstart'
    pilotData = data2post(p).utf8() # Serialize in UTF-8
    response = communicate(reportURL, pilotData) # will croak if unsuccessful

    logger.info("contact with server established")
    logger.info('JOB starting: %s' %  p['job'])

    # EXECUTION
    try:
        x=subprocess.run([payload], stdout=subprocess.PIPE)
        if(verb>1): logger.info('job output: %s' % x.stdout.decode("utf-8"))
        p['state']	='finished'
        p['event']	='jobstop'
        pilotData	= data2post(p).utf8()
        response	= communicate(reportURL, pilotData) # will croak if unsuccessful

        logger.info("contact with server established")
        logger.info('JOB finished: %s' %  p['job'])
    except:
        p['state']	='exception'
        p['event']	='exception'
        pilotData	= data2post(p).utf8()
        response = communicate(reportURL, pilotData) # will croak if unsuccessful

    p['state']	='active'
    #    p['event']	='jobstop'
    pilotData	= data2post(p).utf8()
    response	= communicate(reportURL, pilotData) # will croak if unsuccessful
    
    jobcount+=1
    cnt-=1 # proceed to next cycle
    
    if(cnt==0): break # don't wait another sleep cycle
    time.sleep(period)
# ------


######################## FINISHING UP ##################################

p['state']	= 'stopped'
pilotData	= data2post(p).utf8()
print('!!!!', pilotData)
response	= communicate(reportURL, pilotData) # will croak if unsuccessful

logger.info('STOP %s, host %s, cycles*period: %s*%s, jobs done %s' % (str(p['uuid']), p['host'], cycles, period, str(jobcount)))
exit(0)

######################## DUSTY ATTIC ###################################
# headers	= response.info()
# data		= response.read()

# response_url	= response.geturl()
# response_date	= headers['date']


