#!/usr/bin/env python3.5
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
import signal
import shlex

# --- process management... deferred 4.6.2017
# import psutil

# Django
from django.conf	import settings
from django.utils	import timezone

# local import (utils)
from comms	import logfail, logkill
from serverAPI	import serverAPI
from clientenv	import clientenv

#########################################################
#########################################################

settings.configure(USE_TZ = True) # see the above note on TZ

Usage		= '''Usage:

For command line options run the pilot with "--help" option.

* Error Codes *

NB. Positive error codes describe errors in communication
with the server, negative codes correspond to errors
which are local to the pilot, such as problematic
input and local file system problem.

 4	inconsistent server state
 3	error parsing message from the server
 2	FAIL status received from server
 1	URL Error
 0	normal completion
-1	problem in creation of log file or its directory
-2	pilot ID missing in operation that needs it

* Pilot States
active		registered on the server, no attempt at brokerage yet
no jobs		no jobs matched this pilot
dispatched	got a job and preparing its execution (may still fail)
running		running the payload job
finished	job has completed
stopped		stopped after exhausting all brokerage attempts.


'''
from Pilot import Pilot

#########################################################################        
#############################  BEGIN  ###################################

(user, server, verb, site, logdefault, joblogdefault) = clientenv()

parser = argparse.ArgumentParser()

parser.add_argument("-S", "--server",	type=str,	default=server,
                    help="the server address, defaults to $P3S_SERVER or if unset to http://localhost:8000/")

parser.add_argument("-H", "--host",	type=str,	default='',
                    help="the worker node where a pilot may nee adjustments")

parser.add_argument("-s", "--site",	type=str,	default=site,
                    help="site name - pilot parameters will be pulled from the server based on that")

parser.add_argument("-U", "--usage",	action='store_true',
                    help="print usage notes and exit")

parser.add_argument("-l", "--logdir",	type=str,	default=logdefault,
                    help="(defaults to "+logdefault+") the path for all pilots keep their logs")

parser.add_argument("-L", "--joblogdir",type=str,	default=joblogdefault,
                    help="(defaults to "+joblogdefault+") the path for all jobs keep their stdout and stderr")

parser.add_argument("-t", "--test",	action='store_true',
                    help="when set, forms a request but does not contact the server")

parser.add_argument("-v", "--verbosity", type=int,	default=verb, choices=[0, 1, 2, 3, 4],
                    help="output verbosity (0-4), will default to $P3S_VERBOSITY if set")

parser.add_argument("-c", "--cycles",	type=int,	default=1,
                    help="number of job request cycles: 0 means infinite, negative overrides the per-site setting")

parser.add_argument("-p", "--period",	type=int,	default=5,
                    help="period of the job request cycle, in seconds")

parser.add_argument("-b", "--beat",	type=int,	default=2,
                    help="the heartbeat, in seconds")

parser.add_argument("-d", "--delete",	action='store_true',
                    help="deletes a pilot record from the DB. Needs uuid.")

parser.add_argument("-k", "--kill",	action='store_true',
                    help="sets KILL state for a pilot, which is then expected to exit. Needs uuid, or site, or host.")

parser.add_argument("-u", "--uuid",	type=str,	default='',
                    help="uuid of the pilot to be modified")

parser.add_argument("-x", "--execute",	action='store_true',
                    help="force the payloads to run in shell (for experts)")



#########################################################################
########################### Parse all arguments #########################
args = parser.parse_args()

(
    server,		host,		site,		logdir,		joblogdir,
    verb,		dlt,		kill,		p_uuid,
    usage, shell, period, cycles, beat, tst
) = (
    args.server,	args.host,	args.site,	args.logdir,	args.joblogdir,
    args.verbosity,	args.delete,	args.kill,	args.uuid,
    args.usage, args.execute, args.period, args.cycles, args.beat, args.test
)

keepCycles = cycles # will override the site cycles if negative

############################## START ###################################
if(usage):
    print(Usage)
    exit(0)

### p3s interface defined here
API  = serverAPI(server=server)


if(site!='default' and site!='' and not kill): # bootstrap from the server - need server address

    resp = API.get2server('site','getsiteURL', site)
    try:
        siteData = json.loads(resp)
    except:
        if(verb>0): print('Could not load site data')
        exit(4)
        
    if(len(siteData)!=1):
        if(verb>0): print('Multiple sites reported for site name '+ site +'... Inconsitency - Exiting.')
        exit(5)

    s = siteData[0]['fields']
    doubleQ = s['env'].replace("'", "\"")
    (server, env, period, cycles) = (s['server'], json.loads(doubleQ), s['pilotperiod'], s['pilotcycles'])

    if(verb>0): print('keepCycles ', keepCycles, '  Cycles ', cycles)

    if(keepCycles<0):
        cycles=-keepCycles
        if(verb>0): print('Overriding site cycles with:', cycles)
    
    for k in env.keys():
        os.environ[k]=env[k]

if(kill):
    d = None
    if(p_uuid!=''):			d = dict(uuid=p_uuid)
    if(p_uuid=='' and host!=''):	d = dict(host=host)
    if(p_uuid=='' and site!=''):	d = dict(site=site)

    print(d)
    resp = API.post2server('pilot', 'kill', d)
    print(resp)
    exit(0)

#################### PILOT DELETE AND EXIT #############################
# Check if a pilot needs to be deleted from the DB. This is a drastic
# operation and should be reserved for experts.
if(dlt):
    response = None
    if(p_uuid==''): exit(-2) # check if we have the key

    pilotList = []    # Normal delete, by key(s)
    if ',' in p_uuid: # assume we have a CSV list
        pilotList = p_uuid.split(',')
    else:
        pilotList.append(p_uuid)

    for pid in pilotList:
        resp = API.post2server('pilot', 'delete', dict(uuid=p_uuid))

        if(verb>0): print (resp)

    exit(0)

##################### CREATE A PILOT ###################################
# NB. Need uuid for the logfile etc, so do it now
p = Pilot(cycles=cycles, period=period, site=site)

################### BEGIN: PREPARE LOGGER ##############################
# Check if we have a log directory, example: /tmp/p3s/pilots.
# Create if necessary. Do same for job log directory.

if(not os.path.exists(logdir)):
    try:
        os.makedirs(logdir)
    except:
        exit(-1) # we can't log it

if(not os.path.exists(joblogdir)):
    try:
        os.makedirs(joblogdir)
    except:
        exit(-1) # we can't log it

logfilename = logdir+'/'+str(p['uuid'])+'.log' # note it uses the pilot uuid

if(verb>0): print("Logfile: %s" % logfilename)

logger = logging.getLogger('p3pilot')
logger.setLevel(logging.DEBUG)
logfile = logging.FileHandler(logfilename)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logfile.setFormatter(formatter)

logger.addHandler(logfile)

API.setLogger(logger)
API.setVerbosity(verb)

logger.info('START %s as pid %s on host %s, user %s, p3s server %s, period %s, %s cycles, verbosity %s' %
            (str(p['uuid']), p['pid'], p['host'], user, server, period, cycles, verb))

#########################################################################
################ CONTACT SERVER TO REGISTER THE PILOT ##################
resp = API.registerPilot(p)

if(verb>1): print('REGISTER: server response: %s'	% resp)
if(verb>1): logger.info('REGISTER: server response: %s'	% resp)

msg = {} # we expect a message from the server formatted in json
# print(resp)
try:
    msg		= json.loads(resp)
    p['status']	= msg['status']
    p['state']	= msg['state']
except:
    logger.error('exiting, failed to parse the server message at registration: %s' % resp)
    exit(3)

# By now the pilot MUST have some sort of status set by the server's message
if(p['status']=='FAIL'): logfail(msg, logger)

#########################################################################
################ REGISTERED, ASK FOR JOB DISPATCH #######################
cnt		= p.cycles # Number of cycles to go through before exit
p['jobcount']	= 0 # will count how many jobs were eceuted in this pilot
#################### MAIN "POLL FOR JOBS" LOOP ##########################

while(cnt>0 or p.cycles==0):

    if(verb>1): print('Attempts left: %s' % str(cnt))
    if(verb>1): logger.info('PILOT: brokering attempts left: %s' % str(cnt))

    data = API.post2server('pilot', 'jobRequestURL',dict(uuid=p['uuid']))

    if(verb>1): logger.info('BROKER: server response: %s' % data)
    if(verb>1): print('BROKER: server response: %s' % data)

    #--------------------- important
    msg = {} # Message from the server
    
    try:
        msg = json.loads(data)
        p['status'], p['state']	= msg['status'], msg['state']
    except:
        logger.error('exiting, failed to parse the server message at brokerage: %s' % data)
        exit(3)

    # Failure reported from brokerage on the server, will log and exit
    if(p['status']=='FAIL'): logfail(msg, logger)
    
    # KILL requested by the server, will log and exit
    if(p['status']=='KILL'): logkill(logger)

    if(p['state'] in ('no jobs', 'DB lock')): # didn't get a job, skip the cycle.
        logger.info(p['state'])
        cnt-=1 # won't matter if cycles were set to zero for infinite loop
        if(cnt==0): # EXHAUSTED ATTEMPTS TO GET A JOB
            break
        time.sleep(period)
        continue # NEXT ITERATION OF THE MAIN LOOP IF DIDN'T GET A JOB, otherwise - below
    
######################### GOT A JOB TO DO ###############################
    payload	= ''
    env		= {}
    
    if(p['state']=='dispatched'): # means pilot was matched with a job
        try:
            p['job']	= msg['job']	# uuid of the job
            payload	= msg['payload']# executable (e.g. a script)
            
            if(len(msg['env'])):
                try:
                    env = json.loads(msg['env'])
                except:
                    logger.error('failed to parse JSON description of the environment: %s' % msg['env'])
            else:
                env = {}
        except:
            logger.error('exiting, failed to parse the server message at dispatch: %s' % data)
            exit(3)

        logger.info('JOB received: %s %s' % (p['job'], payload))
        logger.info('ENV received: %s' % str(env))
    

    p['state']='running'
    p['event']='jobstart'

    logger.info('JOB to be started: %s' %  p['job'])
    
    resp = API.reportPilot(p)
    if(verb>0): logger.info('Starting job, server response: %s' % resp)

    # ENVIRONMENT
    pilot_env	= os.environ.copy()
    job_env	= {**pilot_env,**env} # merge the original environment and one set in the job description

    # Add the UUIDs of the job and the pilot to the environment (mey be needed for logging etc)
    job_env['P3S_JOB_UUID']	= p['job']
    job_env['P3S_PILOT_UUID']	= str(p['uuid'])

    logger.info('JOB_ENV: %s' % str(job_env))
    
    if 'P3S_EXECMODE' in job_env.keys(): # can be forced by -s
        shell = True
    
    cmd=shlex.split(payload)
    if(shell): cmd=payload
        
    logger.info('CMD: %s' % cmd)
    proc = None

    joboutFilename = joblogdir+'/'+ p['job']+'.out'
    joberrFilename = joblogdir+'/'+ p['job']+'.err'
    
    jobout = open(joboutFilename,'w')
    joberr = open(joberrFilename,'w')

    logger.info('JOB STDOUT: %s' % joboutFilename)
    logger.info('JOB STDERR: %s' % joberrFilename)

    
    # EXECUTION
    try:
        proc = subprocess.Popen(cmd,
                                stdout=jobout, # stdout=subprocess.PIPE,
                                stderr=joberr, # stderr=subprocess.PIPE,
                                env=job_env,
                                shell=shell)
    except:
        joberr.write('nonstarter')
        jobout.close()
        joberr.close()
        
        p['state']='nonstarter'
        data = API.reportPilot(p)
        logger.error("could not start the job, skip")
        continue
            

    jobPID = proc.pid
    errCode = None

    while True:
        msg = {}
        errCode = proc.poll()
        if(verb>3): print('Heartbeat: Job PID:',jobPID, 'errCode:', errCode)
        if errCode is None:
            p['state']='running'
            p['event']='heartbeat'
            p['jpid'] = jobPID
            data = API.reportPilot(p)
            try:
                msg = json.loads(data)
                p['status'], p['state']	= msg['status'], msg['state']
            except:
                logger.error('exiting, failed to parse the server message at report: %s' % data)
                exit(3)

            # Failure reported from brokerage on the server, will log and exit
            if(p['status']=='FAIL'): logfail(msg, logger)
            
            # The server wants to kill the pilot
            if(p['status']=='KILL'):
                os.kill(jobPID, signal.SIGTERM)
                logger.info('received kill request from server')
                exit(0) # FIXME - will make all this more fancy later

            if(verb>2): logger.info('HEARTBEAT, server response: %s' % data)
        else: # see the "pipe" note on the bottom"
            jobout.close()
            joberr.close()
            break

        # continue the process polling loop, sleep a little
        time.sleep(beat)

    # Ended loop, assume job done (FIXME error handling)
    p['state']	= 'finished'
    p['event']	= 'jobstop'
    p['errcode']= errCode
    p['jobcount']  += 1
    p['jpid']	= jobPID
        
    response = API.reportPilot(p)
    logger.info('JOB finished: %s' %  p['job'])


    # declare the 'active' state again
    p['state']	='active'    #    p['event']	='jobstop'
    response = API.reportPilot(p)
    
    cnt-=1 # proceed to next cycle
    
    if(cnt==0): break	# don't wait another sleep cycle
    time.sleep(period)	# wait before the next cycle

######################## FINISHING UP ##################################

p['state']	= 'stopped'
response = API.reportPilot(p)
logger.info('STOP %s, host %s, cycles*period: %s*%s, jobs done %s' %
            (str(p['uuid']), p['host'], cycles, period, str(p['jobcount'])))
if(verb>0): print("Stopped. Processed jobs: %s" % str(p['jobcount']))

exit(0)

######################## FOR LATER   ###################################
#            errCode = proc.poll()
#            psProc = psutil.Process(pid=jobPID)
#            psKids=psProc.children(recursive=True)
#            if(verb>1): print(psKids)
#
# Decomissioned way of starting jobs
# else: # Deprecated...
#     try:
#         x=subprocess.run([payload], stdout=subprocess.PIPE)
#         if(verb>1): logger.info('job output: %s' % x.stdout.decode("utf-8"))
#         p['state']	='finished'
#         p['event']	='jobstop'
#         p['jobcount']  += 1
#         response = API.reportPilot(p)
#         logger.info('JOB finished: %s' %  p['job'])
#     except:
#         p['state']	='exception'
#         p['event']	='exception'
#         response = API.reportPilot(p)
#         logger.info('JOB exception: %s' %  p['job'])


# Handling pipes from the process, now deprecated
# jobout = open(joblogdir+'/'+ p['job']+'.out','w')
# joberr = open(joblogdir+'/'+ p['job']+'.err','w')
# jobout.write((proc.stdout.read().decode('utf-8')))
# joberr.write((proc.stderr.read().decode('utf-8')))
