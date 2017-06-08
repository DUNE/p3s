#!/usr/bin/env python3.5

import json
import os
import argparse


parser = argparse.ArgumentParser()

parser.add_argument("-j", "--json_in",	type=str,	default='',
                    help="file from which to read the job (must be enclosed in p[])")

args = parser.parse_args()

j = args.json_in

if(j==''): exit(-1)

data = None
with open(j) as data_file:    
    data = json.load(data_file)[0]



print("JOB ENVIRONMENT\n--------------------------")

for k in data['env'].keys():
    os.environ[k]=data['env'][k]
    print(k+'='+data['env'][k])

print("--------------------------")
    
pl=data['payload']
print("PAYLOAD\n--------------------------")
print(pl)
print("--------------------------")

os.system(pl)
