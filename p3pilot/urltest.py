#!/usr/bin/python

import urllib
from urllib import request

response = urllib.request.urlopen('http://localhost:8000/')
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
