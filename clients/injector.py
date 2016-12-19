#!/usr/bin/env python3
#########################################################
# TZ-awarewness:					#
# The following is not TZ-aware: datetime.datetime.now()#
# so we are using timzone.now() where needed		#
#########################################################
# General Python:
import os
import argparse
import uuid
import socket
import time
import datetime
import logging
import json
import subprocess

# Django
from django.conf	import settings
from django.utils	import timezone

# local import (utils)
from comms import data2post, rdec, communicate, logfail
from serverURL import serverURL
#########################################################
settings.configure(USE_TZ = True) # see the above note on TZ

logdefault	= '/tmp/p3s/injector.log'
datadir		= '/home/maxim/p3sdata'
Usage		= '''Usage:

For command line options run the injector with "--help" option.

'''
#########################################################################

parser = argparse.ArgumentParser()

parser.add_argument("-S", "--server",	type=str,	default='http://localhost:8000/',
                    help="the server address, defaults to http://localhost:8000/")

parser.add_argument("-U", "--usage",	action='store_true',
                    help="print usage notes and exit")

parser.add_argument("-l", "--logdir",	type=str,	default=logdefault,
                    help="(defaults to "+logdefault+") the path for all pilots keep their logs etc")

parser.add_argument("-t", "--test",	action='store_true',
                    help="when set, forms a request but does not contact the server")

parser.add_argument("-v", "--verbosity",	type=int,
                    default=0, choices=[0, 1, 2],
                    help="increase output verbosity")

parser.add_argument("-c", "--cycles",	type=int,	default=1,
                    help="how many cycles (with period in seconds) to stay alive")

parser.add_argument("-p", "--period",	type=int,	default=5,
                    help="period of the pilot cycle, in seconds")

parser.add_argument("-d", "--delete",	action='store_true',
                    help="deletes a pilot (for dev purposes). Needs uuid.")

parser.add_argument("-u", "--uuid",	type=str,	default='',
                    help="uuid of the pilot to be modified")

########################### Parse all arguments #########################
args = parser.parse_args()

# strings
server	= args.server
logdir	= args.logdir

# misc
verb	= args.verbosity
delete	= args.delete
p_uuid	= args.uuid
usage	= args.usage

# scheduling
period	= args.period
cycles	= args.cycles

# testing (pre-emptive exit with print)
tst	= args.test

URLs = serverURL(server=server)

###################### USAGE REQUESTED? ################################
if(usage):
    print(Usage)
    exit(0)

