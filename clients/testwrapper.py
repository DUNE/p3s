#!/usr/bin/env python3.5

import json
import os
import argparse


################################################################
# The purpose of this script is to allow the user to test
# a combination of their JSON job description and the payload
# (wrapper) script without doing the actual batch submission
# - to save time and effort.
#
# The script will try to see if the env variable "P3S_INPUT_FILE"
# is set. It will then see if it's overwritten by supplying the
# "-f" option on the command line. If one of the two are present,
# it will in turn try to overwrite what's in the original
# JSON file as part of the environment.
#
# All of the above is meant to give the user more flexibility
# of running same program with different inputs without having
# to edit scirpts and JSON
################################################################


#####

inputOverride = None
outputOverride = None

try:
    inputOverride = os.environ['P3S_INPUT_FILE']
except:
    pass

try:
    outputOverride = os.environ['P3S_OUTPUT_FILE']
except:
    pass

#####

parser = argparse.ArgumentParser()

parser.add_argument("-j", "--json_in",	type=str, default='',	help="file from which to read the job (must be a list)")
parser.add_argument("-f", "--file",	type=str, default=None,	help="input file, overrides the value in json file")
parser.add_argument("-F", "--File",	type=str, default=None,	help="output file, overrides the value in json file")
parser.add_argument("-p", "--payload",	type=str, default=None,	help="payload, overrides the value in json file")

args = parser.parse_args()

j = args.json_in
f = args.file
F = args.File
p = args.payload

if(f): inputOverride=f
if(F): outputOverride=F

if(j==''):
    print('JSON input not defined, exiting... Use -h option for help')
    exit(-1)

data = None
with open(j) as data_file:    
    data = json.load(data_file)[0]



print("JOB ENVIRONMENT\n--------------------------")

for k in data['env'].keys():
    os.environ[k]=data['env'][k]
    print(k+'='+data['env'][k])

if(inputOverride):
    os.environ['P3S_INPUT_FILE']=inputOverride
    print('Input Override:',os.environ['P3S_INPUT_FILE'])

if(outputOverride):
    os.environ['P3S_OUTPUT_FILE']=outputOverride
    print('Output Override:',os.environ['P3S_OUTPUT_FILE'])


print("--------------------------")
    
pl=data['payload']
if(p): pl=p


print("PAYLOAD\n--------------------------")
print(pl)
print("--------------------------")

os.system(pl)
