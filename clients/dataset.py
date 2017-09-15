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
import os

# Django
from django.conf	import settings
from django.utils	import timezone

# local import
from serverAPI import serverAPI
from clientenv import clientenv
#########################################################
settings.configure(USE_TZ = True) # see the above note on TZ

host		= socket.gethostname()
user		= os.environ['USER']
logdefault	= '/tmp/'+user+'/p3s/data/'
datadir		= '/home/maxim/p3sdata'
Usage		= '''Usage:

* Command line *
For command line options run the script with "--help" option.

* Registering data *
JSON string submitted on the command line needs to be enclosed in single
quotes and is ecpeted to have:
- name
- state
- datatype
- wf
- wfuuid

'''
######################### THE DATASET CLASS #############################
class Dataset(dict):
    def __init__(self, name='', state='', comment='', datatype='', wf='', wfuuid=''):
        self['uuid']	= uuid.uuid1()
        self['name']	= name
        self['state']	= state
        self['comment']	= comment
        self['datatype']= datatype
        self['wf']	= wf
        self['wfuuid']	= wfuuid
        
#########################################################################
envDict = clientenv(outputDict=True)


parser = argparse.ArgumentParser()

parser.add_argument("-S", "--server",	type=str,	default=envDict['server'],
                    help="the server address, defaults to $P3S_SERVER or if unset to http://localhost:8000/")

parser.add_argument("-j", "--json",	type=str,	default='',
                    help="json description of the data to be sent")

parser.add_argument("-D", "--deltype",	type=str,	default='',
                    help="the name of the data type to be deleted from the server")

parser.add_argument("-U", "--usage",	action='store_true',
                    help="print usage notes and exit")

parser.add_argument("-l", "--logdir",	type=str,	default=logdefault,
                    help="Log directory (defaults to "+logdefault+"). The file name in logdir will be 'injector.log'")

parser.add_argument("-r", "--registerdata",	action='store_true',
                    help="register dataset")

parser.add_argument("-a", "--adjust",	action='store_true',
                    help="adjust dataset")

parser.add_argument("-R", "--registertype",	action='store_true',
                    help="register data type: requires JSON (-j) option, needs to present name, ext, comment. Ext (extension) contains the dot.")

parser.add_argument("-v", "--verbosity", type=int,	default=envDict['verb'], choices=[0, 1, 2, 3, 4],
                    help="output verbosity (0-4), will default to $P3S_VERBOSITY if set")

parser.add_argument("-c", "--cycles",	type=int,	default=1,
                    help="how many cycles (with period in seconds) to stay alive")

parser.add_argument("-p", "--period",	type=int,	default=5,
                    help="period of the pilot cycle, in seconds")

########################### Parse all arguments #########################
args = parser.parse_args()

# strings
server	= args.server
logdir	= args.logdir
jtxt	= args.json
deltype	= args.deltype

# misc
verb	= args.verbosity
usage	= args.usage

# scheduling
period	= args.period
cycles	= args.cycles


regData	= args.registerdata
regType	= args.registertype
adjust	= args.adjust

API = serverAPI(server=server)

###################### USAGE REQUESTED? ################################
if(usage):
    print(Usage)
    exit(0)

################### BEGIN: PREPARE LOGGER ##############################
# Check if we have a log directory, example: /tmp/p3s/. Create if not
if(not os.path.exists(logdir)):
    try:
        os.makedirs(logdir)
    except:
        exit(-1) # we can't log it

logfilename = logdir+'/dataset.log'

if(verb>0): print("Logfile: %s" % logfilename)

logger = logging.getLogger('dataset')
logger.setLevel(logging.DEBUG)
logfile = logging.FileHandler(logfilename)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logfile.setFormatter(formatter)

logger.addHandler(logfile)
logger.info('DATASET on host %s, talking to server %s' %
            (host, server))

API.setLogger(logger)
API.setVerbosity(verb)

#########################################################################
if(regData):
    if(jtxt!=''):
        j = json.loads(jtxt)
        d = Dataset(name	=j["name"],
                    state	=j["state"],
                    comment	=j["comment"],
                    datatype	=j["datatype"],
                    wf		=j["wf"],
                    wfuuid	=j["wfuuid"]
        )
    else:
        d = Dataset()

    resp = API.registerData(d)

    exit(0)
        
#########################################################################
if(regType):
    if(jtxt==''): exit(0)
    
    j = json.loads(jtxt)
    resp = API.registerType(j)

    exit(0)
        
#########################################################################
if(deltype!=''):
    
    d = {}
    d['name'] = deltype
    resp = API.deleteType(d)

    exit(0)
        
#########################################################################
if(adjust):
    if(jtxt!=''):
        resp = API.adjData(json.loads(jtxt))
    else:
        exit(-1)


    exit(0)
        
