#!/usr/bin/env python3.5


###############################################################
#                                                             #
# A logging interface for p3s which allows scripts            #
# such as running on crontab to communicate their activity    #
# in a centralized manner, to be displayed in momitoring      #
# pages.                                                      #
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

parser.add_argument("-S", "--server",	type=str,
                    help="server URL: defaults to $P3S_SERVER or if unset to http://localhost:8000/",
                    default=envDict['server'])

parser.add_argument("-v", "--verbosity",	type=int, default=envDict['verb'], choices=[0, 1, 2],
                    help="set output verbosity")


args	= parser.parse_args()
verb	= args.verbosity
server	= args.server

### p3s interface defined here
API  = serverAPI(server=server, verb=0)


resp = API.post2server('logic', 'service', dict(foo='moo'))
print(resp)
    


