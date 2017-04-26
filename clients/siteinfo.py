#!/usr/bin/env python3.5
#########################################################
# TZ-awarewness:					#
# The following is not TZ-aware: datetime.datetime.now()#
# so we are using timzone.now() where needed		#
#########################################################
# Please disregard bits of code "left for later" - most #
# will be used for future development                   #
#########################################################

from django.conf	import settings
from django.utils	import timezone

import argparse
import uuid
import socket
import time
import datetime
import logging
import json
import os

import networkx as nx

from serverAPI import serverAPI
from clientenv import clientenv

settings.configure(USE_TZ = True)

(user, server, verb, site) = clientenv()

host		= socket.gethostname()

parser = argparse.ArgumentParser()

parser.add_argument("-S", "--server",	type=str,
                    help='server URL: defaults to $P3S_SERVER or if unset to '+server,
                    default=server)

parser.add_argument("-v", "--verbosity",type=int,	default=verb, choices=[0, 1, 2], help="set verbosity - also needed for data output.")

parser.add_argument("-s", "--site",	type=str,	default='', help='''site info in JSON format,
will be intrepreted as a JSON file name if contains .json''')


########################### Parse all arguments #########################
args = parser.parse_args()

server	= args.server
verb	= args.verbosity
site	= args.site

if(site!=''):

    f = None
    if('.json' in site):
        try:
            f = open(site, 'r')
            content = f.read()
            f.close()
            if(verb>1): print(content)
            site = content
        except:
            print('Problems reading input file %s' % site)
            exit(-1)


    print('Site:', site)
    #resp = API.post2server('workflow', 'addwfURL', {'site':site})
    
    #if(verb>1): print (resp)
    exit(0)

###################### GRAND FINALE ####################################
exit(0)
