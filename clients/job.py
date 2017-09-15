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

from serverAPI import serverAPI
from clientenv import clientenv


#########################################################
settings.configure(USE_TZ = True)

user		= os.environ['USER']
Usage		= '''Usage:

For command line options run the pilot with "--help" option.

* Bulk injection *

Option "-j" allows to inject a collection of jobs based on
the contents of a JSON file. See the "examples" directory
for a sample.

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
class Job(dict):
    def __init__(self, name='',
                 priority=0,
                 jobtype='default',
                 payload='/bin/true',
                 env='',
                 state='defined'):
        
        self['name']	= name
        self['user']	= user
        self['uuid']	= uuid.uuid1()
        self['jobtype']	= jobtype
        self['payload']	= payload
        self['env']	= env
        self['priority']= priority
        self['state']	= state
        self['subhost']	= socket.gethostname() # submission host
        self['ts']	= str(timezone.now()) # see TZ note on top

#-------------------------
envDict = clientenv(outputDict=True) # Will need ('server', 'verb'):

parser = argparse.ArgumentParser()

parser.add_argument("-U", "--usage",	action='store_true',	help="print usage notes and exit")
parser.add_argument("-a", "--adjust",	action='store_true',	help="enables state/priority adjustments. Needs uuid.")
parser.add_argument("-d", "--delete",	action='store_true',	help="deletes a job. Needs uuid.")
parser.add_argument("-t", "--test",	action='store_true',	help="when set, do not contact the server")
parser.add_argument("-S", "--server",	type=str,
                    help="server URL: defaults to $P3S_SERVER or if unset to http://localhost:8000/",
                    default=envDict['server'])

parser.add_argument("-s", "--state",	type=str,	help="job state, used with *adjust* and *purge* options",
                    default='')

parser.add_argument("-p", "--priority",	type=int,	help="sets the job priority, needs *adjust* option",
	            default=0)

parser.add_argument("-N", "--number",	type=int,	help="creates N replicas of same job",
	            default=1)


parser.add_argument("-P", "--purge",	type=str,	help="purge jobs older than YY:DD:HH:MM:SS, based on ts in the T argument",
	            default='')

parser.add_argument("-T", "--timestamp",type=str,	help="type of timestamp for deletion", default='defined',
                    choices=['ts_def','ts_sta','ts_sto'])

parser.add_argument("-u", "--uuid",	type=str,		help="uuid of the job to be adjusted",
                    default='')

parser.add_argument("-i", "--id",	type=str,	default='',
                    help="id of the job to be adjusted (pk)")

parser.add_argument("-v", "--verbosity",	type=int, default=envDict['verb'], choices=[0, 1, 2],
                    help="set output verbosity")

parser.add_argument("-j", "--json_in",	type=str,	default='',
                    help="file from which to read job templates (must be a list)")

########################### Parse all arguments #########################
args = parser.parse_args()

usage	= args.usage

server	= args.server
state	= args.state
priority= args.priority
purge	= args.purge
timestamp= args.timestamp
j_uuid	= args.uuid
j_id	= args.id
verb	= args.verbosity
tst	= args.test
adj	= args.adjust
delete	= args.delete
json_in	= args.json_in
Njobs	= args.number

# prepare a list which may be used in a variety of operations,
# contents will vary depending on context
jobList = []

###################### USAGE REQUESTED? ################################
if(usage):
    print(Usage)
    exit(0)

### p3s interface defined here
API  = serverAPI(server=server)

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

########################### JOB PURGE  #################################
# 
if(purge!=''):
# Functionality being moved elsewhere
#    resp = API.post2server('logic', 'purge', dict(interval=purge, timestamp=timestamp, state=state, what="job"))
#    if(verb>0): print(resp)
    exit(0)

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
    data = None
    try:
        with open(json_in) as data_file:    
            data = json.load(data_file)
    except:
        if(verb>0): print('Failed to parse JSON')
        exit(-3)

    for jj in data:
        for jN in range(Njobs):
            j = Job()
            for k in jj.keys():
                if isinstance(jj[k],dict):
                    j[k] = json.dumps(jj[k])
                else:
                    j[k] = jj[k]
            jobList.append(j)
    if(verb>0): print("Number of jobs to be submitted: %s" % len(jobList))

    # Contact the server, register the job(s)
    for j in jobList:
        if(verb>1): print(j)
        if(tst): continue # just testing
        resp = API.post2server('job', 'add', j)
        if(verb>0): print(resp)


###################### GRAND FINALE ####################################
exit(0)
########################################################################
