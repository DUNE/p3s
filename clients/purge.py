#!/usr/bin/env python3.5

import argparse
import json
import os

from serverAPI import serverAPI
from clientenv import clientenv
from clientUtils import takeJson

(user, server, verb, site, pl, jl) = clientenv()

# will push to git on Jan 15
envDict = clientenv(outputDict=True) # Will need ('server', 'verb'):

parser = argparse.ArgumentParser()

parser.add_argument("-v", "--verbosity",type=int,	default=envDict['verb'], choices=[0, 1, 2], help="verbosity")

parser.add_argument("-j", "--json_in",	type=str,	default='',
                    help="*FUTURE DEVELOPMENT* file or a string from which to read purge policy")

parser.add_argument("-S", "--server",	type=str,	default=envDict['server'],
                    help='server URL: defaults to $P3S_SERVER or if unset to '+envDict['server'])

parser.add_argument("-w", "--what",	type=str,	default='pilot',
                    help="what to purge, defaults to pilot")

parser.add_argument("-s", "--state",	type=str,	default='stopped',
                    help="state of objects to purge, defaults to stopped")


parser.add_argument("-t", "--test",	action='store_true', help="parse input but do not contact the server")

parser.add_argument("-d", "--direct",	action='store_true', help="direct logging in the internal server DB")


args	= parser.parse_args()
json_in	= args.json_in
tst	= args.test
server	= args.server
verb	= args.verbosity

state	= args.state
what	= args.what

tst	= args.test
direct	= args.direct



### p3s interface defined here
API  = serverAPI(server=server, verb=verb)

d = dict(state=state, what=what)
if(direct): d['direct']='True'
resp = API.post2server('logic', 'purge', d)
        
if(resp!=''): print(resp)

exit(0)

##################################################################################
# What's below is kept for future development

if(json_in==''): exit(-1)


f = None
data = None

data = takeJson(json_in)


print(data)
print(list(data.keys()))
for what in data.keys():
    print(what)
    print('!')
    
    if(what=='pilot'):
        print('pilot')
        if(tst):
            pass
        else:
            resp = API.post2server('logic', 'pilotTO', dict(interval=interval, timestamp=timestamp, state=state, what=what))
            print(resp)
        exit(0)
    else:
        exit(-1)


        
    (state, status, timestamp, interval) = ('','','','')
    try:
        state = d[what]['state']
    except:
        pass
    
    try:
        status = d[what]['status']
    except:
        pass
    
    try:
        timestamp = d[what]['timestamp']
    except:
        pass
    
    try:
        interval = d[what]['interval']
    except:
        pass
    
    if(tst):
        print(state,status,'*',timestamp,'*',interval)
        exit(0)
    else:
        resp = API.post2server('logic', 'purge', dict(interval=interval, timestamp=timestamp, state=state, what=what))
        
    print(resp)
    


