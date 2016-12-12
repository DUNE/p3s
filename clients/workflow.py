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

import networkx as nx

#########################################################
settings.configure(USE_TZ = True)

Usage		= '''Usage:

For command line options run the pilot with "--help" option.

* Workflow definitions * 

Option "-g" allows to read and parse contents of a graphML file containing
a workflow description.

'''

#-------------------------
class Job(dict):
    def __init__(self, name='', priority=0, stage='default', state='defined'):
        self['name']	= name
        self['uuid']	= uuid.uuid1()
        self['stage']	= stage
        self['priority']= priority
        self['state']	= state
        self['subhost']	= socket.gethostname() # submission host
        self['ts']	= str(timezone.now()) # see TZ note on top

#-------------------------
parser = argparse.ArgumentParser()

parser.add_argument("-g", "--graphml",	type=str,	default='',
                    help="GraphML file to be read and parsed.")

parser.add_argument("-o", "--out",	action='store_true',
                    help="output the graph to stdout")

parser.add_argument("-H", "--usage",	action='store_true',
                    help="print usage notes and exit")
parser.add_argument("-S", "--server",	type=str,	default='http://localhost:8000/',
                    help="the server address, defaults to http://localhost:8000/")
parser.add_argument("-s", "--state",	type=str,	default='',
                    help="sets the job state, needs *adjust* option to be activated")
parser.add_argument("-p", "--priority",	type=int,	default=-1,
                    help="sets the job priority, needs *adjust* option to be activated")
parser.add_argument("-a", "--adjust",	action='store_true',
                    help="enables state or priority adjustments. Needs uuid.")
parser.add_argument("-d", "--delete",	action='store_true',
                    help="deletes a job. Needs uuid.")
parser.add_argument("-u", "--uuid",	type=str,	default='',
                    help="uuid of the job to be adjusted")
parser.add_argument("-i", "--id",	type=str,	default='',
                    help="id of the job to be adjusted (pk)")
parser.add_argument("-t", "--test",	action='store_true',
                    help="when set, forms a request but does not contact the server")
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
graphml	= args.graphml
out	= args.out

# prepare a list which may be used in a variety of operations,
# contents will vary depending on context
jobList = []

###################### USAGE REQUESTED? ################################
if(usage):
    print(Usage)
    exit(0)

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
    response = None
    if(j_uuid=='' and j_id==''): exit(-1) # check if we have the key

# DELETE ALL!!!DANGEROUS!!!TO BE REMOVED IN PROD, do not document "ALL"
    if(j_uuid=='ALL' or j_id=='ALL'):
        try:
            url = 'jobs/deleteall'
            response = urllib.request.urlopen(server+url) # GET
        except URLError:
            exit(1)

        data = response.read()
        if(verb >0): print (data)

    # Normal delete, by key(s)
    # UUID:
    if(j_uuid!=''):
        if ',' in j_uuid: # assume we have a CSV list
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

    # ID (PK):
    if(j_id!=''):
        if ',' in j_id: # assume we have a CSV list
            jobList = j_id.split(',')
        else:
            jobList.append(j_id)

        for j in jobList:
            delData = data2post(dict(pk=j)).utf8()

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
# these entries to the server. Currently the only option to add a job
# programmatically.

if(graphml!=''):
    if(verb > 1): print ('Reading file', graphml)
    g = nx.read_graphml(graphml)

    if(out):
        print("---- NODES ----")
        print(g.nodes())
        for n in g.nodes():
            print(n)

        print("---- EDGES ----")
        for e in g.edges():
            x = g.edge[e[0]][e[1]]
            print(e,x)



###################### GRAND FINALE ####################################
exit(0)
########################################################################
