#!/usr/bin/env python3.5
import argparse
import json
import os

from serverAPI import serverAPI
from clientenv import clientenv

(user, server, verb, site) = clientenv()

parser = argparse.ArgumentParser()

parser.add_argument("-j", "--json_in",	type=str,	default='',
                    help="file or a string from which to read purge policy")

args = parser.parse_args()
json_in	= args.json_in

if(json_in==''): exit(-1)

f = None
data = None

if('.json' in json_in):
    try:
        f = open(json_in)
    except:
        exit(-2)
        
    try:
        data = json.load(f)
    except:
        exit(-3)
else:
    try:
        data = json.load(json_in)
    except:
        exit(-4)


print(data)


