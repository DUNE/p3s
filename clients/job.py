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

from comms import logfail
from serverAPI import serverAPI

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
parser = argparse.ArgumentParser()

parser.add_argument("-U", "--usage",	action='store_true',	help="print usage notes and exit")
parser.add_argument("-a", "--adjust",	action='store_true',	help="enables state/priority adjustments. Needs uuid.")
parser.add_argument("-d", "--delete",	action='store_true',	help="deletes a job. Needs uuid.")
parser.add_argument("-t", "--test",	action='store_true',	help="when set, do not contact the server")
parser.add_argument("-S", "--server",	type=str,		help="the server URL (default http://localhost:8000/)",
                    default='http://localhost:8000/')

parser.add_argument("-s", "--state",	type=str,		help="sets the job state, needs *adjust* option",
                    default='')
parser.add_argument("-p", "--priority",	type=int,		help="sets the job priority, needs *adjust* option",
	            default=0)

parser.add_argument("-u", "--uuid",	type=str,		help="uuid of the job to be adjusted",
                    default='')

parser.add_argument("-i", "--id",	type=str,	default='',
                    help="id of the job to be adjusted (pk)")

parser.add_argument("-v", "--verbosity",	type=int, default=0, choices=[0, 1, 2],
                    help="set output verbosity")

parser.add_argument("-j", "--json_in",	type=str,	default='',
                    help="file from which to read job templates (must be a list)")

########################### Parse all arguments #########################
args = parser.parse_args()

usage	= args.usage

server	= args.server
state	= args.state
priority= args.priority
j_uuid	= args.uuid
j_id	= args.id
verb	= args.verbosity
tst	= args.test
adj	= args.adjust
delete	= args.delete
json_in	= args.json_in

# prepare a list which may be used in a variety of operations,
# contents will vary depending on context
jobList = []

###################### USAGE REQUESTED? ################################
if(usage):
    print(Usage)
    exit(0)

### p3s interface defined here
API  = serverAPI(server=server)

########################## UPDATE/ADJUSTMENT #############################
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
        resp = API.adjJob(a)
        if(verb>0): print(resp)

    exit(0) # done with update/adjust

###################### JOB DELETE ######################################
# Check if it was a deletion request
if(delete):
    response = None
    if(j_uuid=='' and j_id==''): exit(-1) # check if we have the key

# DELETE ALL!!!DANGEROUS!!!TO BE REMOVED IN PROD, do not document "ALL"
    if(j_uuid=='ALL' or j_id=='ALL'):
        resp = API.deleteAllJobs()
        if(verb>0): print(resp)
        exit(0)

    # Normal delete, by UUIDs:
    if(j_uuid!=''):
        if ',' in j_uuid: # assume we have a CSV list
            jobList = j_uuid.split(',')
        else:
            jobList.append(j_uuid)

        for j in jobList:
            resp = API.deleteJob(dict(uuid=j))
            if(verb>0): print(resp)
        exit(0)
        
    # Normal delete, by ID (PK):
    if(j_id!=''):
        if ',' in j_id: # assume we have a CSV list
            jobList = j_id.split(',')
        else:
            jobList.append(j_id)

        for j in jobList:
            resp = API.deleteJob(dict(pk=j))
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
    with open(json_in) as data_file:    
        data = json.load(data_file)

    for jj in data:
        j = Job()
        for k in jj.keys():
            if isinstance(jj[k],dict):
                j[k] = json.dumps(jj[k])
            else:
                j[k] = jj[k]
        jobList.append(j)

    if(verb>0): print("Number of jobs to be submitted: %s" % len(jobList))

    # Contact the server, try to register the job(s)
    for j in jobList:
        if(verb>1): print(j)
        if(tst): continue # just testing
        resp = API.addJob(j)
        if(verb>0): print(resp)


###################### GRAND FINALE ####################################
exit(0)
########################################################################
