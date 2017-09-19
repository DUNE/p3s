#!/usr/bin/env python3.5
#########################################################
# TZ-awarewness:					#
# The following is not TZ-aware: datetime.datetime.now()#
# so we are using timzone.now() where needed		#
#########################################################

from django.conf import settings
from django.utils import timezone

import argparse
import uuid
import socket
import time
import datetime
import json
import csv

import os

from serverAPI import serverAPI
from clientenv import clientenv


#########################################################
settings.configure(USE_TZ = True)

user		= os.environ['USER']
envDict = clientenv(outputDict=True) # Will need ('server', 'verb'):
parser = argparse.ArgumentParser()

print('test')

parser.add_argument("-f", "--file",	type=str,	help="input file", default='')

args = parser.parse_args()
filename = args.file
f = None

try:
    f = open(filename,"r")
except:
    print("file '%s' not found." % filename)
    exit(-1)
    
#l = f.readline()
#while(l):
#    print(l)
#    l = f.readline()
    
myreader = csv.reader(f, delimiter=' ', quotechar='|')
frst = True
for row in myreader:
    if(frst):
        frst = False
        continue # skip Bruce's header
    for e in row:
        e = e.replace(',', '')
        print(e)
    print(row)
