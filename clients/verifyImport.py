#!/usr/bin/env python3.5
import importlib
import argparse
import sys

parser = argparse.ArgumentParser()

parser.add_argument("-s", "--server",
                    action='store_true',
                    help="check import for server (default is for client)")

args = parser.parse_args()
server	= args.server

if(server):
    packList = ['django','django_tables2','networkx']
else:
    packList = ['django','networkx']

#-------------------------------------------------
sv=sys.version
if (sv>'3.5'):
    print("You have compatible Python version:")
    print(sv)
else:
    print("You have incompatible Python version:"+sv)
    print("Exiting...")
    exit(-1)

    
print('---\nWill test import of',len(packList),'modules')

for p in packList:
    try:
        print('Checking',p,'...')
        importlib.import_module(p)
        print('...OK')
    except:
        print('Could not import',p)
        print("Exiting...")
        exit(-1)
        
print("---\nSuccess")    
exit(0)
