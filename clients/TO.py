#!/usr/bin/env python3.5


###############################################################
#                                                             #
# A utility which sends request to the p3s server             #
# to mark the pilots who didn't send their heartbeats within  #
# a certain time limit, as "timed-out".                       #
#                                                             #
# This can be developed for further useful cleanup kind of    #
# functionality.                                              #
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

parser.add_argument("-t", "--timeout",	type=int, default=600,			help="pilot timeout in seconds, default 600")

parser.add_argument("-S", "--server",	type=str, default=envDict['server'],	help="server URL: defaults to $P3S_SERVER")

parser.add_argument("-v", "--verbosity",type=int, default=envDict['verb'],	help="verbosity", choices=[0, 1, 2])

parser.add_argument("-d", "--direct",	action='store_true', help="direct logging in the internal server DB")


args	= parser.parse_args()
to	= args.timeout
verb	= args.verbosity
server	= args.server
direct	= args.direct

### p3s interface defined here
API  = serverAPI(server=server, verb=0)

d = dict(to=to, host=myhost)
if(direct): d['direct']='True'
resp = API.post2server('logic', 'pilotTO', d)
if(not direct and resp!=''): print(resp)
    


