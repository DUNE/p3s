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

from serverAPI import serverAPI
from clientenv import clientenv

#########################################################
settings.configure(USE_TZ = True) # see the above note on TZ

host		= socket.gethostname()
logdefault	= '/tmp/p3s/'
Usage		= '''Usage:

For command line options run the injector with "--help" option.

'''
######################### THE DATASET CLASS #############################
class Dataset(dict):
    def __init__(self, wf='', name=''):
        self['uuid']	= uuid.uuid1()
        self['name']	= name
        self['wf']	= wf
        
#########################################################################
envDict = clientenv(outputDict=True) # Will need ('server', 'verb'):

parser = argparse.ArgumentParser()

parser.add_argument("-S", "--server",	type=str,	default='http://localhost:8000/',
                    help="the server address, defaults to http://localhost:8000/")

parser.add_argument("-c", "--cycles",	type=int,	default=1,
                    help="how many cycles (with period in seconds) to stay alive")

parser.add_argument("-p", "--period",	type=int,	default=5,
                    help="period of the pilot cycle, in seconds")


parser.add_argument("-v", "--verbosity",	type=int, default=envDict['verb'], choices=[0, 1, 2],
                    help="set output verbosity")

parser.add_argument("-t", "--test",	action='store_true',	help="print parameters and exit")

# --
parser.add_argument("-f", "--filename",	type=str,	default='', help="file to watch")
parser.add_argument("-d", "--datadir",	type=str,	default='/tmp', help="directory to watch")
########################### Parse all arguments #########################
args = parser.parse_args()

# strings
server	= args.server
cycles	= args.cycles
period	= args.period
test	= args.test

filename= args.filename
datadir = args.datadir


# misc
verb	= args.verbosity

# scheduling
period	= args.period
cycles	= args.cycles
verb	= args.verbosity

# testing (pre-emptive exit with print)
tst	= args.test


if(tst):
    print('server:',server,'cycles:',cycles)




API = serverAPI(server=server)


logdir = '/tmp' # FIXME
################### BEGIN: PREPARE LOGGER ##############################
# Check if we have a log directory, example: /tmp/p3s/. Create if not
if(not os.path.exists(logdir)):
    try:
        os.makedirs(logdir)
    except:
        exit(-1) # we can't log it

logfilename = logdir+'/injector.log'

if(verb>0): print("Logfile: %s" % logfilename)

logger = logging.getLogger('injector')
logger.setLevel(logging.DEBUG)
logfile = logging.FileHandler(logfilename)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logfile.setFormatter(formatter)

logger.addHandler(logfile)
logger.info('START injector on host %s, talking to server %s with period %s and %s cycles' %
            (host, server, period, cycles))

API.setLogger(logger)
API.setVerbosity(verb)

if(filename==''): exit(-1)

fileinfo =  '{"NOOP1:filter":{"dirpath":"'+datadir+'","name":"'+filename+'"}}'
jobinfo  = ''

name=add
description='test'
state='defined'

while(cycles>0):
    if(os.path.isfile(datadir+'/'+filename)):
        resp = API.registerWorkflow(add, name, state, fileinfo, jobinfo, description)
        print(resp)
    cycles-=1
    if(cycles==0): # EXHAUSTED ATTEMPTS TO FIND A FILE
        break
    time.sleep(period)

exit(0)

