#!/usr/bin/env python3.5

#########################################################
# Exceptionally, this is an application-dependent	#
# script - it parses a comma-separated file with a      #
# header and creates a dictionaty which can be		#
# sent to the DQM server for inclusion into a table     #
#                                                       #
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

import os

from collections import OrderedDict

from serverAPI import serverAPI
from clientenv import clientenv


#########################################################
settings.configure()

user		= os.environ['USER']
envDict = clientenv(outputDict=True) # Will need ('server', 'verb'):
parser = argparse.ArgumentParser()

parser.add_argument("-d", "--delete",	action='store_true',	help="deletes an entry. Needs entry id or run number.")

parser.add_argument("-f", "--file",	type=str,	help="input file (TXT) with purity data",		default='')
parser.add_argument("-F", "--infile",	type=str,	help="name of the raw data input file used",		default='')
parser.add_argument("-i", "--id",	type=str,	help="id of the entry to be adjusted or deleted (pk)",	default='')
parser.add_argument("-r", "--run",	type=str,	help="run number for items to be added or deleted, AUTO has a special meaning",	default='')

parser.add_argument("-T", "--timestamp",type=str,	default='',
                    help="enforce/override the timestamp - YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ]")


parser.add_argument("-S", "--server",	type=str,
                    help="server URL: defaults to $DQM_SERVER or if unset to http://localhost:8000/",
                    default=envDict['dqmserver'])

parser.add_argument("-v", "--verbosity", type=int,	default=envDict['verb'], help="output verbosity, defaults to P3S default")

args = parser.parse_args()

filename	= args.file
infile		= args.infile
server		= args.server
delete		= args.delete
p_id		= args.id
run		= args.run
timestamp	= args.timestamp
verb		= args.verbosity

f = None


### dqm interface defined here
API  = serverAPI(server=server)


#######################################################################
# FIXME - will need to add Idx+dl here 
#######################################################################
if(delete):
    if(p_id == '' and run == '' and infile == ''):
        print('ID/run/infile for deletion not specified, exiting')
        exit(-1)

    resp = ''
    if(p_id != ''):	resp = API.post2server('purity', 'delete', dict(pk=p_id))
    if(run != ''):	resp = API.post2server('purity', 'delete', dict(run=run))
    if(infile != ''):	resp = API.post2server('purity', 'delete', dict(infile=infile))
    if(verb>0):		print(resp)

    exit(0)

#######################################################################

try:
    f = open(filename,"r")
except:
    print("Could not open file '%s'." % filename)
    exit(-1)

data = [x.strip().replace(' ', '') for x in f.readlines()]

# ---
# Until we don't get the "real" file info e.g. run, idx and dl
# we rely on the auto-incremented counter on the server to
# provide one

err = False
if(run=='AUTO'): # will use counter from the DB to generate a number
    run = API.get2server('purity', 'index', '')
    if 'error' in run:
        err = True
        run = 0
        if(verb>0): print('Error detected while assigning run, will use zero value for testing only ')
    else:
        if(verb>0): print('Assigning run number based on DB: '+run)

# ---
# This has to match the attributes of the "purity" model in the display app
items = ('run','tpc', 'lifetime', 'error', 'count', 'sn', 'snclusters', 'drifttime')

for row in data[1:]:
    cnt=0
    d = OrderedDict.fromkeys(items) # note we take ordered keys from the tuple
    for e in row.split(','):
        d[items[cnt]] = e
        if(verb>2): print(items[cnt], e)
        cnt+=1

    # d['run']	= run
    if infile!='': d['infile'] = infile

    if(timestamp==''):
        pass  # d['ts']	= str(timezone.now()) ---- shift to server
    else:
        d['ts']	= timestamp
        if(verb>0): print('Using timestamp:', d['ts'])
        
    if verb>0: print(d)
    
    if not err:
        resp = API.post2server('purity', 'add', d)
        if(verb>0): print(resp)


exit(0)

    
