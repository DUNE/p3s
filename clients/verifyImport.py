#!/usr/bin/env python3
import importlib
packList = ['django','django_tables2','networkx']
print('Will test import of',len(packList),'modules')
for p in packList:
    try:
        print('Checking',p,'...')
        importlib.import_module(p)
        print('...OK')
    except:
        print('Could not import',p)
    
