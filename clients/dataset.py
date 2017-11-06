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
from serverAPI		import serverAPI
from clientenv		import clientenv

from clientUtils	import takeJson
from Job		import Job

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

* Registering data type *
-R option; also requires JSON (-j) option, needs to contain name, ext, comment.
"Ext" (extension) contains the dot e.g. ".txt"



* Misc Notes *
The file name in logdir will be 'injector.log'
If P3S_SERVER is unset the default will be http://localhost:8000/
Verbosity will default to $P3S_VERBOSITY if not set explicitly

'''
######################### THE DATASET CLASS #############################
# (Temporarily) deprecated
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
#exit(0)

parser = argparse.ArgumentParser()


parser.add_argument("-U", "--usage",	help="print usage notes and exit", action='store_true')
parser.add_argument("-t", "--test",	help="print, do not contact the server", action='store_true')


parser.add_argument("-S", "--server",	type=str, help="the server address, defaults to $P3S_SERVER",	default=envDict['server'])
parser.add_argument("-J", "--JSON",	type=str, help="JSON template of the job to be generated",	default='')
parser.add_argument("-f", "--filename",	type=str, help="filename to plug into the template",		default='')
parser.add_argument("-j", "--json",	type=str, help="JSON description of the data to be manipulated",default='')
parser.add_argument("-a", "--adjust",	type=str, help="the uuid to be adjusted, needs JSON input",	default='')
parser.add_argument("-D", "--deltype",	type=str, help="data type to be deleted from the server",	default='')
parser.add_argument("-l", "--logdir",	type=str, help="Log directory (defaults to "+logdefault+").",	default=logdefault)
parser.add_argument("-u", "--uuid",	type=str, help="uuid of the data to be modified or deleted",	default='')
parser.add_argument("-i", "--inputdir",	type=str, help="input directory",				default='')


parser.add_argument("-r", "--registerdata",	  help="register dataset",				action='store_true')
parser.add_argument("-g", "--generateJob",	  help="generate job (needs -J)",			action='store_true')
parser.add_argument("-R", "--registertype",	  help="register data type (see Usage for details)",	action='store_true')
parser.add_argument("-d", "--delete",		  help="deletes a record from the DB. Needs uuid.",	action='store_true')

parser.add_argument("-A", "--allow",		  help="allow job generation on data already used",	action='store_true')

parser.add_argument("-N", "--noreg",		  help="no registration of input data",			action='store_true')


parser.add_argument("-v", "--verbosity", type=int,help="output verbosity (0-4)",choices=[0, 1, 2, 3, 4],default=envDict['verb'])

parser.add_argument("-p", "--period",	type=int, help="polling period, in seconds",			default=5)
parser.add_argument("-c", "--cycles",	type=int, help="number of cycles to stay alive",		default=1)


########################### Parse all arguments #########################
args = parser.parse_args()

# strings
server	= args.server
logdir	= args.logdir
json_in	= args.json
JSON_in	= args.JSON
filename= args.filename
deltype	= args.deltype
dlt	= args.delete
d_uuid	= args.uuid
inputDir= args.inputdir

# misc
verb	= args.verbosity
usage	= args.usage
tst	= args.test
# scheduling
period	= args.period
cycles	= args.cycles


regData	= args.registerdata
regType	= args.registertype
adjust	= args.adjust


allow	= args.allow
noreg	= args.noreg

generateJob = args.generateJob


API = serverAPI(server=server)

###################### USAGE REQUESTED? ################################
if(usage):
    print(Usage)
    exit(0)

################# DATA RECORD DELETE AND EXIT ##########################
if(dlt):
    response = None
    if(d_uuid==''): exit(-2) # check if we have the key

    dList = []    # Normal delete, by key(s)
    if ',' in d_uuid: # assume we have a CSV list
        dList = d_uuid.split(',')
    else:
        dList.append(d_uuid)

    for d_id in dList:
        resp = API.post2server('data', 'delete', dict(uuid=d_id))

        if(verb>0): print (resp)

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
    if(json_in==''): exit(0)
    
    data		= takeJson(json_in, verb)
    data['uuid']	= uuid.uuid1() # note we create a fresh UUID here
    data['dirpath']	= envDict['dirpath']
    
    resp = API.post2server('data', 'register', data)
    print(resp)
    
    exit(0)
        
#########################################################################
if(regType):
    if(json_in==''): exit(0)
    
    data = takeJson(json_in, verb)
    resp = API.post2server('data', 'registertype', data)
    print(resp)
    exit(0)
        
#########################################################################
if(deltype!=''):
    print(dict({'name':deltype}))
    resp = API.post2server('data', 'deletetype', dict({'name':deltype}))
    print(resp)
    exit(0)
        
#########################################################################
if(adjust!=''):
    if(json_in==''): exit(0)
    
    data	= takeJson(json_in, verb)
    data['uuid']= adjust
    print(data)

    resp = API.post2server('data', 'adjust', data)
    print(resp)

    exit(0)
        
#########################################################################
if(generateJob): #
    if(JSON_in==''): exit(-1)

    data	= takeJson(JSON_in, verb)

    inputFile = ''

    try:
        inputFile = os.environ['P3S_INPUT_FILE']
    except:
        pass

    if(filename!=''): inputFile = filename


    if (not allow):
        resp	= API.get2server('data', 'getdata', filename)
        result	= takeJson(resp, verb)

        if(len(result)!=0):
            print('File '+filename+' already registered')
            exit(0)

    theDir = ''
    try:
        theDir=envDict['dirpath']+'/input'
    except:
        pass
    

    if(inputDir!=''):
        theDir = inputDir

    for job in data:
        job['env']['P3S_INPUT_FILE'] = inputFile

        j = Job(job)

        if(tst):
            print('testing... job submissio skipped')
        else:
            j_uuid = API.post2server('job', 'add', j)
            print('job uuid:', j_uuid)
    
    if(noreg):
        if(verb>0): print('SKIPPING REG')
        exit(0)

    dataSet		= {}
    dataSet['name']	= inputFile
    dataSet['state']	= 'defined'

    dataSet['targetuuid']	= j_uuid
    dataSet['uuid']		= uuid.uuid1() # note we create a fresh UUID here
    dataSet['dirpath']	= theDir

    print(dataSet)
    
    resp = API.post2server('data', 'register', dataSet)
    print(resp)
    delay = 5
    time.sleep(delay/1000.0) # prevent self-inflicted DOS
