#!/usr/bin/python

'''This is a stub for the p3s pilot'''
#!/usr/bin/python

import argparse
import uuid
import socket

import urllib
from urllib import request
from urllib import error
from urllib import parse

from urllib.error import URLError

#-------------------------
parser = argparse.ArgumentParser()

parser.add_argument("-u", "--url",
                    type=str,
                    default='http://localhost:8000/',
                    help="url of the server, defaults to http://localhost:8000/")

parser.add_argument("-t", "--test",
                    action='store_true',
                    help="when set, forms a request but does not contact the server")

parser.add_argument("-v", "--verbosity",
                    type=int,
                    default=0, choices=[0, 1, 2],
                    help="increase output verbosity")

args = parser.parse_args()

url	= args.url
verb	= args.verbosity
tst	= args.test

print(tst) 
pilotID = uuid.uuid1()
print(pilotID)
host = socket.gethostname()
print(host)

pilotData = urllib.parse.urlencode({'uuid' : pilotID, 'host' : host})
pilotData = pilotData.encode('UTF-8')

print(pilotData)

if(tst):
    exit(0)

try:
    response = urllib.request.urlopen(url)
except URLError:
    exit(1)
    
    
headers		= response.info()
data		= response.read()

response_url	= response.geturl()
response_date	= headers['date']

if(verb >0):
    print (data)
    
exit(0)

