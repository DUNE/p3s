#!/usr/bin/env python3.5

#########################################################
# This version of the evdispl client aims to comply     #
# with the filename and other changes in the evdisp     #
# app and also to take advantage of the metadata        #
# feature in the current DQM service (as of Aug 2018).  #
#                                                       #
# As such, its purpose is to generate JSON to feed a    #
# separate (universal) client, the "monrun"             #
#########################################################


#########################################################
# TZ-awarewness:					#
# The following is not TZ-aware: datetime.datetime.now()#
# so we are using timezone.now() where needed		#
#########################################################

from django.conf	import settings
from django.utils	import timezone

import argparse
import uuid
import socket
import time
import datetime
import json
import csv

import os

from collections import OrderedDict

from serverAPI		import serverAPI
from clientenv		import clientenv
from clientUtils	import takeJson

########################################################
fileTypes = OrderedDict([
    ('adcraw_tpp',		'Raw ADC - pedestal channel vs. tick'),
    ('chmet_ped_tps',		'ADC Pedestals'),
    ('chmet_pedexc_tps',	'ADC pedestal peak bin excess'),
    ('chmet_pedorf_tps',	'ADC pedestal out-of-range fraction'),
    ('chmet_pedrms_tps',	'ADC pedestal sigma'),
    ('detprep-',		'Raw ADC detector display (Collection View)'),
])

# ---
output		= OrderedDict()
filesDict	= OrderedDict()

########################################################
parser = argparse.ArgumentParser()

parser.add_argument("-a", "--auto", action='store_true', help="parse the current directory automatically")
parser.add_argument("-v", "--verbosity", type=int, default=0, help="output verbosity")

args	= parser.parse_args()

auto	= args.auto
verb	= args.verbosity

#########################################################
if(auto):
    output['Category']	= '2D Event Display'
    L = sorted(os.listdir("."))
    for k in fileTypes: #    print('KEY----------------->', k)
        files = []
        for f in L:
            if (f.startswith(k) and f.endswith(".png")): files.append(f)
        if (len(files)>0): filesDict[fileTypes[k]] = ",".join(files)
        
    output['Files']	= filesDict
    print(json.dumps([output]))
exit(0)

#########################################################
