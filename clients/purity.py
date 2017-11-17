#!/usr/bin/env python3.5
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

from serverAPI import serverAPI
from clientenv import clientenv


#########################################################
settings.configure()

user		= os.environ['USER']
envDict = clientenv(outputDict=True) # Will need ('server', 'verb'):
parser = argparse.ArgumentParser()

parser.add_argument("-f", "--file",	type=str,	help="input file", default='')

parser.add_argument("-d", "--delete",	action='store_true',	help="deletes an entry. Needs entry id or run number.")

parser.add_argument("-i", "--id",	type=str,	default='',
                    help="id of the entry to be adjusted or delted (pk)")

parser.add_argument("-r", "--run",	type=str,	default='',
                    help="run number of the entries to be added, adjusted or deleted")


parser.add_argument("-S", "--server",	type=str,
                    help="server URL: defaults to $DQM_SERVER or if unset to http://localhost:8000/",
                    default=envDict['dqmserver'])


args = parser.parse_args()

filename	= args.file
server		= args.server
delete		= args.delete
p_id		= args.id
run		= args.run


f = None


### dqm interface defined here
API  = serverAPI(server=server)


if(delete):
    if(p_id == '' and run == ''):
        print('ID/run for deletion not specified, exiting')
        exit(-1)

    resp = ''
    if(p_id != ''):
        resp = API.post2server('purity', 'del', dict(pk=p_id))
    if(run != ''):
        resp = API.post2server('purity', 'del', dict(run=run))
        
    print(resp)

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
    print('Assigning run number based on DB: '+run)

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
    d['ts']	= str(timezone.now())
    
    resp = API.post2server('purity', 'add', d)

    
    print(resp)
