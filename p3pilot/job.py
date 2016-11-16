#!/usr/bin/python

from django.conf import settings
from django.utils import timezone

import argparse
import uuid
import socket
import time
import datetime

import urllib
from urllib import request
from urllib import error
from urllib.error import URLError

#########################################################
settings.configure(USE_TZ = True)

#-------------------------
class Job(dict):
    def __init__(self):
        self['uuid']	= uuid.uuid1()
        self['stage']	= 'default'
        self['priority']= 0
        self['state']	= 'defined'
        self['subhost']	= socket.gethostname() # submission host
        self['ts']	= str(timezone.now()) # ts = str(datetime.datetime.now()): problems with DB due to TZ
        

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
########################################################################

# Check if an adjustment of an existing job is requested,
# and contact the server to do so. If not, proceed to attempt
# a job registration
if(adj): # adjust priority, state
    if(j_uuid==''):
        exit(-1)

    if(priority==-1 and state==''):
        exit(-1)

    a = dict()
    a['uuid'] = j_uuid
    if(priority!=-1):
        a['priority'] = str(priority)

    if(state!=''):
        a['state'] = state

    adjData = urllib.parse.urlencode(a)
    adjData = adjData.encode('UTF-8')

    try:
        url = 'jobs/set'
        response = urllib.request.urlopen(server+url, adjData) # POST
    except URLError:
        exit(1)
    
    data = response.read()

    if(verb >0):
        print (data)

    exit(0)

# Check if it was a deletion request
if(delete):
    if(j_uuid==''):
        exit(-1)
    d = dict()
    d['uuid'] = j_uuid

    delData = urllib.parse.urlencode(d)
    delData = delData.encode('UTF-8')
    print(delData)

    try:
        url = 'jobs/delete'
        response = urllib.request.urlopen(server+url, delData) # POST
    except URLError:
        exit(1)
    
    data = response.read()

    if(verb >0):
        print (data)

    exit(0)
########################################################################
if(j_uuid!=''): # should have handled adjust uuid-specific requests already, can't be here with uuid
    exit(-1)


########################################################################
# So we want to create and serialize job, and register it on the server
j = Job()
jobData = urllib.parse.urlencode(j)
jobData = jobData.encode('UTF-8')

if(verb>0):
    print(jobData)

if(tst): # if in test mode simply bail
    exit(0)


try:
    url = 'jobs/addjob'
    response = urllib.request.urlopen(server+url, jobData) # POST
except URLError:
    exit(1)
    
data = response.read()

if(verb >0):
    print (data)
    
exit(0)

