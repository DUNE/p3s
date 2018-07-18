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

parser.add_argument("-s", "--summary",	type=str,	help="summary file name (JSON)", default='')

parser.add_argument("-D", "--description",type=str,	help="description file name (JSON)", default='')

parser.add_argument("-u", "--uuid",	type=str,	help="job uuid to delete or to register (override)", default='')

parser.add_argument("-d", "--delete",	action='store_true',	help="deletes an entry. Needs entry id or run number, or job uuid")

parser.add_argument("-a", "--auto",	action='store_true',	help="parse the current directory automatically")

parser.add_argument("-i", "--id",	type=str,	default='',
                    help="id of the entry to be adjusted or deleted (pk)")

parser.add_argument("-r", "--run",	type=str,	default='',
                    help="run number")

parser.add_argument("-T", "--timestamp",type=str,	default='',
                    help="enforce/override the timestamp - YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ]")


parser.add_argument("-S", "--server",	type=str,
                    help="server URL: defaults to $DQM_SERVER or if unset to http://localhost:8000/",
                    default=envDict['dqmserver'])

parser.add_argument("-v", "--verbosity", type=int,	default=envDict['verb'], help="output verbosity, defaults to P3S default")

args = parser.parse_args()

summary		= args.summary
description	= args.description

job_uuid	= args.uuid
server		= args.server

delete		= args.delete
auto		= args.auto
pk		= args.id
run		= args.run
timestamp	= args.timestamp
verb		= args.verbosity

### dqm interface defined here
API  = serverAPI(server=server)

#########################################################

# if(delete):
#     if(p_id == '' and run == '' and job == ''):
#         print('ID/run/job for deletion not specified, exiting')
#         exit(-1)

#     resp = ''
#     if(p_id != ''):	resp = API.post2server('evd', 'delete', dict(pk=p_id))
#     if(run != ''):	resp = API.post2server('evd', 'delete', dict(run=run))
#     if(job != ''):	resp = API.post2server('evd', 'delete', dict(j_uuid=job))
        
#     if(verb>0): print(resp)

#     exit(0)

#########################################################

d = {}    
#########################################################

if((summary=='' or description=='') and not delete):
    print("Missing input summary and/or description, exiting...")
    exit(-1)
    
if(summary!='' and description!=''):
    
    summary_dict = takeJson(summary, verb)

    sf = open(summary)
    summary_data = sf.read()
    print(summary_data)
    
    df = open(description)
    description_data = df.read()
    print(description_data)
    
#    description_data = takeJson(description, verb)
#    print(description_data)

    if(job_uuid==''):
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
    d['description']	= description_data
    d['run']		= run
    d['subrun']		= subrun

    if(timestamp==''):
        d['ts']	= str(timezone.now())
    else:
        d['ts']	= timestamp

    if(verb>0): print('Using timestamp:', d['ts'])
    
    resp = API.post2server('monitor', 'addmon', d)
    print(resp)
    
    exit(0)

if(delete):
    if(run=='' and pk==''):
        print('Need to specify the run number or ID to delete, exiting...')
        exit(-3)
        
    
    if(run!=''): d['run'] = run
    if(pk!=''): d['pk'] = pk

    resp = API.post2server('monitor', 'delmon', d)
    print(resp)
    
    exit(0)

print("Inconsistent input, check...")
exit(-3)

#########################################################
