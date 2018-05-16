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

parser.add_argument("-j", "--json_in",	type=str,	help="image file descriptor", default='')

parser.add_argument("-d", "--delete",	action='store_true',	help="deletes an entry. Needs entry id or run number.")

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
server		= args.server
delete		= args.delete
p_id		= args.id
run		= args.run
timestamp	= args.timestamp
verb		= args.verbosity

f = None


### dqm interface defined here
API  = serverAPI(server=server)

print(json_in)

data = takeJson(json_in, verb)

for entry in data:
    if(run!=''):
        if(run=='NEXT'): run=API.get2server('evdisp', 'index', '')
        entry['run']=run
    if(timestamp!=''):
        if(timestamp=='NOW'): timestamp=str(timezone.now())
        entry['ts']=timestamp

# print(data)

d = {}

d['json'] = json.dumps(data)

# print(d)


resp = API.post2server('evdisp', 'add', d)

print(resp)



exit(0)



if(delete):
    if(p_id == '' and run == ''):
        print('ID/run for deletion not specified, exiting')
        exit(-1)

    resp = ''
    if(p_id != ''):
        resp = API.post2server('purity', 'del', dict(pk=p_id))
    if(run != ''):
        resp = API.post2server('purity', 'del', dict(run=run))
        
    if(verb>0): print(resp)

    exit(0)


try:
    f = open(filename,"r")
except:
    print("file '%s' not found." % filename)
    exit(-1)
    
myreader = csv.reader(f, delimiter=' ', quotechar='|')

frst = True

if(run==''):
    run = API.get2server('purity', 'ind', '')
    if(verb>0): print('Assigning run number based on DB: '+run)

items = ('run','tpc', 'lifetime', 'error', 'count')

for row in myreader:    # print(row)
    if(frst):
        frst = False
        continue # skip Bruce's header
    
    cnt=0
    d = OrderedDict.fromkeys(items)
    for e in row:
        e = e.replace(',', '')
        d[items[cnt]] = e
        cnt+=1
        # print(cnt)

    d['run']	= run

    if(timestamp==''):
        d['ts']	= str(timezone.now())
    else:
        d['ts']	= timestamp

    if(verb>0): print('Using timestamp:', d['ts'])
    
    resp = API.post2server('purity', 'add', d)

    
    if(verb>0): print(resp)
