#!/usr/bin/env python3.5
import argparse
import json

from serverAPI import serverAPI
from clientenv import clientenv

#########################################################################        
#############################  BEGIN  ###################################

(user, server, verb, site) = clientenv()


parser = argparse.ArgumentParser()

parser.add_argument("-S", "--server",	type=str,	default=server,
                    help="the server address, defaults to $P3S_SERVER or if unset to http://localhost:8000/")


########################### Parse all arguments #########################
args = parser.parse_args()

server =  args.server

API  = serverAPI(server=server)
resp = API.get2server('info','dash', '?out=json')
info = json.loads(resp)


print("Domain: %s, hostname %s, uptime %s" % (info['domain'], info['hostname'], info['uptime']))

print("Pilots: total %s, idle %s, running %s, stopped %s" %
      (info['pilots']['data'][0], info['pilots']['data'][1], info['pilots']['data'][2], info['pilots']['data'][3]))

print("Jobs: total %s, defined %s, running %s, finished %s" %
      (info['jobs']['data'][0],   info['jobs']['data'][1],   info['jobs']['data'][2],   info['jobs']['data'][3]))


print("Workflows %s" % info['workflows']['data'][0])

print("Datasets %s" % info['datasets']['data'][0])
