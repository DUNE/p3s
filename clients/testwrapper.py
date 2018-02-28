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

inputOverride	= None
outputOverride	= None
fclOverride	= None

try:
    inputOverride = os.environ['P3S_INPUT_FILE']
except:
    pass

try:
    outputOverride = os.environ['P3S_OUTPUT_FILE']
except:
    pass

try:
    fclOverride = os.environ['P3S_FCL']
except:
    pass

#####

parser = argparse.ArgumentParser()

parser.add_argument("-j", "--json_in",	type=str, default='',	help="JSON file from which to read the job description (must be a list)")
parser.add_argument("-i", "--infile",	type=str, default=None,	help="overrides the value of P3S_INPUT_FILE in json file")
parser.add_argument("-o", "--outfile",	type=str, default=None,	help="overrides the value of P3S_OUTPUT_FILE in json file")
parser.add_argument("-p", "--payload",	type=str, default=None,	help="overrides the value of payload in JSON file")

parser.add_argument("-f", "--fcl",	type=str, default=None,	help="FCL, overrides the value of P3S_FCL in json file")

args = parser.parse_args()

j	= args.json_in
ifile	= args.infile
ofile	= args.outfile
pay	= args.payload
fcl	= args.fcl

if(ifile):	inputOverride=ifile
if(ofile):	outputOverride=ofile

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

if(fclOverride):
    os.environ['P3S_FCL']=fclOverride
    print('Fcl Override:',os.environ['P3S_FCL'])


print("--------------------------")
    
pl=data['payload']
if(pay): pl=pay


print("PAYLOAD\n--------------------------")
print(pl)
print("--------------------------")

os.system(pl)
