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

parser.add_argument("-j", "--json_in",	type=str,	help="summary file name", default='')

parser.add_argument("-J", "--job",	type=str,	help="job uuid to delete or to register (override)", default='')

parser.add_argument("-d", "--delete",	action='store_true',	help="deletes an entry. Needs entry id or run number, or job uuid")

parser.add_argument("-a", "--auto",	action='store_true',	help="parse the current directory automatically")

parser.add_argument("-i", "--id",	type=str,	default='',
                    help="id of the entry to be adjusted or deleted (pk)")

parser.add_argument("-r", "--run",	type=str,	default='',
                    help="run number")

parser.add_argument("-T", "--timestamp",type=str,	default='',
                    help="override the timestamp with user value like 2018-05-16, NOW has a special meaning")


parser.add_argument("-S", "--server",	type=str,
                    help="server URL: defaults to $DQM_SERVER or if unset to http://localhost:8000/",
                    default=envDict['dqmserver'])

parser.add_argument("-v", "--verbosity", type=int,	default=envDict['verb'], help="output verbosity, defaults to P3S default")

args = parser.parse_args()

json_in		= args.json_in
job		= args.job
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

if(json_in!=''):
    
    data = takeJson(json_in, verb)
    print(data)

    if(job==''):
        d['j_uuid'] = os.path.basename(os.getcwd())
    else:
        d['j_uuid'] = job
        

    if(d['j_uuid'==''):
        print('Need job ID to proceed, exiting...')
        exit(-1)
        
    print('Run descriptor:', data[0]["run"])

    rs		= data[0]["run"].split('_')
    run		= rs[0][3:]
    subrun	= rs[1]
    
    print('Run:', run, '   Subrun:', subrun)

    d['json']	= data
    d['run']	= run
    d['subrun']	= subrun

    resp = API.post2server('monitor', 'addmon', d)
    print(resp)
    exit(0)

if(delete):
    if(run=='' and pk==''):
        print('Need to specify the run number or ID to delete, exiting...')
        exit(-1)
        
    
    if(run!=''): d['run'] = run
    if(pk!=''): d['pk'] = pk

    resp = API.post2server('monitor', 'delmon', d)
    print(resp)
    
exit(0)

#########################################################
