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

(user, server, verb, site, pl, jl) = clientenv()

myhost = socket.gethostname()

### p3s interface defined here
API  = serverAPI(server=server, verb=0)

parser = argparse.ArgumentParser()

parser.add_argument("-t", "--timeout",	type=int,	default=600,
                    help="pilot timeout in seconds, default 600")


parser.add_argument("-T", "--test",	action='store_true',
                    help="when set, parses input but does not contact the server")


args	= parser.parse_args()
to	= args.timeout
tst	= args.test


if(tst):
    pass
else:
    resp = API.post2server('logic', 'pilotTO', dict(to=to, host=myhost))
    print(resp)
    


