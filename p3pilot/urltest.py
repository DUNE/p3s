#!/usr/bin/python

import argparse

import urllib
from urllib import request
from urllib import error
from urllib.error import URLError

#-------------------------
parser = argparse.ArgumentParser()

parser.add_argument("-u", "--url", type=str, default='http://localhost:8000/')
parser.add_argument("-v", "--verbosity", type=int, default=0, choices=[0, 1, 2],
                    help="increase output verbosity")

args = parser.parse_args()

url	= args.url
verb	= args.verbosity

try:
    response = urllib.request.urlopen(url)
except URLError:
    exit(1)
    
    
headers = response.info()
data = response.read()

if(verb >=2):
    print ('RESPONSE:', response)
    print ('URL     :', response.geturl())

    print ('DATE    :', headers['date'])
    print ('HEADERS :')
    print ('---------')
    print (headers)

    print ('LENGTH  :', len(data))
    print ('DATA    :')
    print ('---------')
    
if(verb >0):
    print (data)
    
exit(0)

