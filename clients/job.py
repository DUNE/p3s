#!/usr/bin/env python3.5
#########################################################
# TZ-awarewness:					#
# The following is not TZ-aware: datetime.datetime.now()#
# so we are using timzone.now() where needed		#
#########################################################

from django.conf import settings
from django.utils import timezone

import argparse
import uuid
import socket
import time
import datetime
import json
import os

from serverAPI		import serverAPI
from clientenv		import clientenv

from clientUtils	import takeJson
from Job		import Job

#########################################################
settings.configure(USE_TZ = True)

user		= os.environ['USER']
Usage		= '''Usage:

For command line options run the pilot with "--help" option.

* Bulk injection *

Option "-j" allows to inject a collection of jobs based on
the contents of a JSON file (formatted as a list). See the
"examples" directory for a sample. In addition, if
a single job is specified in the list, the user can create
replicas of this job in the system with the "-N" option.
In either case, the jobs are registered at the server
with consecutive HTTP messages. There is a delay
between the messages which aims to avoid a DOS situation.

* "Test Wrapper"

It may be useful to test the job on an interactive node
before sending it to the server for bulk execution. If
this is the case, the "testwrapper.py" script should
be used. It provides correct setting of the environment
for the job before its execution commences.


* Changing attributes of a job *

Option "-a" allows to change the job state or priority -
with options "-s" and "-p" respectively. Can be used
concurrently.

* Relation to workflows *

Jobs can be standalone i.e. not a part of any workflow,
or can belong to one.

* Relation to data

If a structured definition of input and/or output data is
needed, a job must be defined as a part of a workflow. Otherwise
it's up to the job itself to find its inputs and define its
outputs


'''

#-------------------------
#-------------------------
envDict = clientenv(outputDict=True) # Will need ('server', 'verb'):

parser = argparse.ArgumentParser()

parser.add_argument("-U", "--usage",	action='store_true',	help="print usage notes and exit")

parser.add_argument("-a", "--adjust",	action='store_true',	help="enables state/priority adjustments. Needs these parameters plus uuid.")

parser.add_argument("-d", "--delete",	action='store_true',	help="deletes the DB record job regardless of its state. Needs uuid or id (pk). *SHOULD BE USED WITH CARE*")

parser.add_argument("-t", "--test",	action='store_true',	help="do not contact the server - testing the client")

parser.add_argument("-l", "--ltype",	action='store_true',	help="list or set job types and limits")

parser.add_argument("-L", "--limit",	type=int,	help="sets the job type limit",	default=-1)

parser.add_argument("-T", "--jobtype",	type=str,	help="job type to retrieve or adjust",	default='')

parser.add_argument("-S", "--server",	type=str,
                    help="server URL: defaults to $P3S_SERVER or if unset to http://localhost:8000/",
                    default=envDict['server'])

parser.add_argument("-s", "--state",	type=str,	help="job state - for  *adjust* and *purge* options",	default='')

parser.add_argument("-P", "--priority",	type=int,	help="sets the job priority, needs *adjust* option",	default=0)

parser.add_argument("-N", "--number",	type=int,	help="creates N job replicas (delay is configurable)",	default=1)

parser.add_argument("-D", "--delay",	type=int,	help="delay in serial submission of replicas, ms",	default=1000)

parser.add_argument("-u", "--uuid",	type=str,	help="uuid of the job to be manipulated",		default='')

parser.add_argument("-p", "--pk",	type=str,	help="pk of the job to be manipulated",			default='')


parser.add_argument("-j", "--json_in",	type=str,	help="JSON file with job templates (list)",		default='')

parser.add_argument("-f", "--filename",	type=str,	help="value with which to override P3S_INPUT_FILE in the job template",
		    default='')

parser.add_argument("-v", "--verbosity",type=int,	help="set output verbosity", default=envDict['verb'], choices=[0, 1, 2])

parser.add_argument("-V", "--version",	type=str,	help="value with which to override DUNETPCVER in the job template",
		    default='')
########################### Parse all arguments #########################
args = parser.parse_args()

usage	= args.usage

server	= args.server
state	= args.state
priority= args.priority
j_uuid	= args.uuid
j_id	= args.pk
verb	= args.verbosity
tst	= args.test
adj	= args.adjust
delete	= args.delete
json_in	= args.json_in
Njobs	= args.number
delay	= args.delay
version	= args.version

ltype	= args.ltype
limit	= args.limit
jobtype	= args.jobtype


filename= args.filename

# save for later:
# inputDir= args.inputdir
# timestamp= args.timestamp


# prepare a list which may be used in a variety of operations,
# contents will vary depending on context
jobList = []

###################### USAGE REQUESTED? ################################
if(usage):
    print(Usage)
    exit(0)

### p3s interface defined here
API  = serverAPI(server=server, verb=verb)



################# JOB TYPES: DUMP AND SET LIMITS   #####################

if(ltype):
    if(limit>=0):
        d = {}
        d["name"]	= jobtype
        d["limit"]	= limit
        resp = API.post2server('job', 'limit', d)
        if(verb>0): print(resp)
        exit(0)

        
    resp = API.get2server('job', 'ltype', jobtype)
    if(verb>0): print(resp)

    exit(0)
    

########################## UPDATE/ADJUSTMENT ###########################
# Check if an adjustment of an existing job is requested, and send a
# request to the server to do so. Can adjust priority, state.

if(adj):
    response = None
    if(j_uuid==''):			exit(-1) # check if we have the key
    if(priority==-1 and state==''):	exit(-1) # nothing to adjust

    if ',' in j_uuid:
        jobList = j_uuid.split(',')
    else:
        jobList.append(j_uuid)
        
    for j in jobList:
        a = dict(uuid=j) # create a dict to be serialized and sent to the server
        if(priority>0):	a['priority']	= str(priority)
        if(state!=''):	a['state']	= state
        resp = API.post2server('job', 'adjust', a)
        if(verb>0): print(resp)

    exit(0) # done with update/adjust

########################### JOB DELETE #################################
# Check if it was a deletion request
if(delete):
    response = None
    if(j_uuid=='' and j_id==''): exit(-1) # check if we have the key

    
    if(j_uuid!=''): # delete by UUIDs
        if ',' in j_uuid: # assume we have a CSV list
            jobList = j_uuid.split(',')
        else:
            jobList.append(j_uuid)

        for j in jobList:
            resp = API.post2server('job', 'delete', dict(uuid=j))
            if(verb>0): print(resp)
        exit(0)
        
    
    if(j_id!=''): # delete by ID (PK)
        if ',' in j_id: # assume we have a CSV list
            jobList = j_id.split(',')
        else:
            jobList.append(j_id)

        for j in jobList:
            resp = API.post2server('job', 'delete', dict(pk=j))
            if(verb>0): print(resp)
        exit(0)


    exit(0)

########################################################################
# Catch-all for uuid: should have handled uuid-specific requests already,
# if we are here it's an error
if(j_uuid!=''): exit(-1)

########################## REGISTRATION ################################
# Check if we want to read a json file with job templates and register

if(json_in!=''):
    inputFile	= ''

    try:
        inputFile = os.environ['P3S_INPUT_FILE']
    except:
        pass

    try:
        version = os.environ['DUNETPCVER']
    except:
        pass

    if(filename!=''):	inputFile = filename


    inputFiles = inputFile.split(',')
    
    # multiple files override the number of jobs to be auto-generated
    # N.B. this feature may be suspended if it interferes with testing
    # with a subset of all files...
    
    if(len(inputFiles) !=1): Njobs=len(inputFiles)
    
    data = takeJson(json_in, verb)

    for jj in data:
        for jN in range(Njobs):
            pld=jj['payload']
            isGood = os.access(pld, os.R_OK) and os.access(pld, os.X_OK)
            
            if(not isGood):
                print('FAIL: The payload is not readable or executable for members of your group, plese check the path.')
                print('Also make sure any I/O files you specify in the "env" attribute are READ/WRITE accessible to members of your group.')
                exit(-1)
            if(inputFile!=''):
                if(len(inputFiles)==1):
                    jj['env']['P3S_INPUT_FILE'] = inputFiles[0]
                    if(verb>1): print('Overriding input file with: '+inputFiles[0])
                else:
                    jj['env']['P3S_INPUT_FILE'] = inputFiles[jN-1]
                    if(verb>1): print('Overriding input file with: '+inputFiles[jN-1])
            if(version!=''):
                jj['env']['DUNETPCVER'] = version
                if(verb>1): print('Overriding DUNETPCVER with: '+version)
            
            jobList.append(Job(jj))
    
    if(verb>0): print("Number of jobs to be submitted: %s" % len(jobList))

    for j in jobList:# Contact the server, register the job(s)
        
        if(verb>1): print(j)
        
        if(tst): continue # just testing
        
        resp = API.post2server('job', 'add', j)
        
        if(verb>0): print(resp)
        
        time.sleep(delay/1000.0) # delay to prevent a self-inflicted DOS attack


###################### GRAND FINALE ####################################
exit(0)
########################################################################
# parser.add_argument("-i", "--inputdir",	type=str,	help="input directory *FUTURE DEVELOPMENT",		default='')
# parser.add_argument("-k", "--kill",	action='store_true',	help="kills a running job. Needs uuid or id (pk). *FUTURE DEVELOPMENT*")

