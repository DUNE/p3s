#!/usr/bin/env python3.5
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
import csv

import os

from collections import OrderedDict

from serverAPI import serverAPI
from clientenv import clientenv


#########################################################
settings.configure(USE_TZ = True)

user		= os.environ['USER']
envDict = clientenv(outputDict=True) # Will need ('server', 'verb'):
parser = argparse.ArgumentParser()

parser.add_argument("-f", "--file",	type=str,	help="input file", default='')
parser.add_argument("-d", "--delete",	action='store_true',	help="deletes an entry. Needs id.")
parser.add_argument("-i", "--id",	type=str,	default='',
                    help="id of the job to be adjusted (pk)")


parser.add_argument("-S", "--server",	type=str,
                    help="server URL: defaults to $P3S_SERVER or if unset to http://localhost:8000/",
                    default=envDict['server'])


args = parser.parse_args()

filename	= args.file
server		= args.server
delete		= args.delete
p_id		= args.id


f = None


### dqm interface defined here
API  = serverAPI(server=server)

if(delete):
    if(p_id == ''):
        print('ID for deletion not specified, exiting')
        
    resp = API.post2server('purity', 'del', dict(pk=p_id))
    print(resp)

    exit(0)


try:
    f = open(filename,"r")
except:
    print("file '%s' not found." % filename)
    exit(-1)
    
myreader = csv.reader(f, delimiter=' ', quotechar='|')

frst = True

items = ('run','tpc', 'lifetime', 'error', 'count')
for row in myreader:
    # print(row)
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
    resp = API.post2server('purity', 'add', d)
    print(resp)
