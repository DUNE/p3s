#!/usr/bin/env python3.5



#########################################################
# THIS SCRIPT IS DEPRECATED AS OF JULY 2018 AND IS KEPT #
# HERE FOR REFERENCE                                    #
#########################################################



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

settings.configure()

user = os.environ['USER']
envDict = clientenv(outputDict=True) # Will need ('server', 'verb'):
parser = argparse.ArgumentParser()

parser.add_argument("-j", "--json_in",	type=str,	help="image file descriptor", default='')

parser.add_argument("-J", "--job",	type=str,	help="job uuid to delete or to register (override)", default='')

parser.add_argument("-d", "--delete",	action='store_true',	help="deletes an entry. Needs entry id or run number, or job uuid")

parser.add_argument("-a", "--auto",	action='store_true',	help="parse the current directory automatically")

parser.add_argument("-i", "--id",	type=str,	default='',
                    help="id of the entry to be adjusted or deleted (pk)")

parser.add_argument("-r", "--run",	type=str,	default='',
                    help="run number to be deleted, or to override the entry with; NEXT has a special meaning")

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
p_id		= args.id
run		= args.run
timestamp	= args.timestamp
verb		= args.verbosity

cgdict = {
    '00000-02559':1,
    '02560-04639':2,
    '05120-07679':3,
    '07680-09759':4,
    '10240-12799':5,
    '12800-14879':6
}


### dqm interface defined here
API  = serverAPI(server=server)

#########################################################

if(delete):
    if(p_id == '' and run == '' and job == ''):
        print('ID/run/job for deletion not specified, exiting')
        exit(-1)

    resp = ''
    if(p_id != ''):	resp = API.post2server('evd', 'delete', dict(pk=p_id))
    if(run != ''):	resp = API.post2server('evd', 'delete', dict(run=run))
    if(job != ''):	resp = API.post2server('evd', 'delete', dict(j_uuid=job))
        
    if(verb>0): print(resp)

    exit(0)

#########################################################

d = {}    
#########################################################
if(auto):
    if(job==''): job=os.path.basename(os.getcwd())

    timestamp	= str(timezone.now())
    entries	= []
    
    for f in os.listdir("."):
        filedict = {}
        if f.endswith(".png"):
            if(verb>0): print(f)
            for t in ('raw','prep'):
                
                # important - this will change, this is a necessary stop-gap hack
                # based on the current convention re: filenames
                
                filedict['evnum']	= f.split('_')[2][3:] # will correct later
                filedict['run']		= API.get2server('evd', 'maxrun', '')

                # in MCC the runs are now fixed at 1 so we need to run a counter
                # we do ignore the constant "1" here in the filename
                
                if(verb>0): print('Will use the run:', filedict['run'])
                
                if(t in f): filedict['datatype'] = t
                
                for cg in cgdict.keys():
                    if(cg in f): filedict['changroup'] = cgdict[cg]
                    
            filedict['ts'] = timestamp
            filedict['j_uuid'] = job
            
            entries.append(filedict)

    if(verb>0): print(entries)
    d['json'] = json.dumps(entries)
    
#########################################################

if(json_in!=''):
    data = takeJson(json_in, verb)

    for entry in data:
        if(run!=''):
            if(run=='NEXT'): run=API.get2server('evd', 'maxrun', '')
            entry['run']=run
        if(timestamp!=''):
            if(timestamp=='NOW'): timestamp=str(timezone.now())
            entry['ts']=timestamp
        else:
            timestamp=str(timezone.now())

    d['json'] = json.dumps(data)

resp = API.post2server('evd', 'add', d)
print(resp)


exit(0)

#########################################################
