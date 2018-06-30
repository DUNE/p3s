#!/usr/bin/env python3.5


###############################################################
#                                                             #
# A utility which sends request to the p3s server             #
# a) to mark the pilots who didn't send their heartbeats      #
# within a certain time limit, as "timed-out".                #
#                                                             #
# b) to erase from the DB jobs which are in the running state #
# but beyond their assigned time limit so presumed dead       #
#                                                             #
###############################################################

import argparse
import json
import os
import socket

from serverAPI import serverAPI
from clientenv import clientenv

envDict = clientenv(outputDict=True) # Will need ('server', 'verb'):

myhost = socket.gethostname()

parser = argparse.ArgumentParser()

parser.add_argument("-t", "--timeout",	type=int, default=0,			help="pilot timeout in seconds, default 600")

parser.add_argument("-S", "--server",	type=str, default=envDict['server'],	help="server URL: defaults to $P3S_SERVER")

parser.add_argument("-v", "--verbosity",type=int, default=envDict['verb'],	help="verbosity", choices=[0, 1, 2])

parser.add_argument("-d", "--direct",	action='store_true', help="direct logging in the internal server DB")

parser.add_argument("-w", "--what",	type=str, default='pilot',
                    help="what object to time out")



args	= parser.parse_args()
to	= args.timeout
verb	= args.verbosity
server	= args.server
direct	= args.direct
what	= args.what

### p3s interface defined here
API  = serverAPI(server=server, verb=0)

if(what=='pilot'):
    if(to==0): exit # careful with the pilots, require explicit value
    d = dict(to=to, host=myhost)
    if(direct): d['direct']='True'
    resp = API.post2server('logic', 'pilotTO', d)
    if(not direct and resp!=''):
        print(resp)
    
    exit
    print('done with pilot TO')
    # assume it's a job

if(verb>0): print('will be TOing jobs with timeout', to)

d = dict(to=to, host=myhost)
if(direct): d['direct']='True'
resp = API.post2server('logic', 'jobTO', d)

if(not direct and resp!=''): print(resp)
exit
    


