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

parser.add_argument("-n", "--name",	type=str,	default='',
                    help="the name of the service publishing the message")

parser.add_argument("-m", "--message",	type=str,	default='',
                    help="the message to be published on the server")

parser.add_argument("-d", "--delete",	action='store_true',	help="deletes an entry. Needs entry id or run number.")

parser.add_argument("-i", "--id",	type=str,	default='',
                    help="id of the entry to be adjusted or deleted (pk)")

parser.add_argument("-v", "--verbosity",	type=int, default=envDict['verb'], choices=[0, 1, 2],
                    help="set output verbosity")


args	= parser.parse_args()
server	= args.server
delete	= args.delete
message	= args.message
name	= args.name

s_id	= args.id

verb	= args.verbosity

### p3s interface defined here
API  = serverAPI(server=server, verb=0)

if(delete):
    if(s_id == ''):
        print('ID not specified, exiting')
        exit(-1)

    resp = API.post2server('logic', 'delete', dict(pk=s_id))
    print(resp)
    exit(0)


if(message!='' and name!=''):
    resp = API.post2server('logic', 'service', dict(message=message,name=name))
    print(resp)
    


