#!/usr/bin/env python3.5

import json
import os
import argparse


#####
inputOverride = None

try:
    inputOverride = os.environ['P3S_INPUT_FILE']
except:
    pass
#####

parser = argparse.ArgumentParser()

parser.add_argument("-j", "--json_in", type=str, default='', help="file from which to read the job (must be a list)")
parser.add_argument("-f", "--file", type=str, default=None, help="input file, overrides the value in json file")

args = parser.parse_args()

j = args.json_in
f = args.file

if(f): inputOverride=f

if(j==''): exit(-1)

data = None
with open(j) as data_file:    
    data = json.load(data_file)[0]



print("JOB ENVIRONMENT\n--------------------------")

for k in data['env'].keys():
    os.environ[k]=data['env'][k]
    print(k+'='+data['env'][k])

if(inputOverride):
    os.environ['P3S_INPUT_FILE']=inputOverride
    print('Override:',os.environ['P3S_INPUT_FILE'])


print("--------------------------")
    
pl=data['payload']
print("PAYLOAD\n--------------------------")
print(pl)
print("--------------------------")

os.system(pl)
