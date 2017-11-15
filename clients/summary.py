#!/usr/bin/env python3.5
import argparse
import json

from serverAPI import serverAPI
from clientenv import clientenv

#########################################################################        
#############################  BEGIN  ###################################

envDict = clientenv(outputDict=True) # Will need 'server' only

parser = argparse.ArgumentParser()

parser.add_argument("-S", "--server",	type=str,	default=envDict['server'],
                    help="the server address, defaults to $P3S_SERVER or if unset to http://localhost:8000/")

parser.add_argument("-P", "--print",	action='store_true',
                    help="when set, prints a p3s summary in human-readable text format")

parser.add_argument("-p", "--pilotsActive",	action='store_true',
                    help="get the number of active pilots (running+idle)")

########################### Parse all arguments #########################
args = parser.parse_args()

server	= args.server
p	= args.print
pa	= args.pilotsActive

API  = serverAPI(server=server)

if(pa):
    N = API.get2server('info','pilotinfo','')
    print(N)
    exit(0)


resp = API.get2server('info','dash', '?out=json')
info = json.loads(resp)


if(p):
    print("Domain: %s, hostname %s, uptime %s" % (info['domain'], info['host'], info['uptime']))
    print("Pilots: total %s, idle %s, running %s, stopped %s, TO %s"  %
          (info['pilots']['data'][0],
           info['pilots']['data'][1],
           info['pilots']['data'][2],
           info['pilots']['data'][3],
           info['pilots']['data'][4]
          ))

    print("Jobs: total %s, defined %s, running %s, finished %s, pilotTO %s" %
          (info['jobs']['data'][0],
           info['jobs']['data'][1],
           info['jobs']['data'][2],
           info['jobs']['data'][3],
           info['jobs']['data'][4],
          ))


    print("Workflows %s" % info['workflows']['data'][0])
    print("Datasets %s" % info['datasets']['data'][0])


#if(pa):- this doesn't work well since there is also a 'finished' state
#    N = int(info['pilots']['data'][1])+int(info['pilots']['data'][2])
#    print(N)
    
