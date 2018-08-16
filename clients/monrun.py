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
parser.add_argument("-d", "--delete", 			help="deletes an entry. Needs id or run number or job uuid", action='store_true')
parser.add_argument("-a", "--auto",			help="parse the current directory automatically",	action='store_true')
parser.add_argument("-s", "--summary",	type=str,	help="summary file name (JSON)",			default='')
parser.add_argument("-D", "--descr",	type=str,	help="description file name (JSON)",			default='')
parser.add_argument("-u", "--uuid",	type=str,	help="job uuid to delete or to register (override)",	default='')
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

if((summary=='' or description=='') and not delete):
    print("Missing input summary and/or description, exiting...")
    exit(-1)
    
if(description!=''):

    summary_dict = {}
    if(summary!=''): summary_dict = takeJson(summary, verb)

    summaryFile = open(summary)
    summary_data = summaryFile.read()
    
    if(verb>2):
        print("Summary Data:")
        print(summary_data)

    descrList	= description.split(',')
    masterList	= []
    
    for descr in descrList:
        if(verb>1): print("Opening description file", descr)
        descrFile = open(descr)
        data = json.load(descrFile)
        masterList = masterList+data # catenate, work with lists
        print(data)


    exit(0)
    
    if(job_uuid==''): # default to local dir name
        d['j_uuid'] = os.path.basename(os.getcwd())
    else:
        d['j_uuid'] = job_uuid
        

    if(d['j_uuid']==''):
        print('Need job ID to proceed, exiting...')
        exit(-2)
        
    print('Run descriptor:', summary_dict[0]["run"])

    rs		= summary_dict[0]["run"].split('_')
    run		= rs[0][3:]
    subrun	= rs[1]
    
    print('Run:', run, '   Subrun:', subrun)

    d['summary']	= summary_data
    d['description']	= json.dumps(masterList)
    d['run']		= run
    d['subrun']		= subrun
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

if(delete):
    if(run=='' and pk==''):
        print('Need to specify the run number or ID to delete, exiting...')
        exit(-3)
        
    
    if(run!=''):	d['run']	= run
    if(pk!=''):		d['pk']		= pk

    resp = API.post2server('monitor', 'delmon', d)
    if(verb>0): print(resp)
    
    exit(0)

print("Inconsistent input, please check...")
exit(-3)

#########################################################
