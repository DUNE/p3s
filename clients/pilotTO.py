#!/usr/bin/env python3.5

import argparse
import json
import os

from serverAPI import serverAPI
from clientenv import clientenv

(user, server, verb, site, pl, jl) = clientenv()

### p3s interface defined here
API  = serverAPI(server=server, verb=0)

parser = argparse.ArgumentParser()

parser.add_argument("-j", "--json_in",	type=str,	default='',
                    help="required: file or a string from which to read purge policy")


parser.add_argument("-t", "--test",	action='store_true',
                    help="when set, parses input but does not contact the server")


args	= parser.parse_args()
json_in	= args.json_in
tst	= args.test

if(json_in==''): exit(-1)


f = None
data = None

if('.json' in json_in): # assume it's a file
    try:
        f = open(json_in)
        print('opened file')
    except:
        exit(-2)
        
    try:
        data = json.load(f)
        print('parsed data', data)
    except:
        exit(-3)
else: # assume it's a string on the command line
    try:
        data = json.loads(json_in)
    except:
        exit(-4)


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
    
    # print(state,status,'*',timestamp,'*',interval)
    if(tst):
        pass
    else:
        resp = API.post2server('logic', 'purge', dict(interval=interval, timestamp=timestamp, state=state, what=what))
        
    print(resp)
    


