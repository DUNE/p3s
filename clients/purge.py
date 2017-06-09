#!/usr/bin/env python3.5
import argparse
import json
import os

from serverAPI import serverAPI
from clientenv import clientenv

(user, server, verb, site) = clientenv()

### p3s interface defined here
API  = serverAPI(server=server, verb=0)

parser = argparse.ArgumentParser()

parser.add_argument("-j", "--json_in",	type=str,	default='',
                    help="file or a string from which to read purge policy")

args = parser.parse_args()
json_in	= args.json_in

if(json_in==''): exit(-1)

f = None
data = None

if('.json' in json_in):
    try:
        f = open(json_in)
    except:
        exit(-2)
        
    try:
        data = json.load(f)
    except:
        exit(-3)
else:
    try:
        data = json.loads(json_in)
    except:
        exit(-4)


for d in data:
    what = list(d.keys())[0]
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
    resp = API.post2server('logic', 'purge', dict(interval=interval, timestamp=timestamp, state=state, what=what))
    print(resp)
    


