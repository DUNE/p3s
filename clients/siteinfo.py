#!/usr/bin/env python3.5

#########################################################
# This script allows to define a p3s site on the        #
# server using a JSON-formatted description             #
#########################################################


#########################################################
# TZ-awarewness:					#
# The following is not TZ-aware: datetime.datetime.now()#
# so we are using timzone.now() where needed		#
#########################################################

from django.conf	import settings
from django.utils	import timezone

import argparse
import uuid
import socket
import time
import datetime
import logging
import json
import os

import networkx as nx

from serverAPI import serverAPI
from clientenv import clientenv

settings.configure(USE_TZ = True)

envDict = clientenv(outputDict=True) # Will need ('server', 'verb'):

host	= socket.gethostname()
parser	= argparse.ArgumentParser()

parser.add_argument("-S", "--server",	type=str,	default=envDict['server'],
                    help='server URL: defaults to $P3S_SERVER or if unset to '+envDict['server'])

parser.add_argument("-v", "--verbosity",type=int,	default=envDict['verb'], choices=[0, 1, 2], help="verbosity")

parser.add_argument("-j", "--json",	type=str,	default='', help='name of the file containing site info in JSON format')

parser.add_argument("-d", "--delete",	type=str,	default='', help='name of the site to be deleted')


########################### Parse all arguments #########################
args = parser.parse_args()

server	= args.server
delete	= args.delete
verb	= args.verbosity
jsite	= args.json

### p3s interface defined here
API  = serverAPI(server=server, verb=verb)

if(delete!=''):
    resp = API.post2server('site', 'deleteURL', {'site': delete})
    if(verb>0): print(resp)
    exit(0)

if(jsite==''):
    print('No input specified')
    exit(-1)

content = ''
try:
    f = open(jsite, 'r')
    content = f.read()
    f.close()
    if(verb>1): print(content)
except:
    print('Problems reading input file %s' % site)
    exit(-1)


resp = API.post2server('site', 'defineURL', {'site': content})
    
if(verb>1): print (resp)
exit(0)

