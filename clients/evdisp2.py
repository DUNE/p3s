#!/usr/bin/env python3.5

#########################################################
# This version of the evdispl client aims to comply     #
# with the filename and other changes in the evdisp     #
# app and also to take advantage of the metadata        #
# feature in the current DQM service (as of Aug 2018).  #
#                                                       #
# As such, its purpose is to generate JSON to feed a    #
# separate (universal) client, the "monrun"             #
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

########################################################
fileTypes = OrderedDict([
    ('adcraw_tpp',		'Raw ADC'),
    ('chmet_ped_tps',		'ADC Pedestals'),
    ('chmet_pedexc_tps',	'ADC pedestal peak bin excess'),
    ('chmet_pedorf_tps',	'ADC pedestal out-of-range fraction'),
    ('chmet_pedrms_tps',	'ADC pedestal RMS'),
    ('detprep-',		'Raw ADC Collection View'),
])
# ---
output		= OrderedDict()
filesDict	= OrderedDict()

########################################################
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


### dqm interface defined here
API  = serverAPI(server=server)

#########################################################

d = {}    
#########################################################
if(auto):
    if(job==''): job=os.path.basename(os.getcwd())

    timestamp	= str(timezone.now())
    entries	= []
    
    output['Category']	= '2D Event Display'

    for k in fileTypes:
        print('KEY----------------->', k)
        files = []
        for f in os.listdir("."):
            if (f.startswith(k) and f.endswith(".png")):
                files.append(f)
                
        if (len(files)>0): filesDict[fileTypes[k]] = ",".join(files)

        
    output['Files']	= filesDict
    print(json.dumps(output))
exit(0)

#########################################################
