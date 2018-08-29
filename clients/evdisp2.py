#!/usr/bin/env python3.5

#########################################################
#                                                       #
# This version of the evdisp client aims to comply      #
# with the filename and other changes in the evdisp     #
# app and also to take advantage of the metadata        #
# feature in the current DQM service (as of Aug 2018).  #
#                                                       #
# As such, its purpose is to generate JSON to feed a    #
# separate (universal) client, the "monrun", which      #
# communicates with the DQM server. For that reason, it #
# differs in functionality from the first version of    #
# the client which was registering files in a dedicated #
# database. Now, all goes into the "monitor" records.   #
#                                                       #
# We rely on parsing of the input file name to          #
# extract vital metadata i.e. the run number, the file  #
# index and the data logger number. Example:            #
#                                                       #
# np04_raw_run003498_0012_dl8.root                      #
#                                                       #
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
summaryDict	= OrderedDict()

########################################################
parser = argparse.ArgumentParser()

parser.add_argument("-a", "--auto",	action='store_true',	help="parse the current directory automatically")
parser.add_argument("-v", "--verbosity",type=int, default=0,	help="output verbosity")
parser.add_argument("-f", "--filename",	type=str,		help="raw data file name e.g. np04_raw_run003498_0012_dl8.root", default='')

args	= parser.parse_args()

auto	= args.auto
verb	= args.verbosity
filename= args.filename

#########################################################
if(auto):
    run	= None
    evt	= None
    L	= sorted(os.listdir("."))

    # Let's extract the run, event numbers
    # Example: np04_raw_run003498_0012_dl8.root                      #
    
    tokens	= filename.split('_')
    
    run		= int(tokens[2][3:])
    idx		= int(tokens[3])
    dl		= int(tokens[4].split('.')[0][2:])

    print("Run:", run, "Idx:", idx, "dl:", dl)
    
    if run is None or idx is None or dl is None:
        print("Could not parse the run parameters, exiting...")
        exit(-1)

    formatted_run	= "run%06d_%04d_dl%02" % (run, idx, dl)
    
    summaryDict['run']	= formatted_run
    summaryDict['Type']	= 'evdisp'

    summaryFile = open(formatted_run+'_summary.json', 'w')
    summaryFile.write(json.dumps([summaryDict], indent=4))
    summaryFile.close()
    
    for k in fileTypes: #    print('KEY----------------->', k)
        files = []
        for f in L:
            if (f.startswith(k) and f.endswith(".png")): files.append(f)
        if (len(files)>0): filesDict[fileTypes[k]] = ",".join(files)
        
    output['Category']	= '2D Event Display'
    output['Files']	= filesDict
    
    fileListFile = open(formatted_run+'_FileList.json', 'w')
    fileListFile.write(json.dumps([output], indent=4))
    fileListFile.close()

exit(0)

#########################################################
# run	= None
# evt	= None
# L	= sorted(os.listdir("."))

# # Let's extract the run, event numbers
# # Example adcraw_tpp0c_run002973_evt000010.png
    
# for f in L:
#     if (f.startswith('adcraw') and f.endswith('.png') and run is None and evt is None):
#         tokens = f.split('_')
#         run = int(tokens[2][3:])
#         evt = int(tokens[3][3:9])
