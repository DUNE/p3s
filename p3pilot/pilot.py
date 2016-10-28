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

parser.add_argument("-s", "--server",
                    type=str,
                    default='http://localhost:8000/',
                    help="the server address, defaults to http://localhost:8000/")

parser.add_argument("-u", "--url",
                    type=str,
                    default='',
                    help="url of the query to be added, defaults to empty string")

parser.add_argument("-t", "--test",
                    action='store_true',
                    help="when set, forms a request but does not contact the server")

parser.add_argument("-r", "--register",
                    action='store_true',
                    help="when set, the pilot will attempt to register with the server")

parser.add_argument("-v", "--verbosity",
                    type=int,
                    default=0, choices=[0, 1, 2],
                    help="increase output verbosity")

args = parser.parse_args()

server	= args.server
url	= args.url
verb	= args.verbosity

# Boolean
tst	= args.test
register= args.register

print(register) 
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
    if(register):
        response = urllib.request.urlopen(server+url, pilotData)
    else:
        response = urllib.request.urlopen(server+url)
        
except URLError:
    exit(1)
    
    
headers		= response.info()
data		= response.read()

response_url	= response.geturl()
response_date	= headers['date']

if(verb >0):
    print (data)
    
exit(0)

