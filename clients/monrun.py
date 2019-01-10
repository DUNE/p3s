#!/usr/bin/env python3.5

#########################################################
# This is an application-dependent script - it sends    #
# information about a graphics file to the server       #
# FIXME - need to cleanup later as this is not really   #
# a part of p3s proper                                  #
#########################################################


#########################################################
# TZ-awarewness:					#
# The following is not TZ-aware: datetime.datetime.now()#
# so we are using timezone.now() where needed		#
#########################################################

from django.conf	import settings
from django.utils	import timezone

import argparse
import uuid
import socket
import time
import datetime
import json
import csv

import os

from collections import OrderedDict

from serverAPI		import serverAPI
from clientenv		import clientenv
from clientUtils	import takeJson


#########################################################
settings.configure()

user = os.environ['USER']
envDict = clientenv(outputDict=True) # Will need ('server', 'verb'):
parser = argparse.ArgumentParser()

# ---
parser.add_argument("-D", "--delete", 			help="deletes an entry. Needs id or run number or job uuid", action='store_true')
parser.add_argument("-a", "--auto",			help="parse the current directory automatically",	action='store_true')
parser.add_argument("-s", "--summary",	type=str,	help="summary file name (JSON)",			default='')
parser.add_argument("-d", "--descr",	type=str,	help="description file name (JSON)",			default='')
parser.add_argument("-u", "--uuid",	type=str,	help="job uuid to delete or to register (override)",	default='')
parser.add_argument("-m", "--moveto",	type=str,	help="directory to move the results to, from cwd",	default='')
parser.add_argument("-j", "--jobtype",	type=str,	help="job type (which produced these data",		default='')
parser.add_argument("-i", "--id",	type=str,	help="id of the entry to be adjusted or deleted (pk)", 	default='')
parser.add_argument("-r", "--run",	type=str,	help="run number",					default='')
parser.add_argument("-T", "--timestamp",type=str,	help="enforce/override the timestamp - YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ]", default='')
parser.add_argument("-v", "--verbosity",type=int,	help="output verbosity, defaults to P3S default",	default=envDict['verb'])

parser.add_argument("-S", "--server",	type=str,
                    help="server URL: defaults to $DQM_SERVER or if unset to http://localhost:8000/",
                    default=envDict['dqmserver'])
# ---
args = parser.parse_args()

summary		= args.summary
description	= args.descr

job_uuid	= args.uuid
moveto		= args.moveto
jobtype		= args.jobtype
server		= args.server

delete		= args.delete
auto		= args.auto
pk		= args.id
run		= args.run
timestamp	= args.timestamp
verb		= args.verbosity

### The DQM server interface defined here
API  = serverAPI(server=server)

#########################################################
#########################################################
#########################################################

d = {}    


# ---
# DELETION
# ---
if(delete):
    if(run=='' and pk==''):
        print('Error: you need to specify either the run number or ID to delete entries. Exiting...')
        exit(-3)
        
    
    if(run!=''):
        if '::' in run:
            r,s = run.split('::')
            print(r,s)
            d['run']=r
            d['subrun']=s
        else:
            d['run']=r

    if(pk!=''):	d['pk']=pk

    resp = API.post2server('monitor', 'delmon', d)
    if(verb>0): print(resp)
    
    exit(0)

# ---
# MIGRATION
# ---

if(moveto!=''):
    if(pk==''):
        print('Need item IDs (pk)  in order to move them, exiting...')
        exit(-1)

    d['pk']	= pk
    d['moveto']	= moveto
    
    resp = API.post2server('monitor', 'move', d)
    if(verb>0): print(resp)
    
    exit(0)

# ---
# REGISTRAION
# ---
# By now we assume we are to perform registration of
# a "monitor run" on the server. First check if there is
# a description, otherwise it's pointless:
if(description==''):
    print("Missing description, exiting...")
    exit(-1)

summary_dict = {}
if(summary!=''):
    summary_dict = takeJson(summary, verb)
else:
    print("Missing summary, exiting...")
    exit(-1)
    

summary_data = ''
if(summary!=''):
    try:
        summaryFile = open(summary)
        summary_data = summaryFile.read()
        if(verb>2):
            print("Summary Data:")
            print(summary_data)
    except:
        print("Problem with summary file", summary)

# ---
# Handle file description
descrList	= description.split(',')
masterList	= []
    
for descr in descrList:
    if(verb>1): print("Opening description file", descr)
    descrFile = open(descr)
    data = json.load(descrFile)
    masterList = masterList+data # catenate, work with lists
    if(verb>2):
        print("Description file:", descr)
        print(data)

if(job_uuid==''): # default to local dir name
    d['j_uuid'] = os.path.basename(os.getcwd())
else:
    d['j_uuid'] = job_uuid
        

if(d['j_uuid']==''):
    print('Need job ID to proceed, exiting...')
    exit(-2)


tokens, run, subrun, dl = None, '','',''
try:
    print('Run descriptor:', summary_dict[0]["run"])

    tokens	= summary_dict[0]["run"].split('_')
    run		= tokens[0][3:]
    subrun	= tokens[1]
    if(len(tokens)>2): dl = tokens[2][2:]
except:
    print("Problem encountered while parsing the summary file, exiting...")
    exit(-3)
        
print('Run:', run, '   Subrun:', subrun, '   dl:', dl)

d['summary']	= summary_data
d['description']= json.dumps(masterList)
d['run']	= run
d['subrun']	= subrun
d['dl']		= dl
d['jobtype']	= jobtype

if(timestamp==''):
    d['ts']	= str(timezone.now())
else:
    d['ts']	= timestamp

if(verb>0): print('Using timestamp:', d['ts'])
    
resp = API.post2server('monitor', 'addmon', d)
print(resp)
    
exit(0)

# ---

#########################################################
