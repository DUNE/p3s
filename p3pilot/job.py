#!/usr/bin/python
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
from pprint import pprint

import urllib
from urllib import request
from urllib import error
from urllib.error import URLError

# local import, requires PYTHONPATH to be set
from comms import data2post

#########################################################
settings.configure(USE_TZ = True)

#-------------------------
class Job(dict):
    def __init__(self, priority=0, stage='default', state='defined'):
        self['uuid']	= uuid.uuid1()
        self['stage']	= stage
        self['priority']= priority
        self['state']	= state
        self['subhost']	= socket.gethostname() # submission host
        self['ts']	= str(timezone.now()) # see TZ note on top

#-------------------------
parser = argparse.ArgumentParser()

parser.add_argument("-S", "--server",
                    type=str,
                    default='http://localhost:8000/',
                    help="the server address, defaults to http://localhost:8000/")

parser.add_argument("-s", "--state",
                    type=str,
                    default='',
                    help="sets the job state, needs *adjust* option to be activated")

parser.add_argument("-p", "--priority",
                    type=int,
                    default=-1,
                    help="sets the job priority, needs *adjust* option to be activated")

parser.add_argument("-a", "--adjust",
                    action='store_true',
                    help="enables state or priority adjustments. Needs uuid.")

parser.add_argument("-d", "--delete",
                    action='store_true',
                    help="deletes a job. Needs uuid.")

parser.add_argument("-u", "--uuid",
                    type=str,
                    default='',
                    help="uuid of the job to be adjusted")

parser.add_argument("-t", "--test",
                    action='store_true',
                    help="when set, forms a request but does not contact the server")

parser.add_argument("-v", "--verbosity",
                    type=int, default=0, choices=[0, 1, 2],
                    help="set output verbosity")

parser.add_argument("-j", "--json_in",
                    type=str,
                    default='',
                    help="file from which to read job templates (must be a list)")

########################### Parse all arguments #########################
args = parser.parse_args()

server	= args.server
state	= args.state
priority= args.priority
j_uuid	= args.uuid
verb	= args.verbosity
tst	= args.test
adj	= args.adjust
delete	= args.delete
json_in	= args.json_in

# prepare a list which may be used in a variety of operations,
# contents will vary depending on context
jobList = []

########################## UPDATE/ADJUSTMENT #############################
# Check if an adjustment of an existing job is requested, and send a
# request to the server to do so. Can adjust priority, state.

if(adj):
    if(j_uuid==''):			exit(-1) # check if we have the key
    if(priority==-1 and state==''):	exit(-1) # nothing to adjust

    if ',' in j_uuid:
        jobList = j_uuid.split(',')
    else:
        jobList.append(j_uuid)
        
    for j in jobList:
        a = dict(uuid=j) # create a dict to be serialized and sent to the server
        if(priority!=-1):	a['priority']	= str(priority)
        if(state!=''):		a['state']	= state
        adjData = data2post(a).utf8()

        try:
            url = 'jobs/set'
            response = urllib.request.urlopen(server+url, adjData) # POST
        except URLError:
            exit(1)
    
        data = response.read()
        if(verb >0): print (data)

    exit(0) # done with update/adjust

###################### JOB DELETE ######################################
# Check if it was a deletion request
if(delete):
    if(j_uuid==''): exit(-1) # check if we have the key

    if ',' in j_uuid:
        jobList = j_uuid.split(',')
    else:
        jobList.append(j_uuid)

    for j in jobList:
        delData = data2post(dict(uuid=j)).utf8()

        try:
            url = 'jobs/delete'
            response = urllib.request.urlopen(server+url, delData) # POST
        except URLError:
            exit(1)
    
        data = response.read()
        if(verb >0): print (data)

    exit(0)

########################################################################
# Catch-all for uuid: should have handled uuid-specific requests already,
# if we are here it's an error
if(j_uuid!=''): exit(-1)

########################## REGISTRATION ################################
# Check if we want to read a json file with job templates and send
# these entries to the server
if(json_in!=''):
    with open(json_in) as data_file:    
        data = json.load(data_file)

    for jj in data:
        jobList.append(Job(priority	= jj['priority'],
                           state	= jj['state'],
                           stage	= jj['stage']))

else:
    # Create and serialize a single job, and register it on the server.
    # This will be a default object, not useable unless updated later.
    jobList.append(Job())


if(verb>0):
    print("Number of jobs to be submitted: %s" % len(jobList))
# Collection of candidate jobs has been prepared.
# Now contact the server and try to register.
for j in jobList:
    jobData = data2post(j).utf8()
    if(verb>0):	print(jobData)
    if(tst):	continue # if in test mode skip contact with the server

    try:
        url = 'jobs/addjob'
        response = urllib.request.urlopen(server+url, jobData) # POST
    except URLError:
        exit(1)
    
    data = response.read()

    if(verb >0): print (data)

# Grand finale      
exit(0)
########################################################################
