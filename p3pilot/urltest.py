#!/usr/bin/python

import argparse

import urllib
from urllib import request

#-------------------------
parser = argparse.ArgumentParser()
parser.add_argument("-u", "--url", type=str, default='http://localhost:8000/')
args = parser.parse_args()

url = args.url
print(url)

response = urllib.request.urlopen(url)
print ('RESPONSE:', response)
print ('URL     :', response.geturl())

headers = response.info()
print ('DATE    :', headers['date'])
print ('HEADERS :')
print ('---------')
print (headers)

data = response.read()
print ('LENGTH  :', len(data))
print ('DATA    :')
print ('---------')
print (data)
