import urllib
from urllib		import request
from urllib		import error
from urllib.error	import URLError

import logging

###################################################################
# Just want to encapsulate some voodoo which encodes a dictionary #
# in UTF-8, as is customary                                       #
###################################################################
class data2post():
    def __init__(self, myDict):
        encoding = urllib.parse.urlencode(myDict)
        encoding = encoding.encode('UTF-8')
        self.packaged = encoding

    def utf8(self):
        return self.packaged

    def __str__(self):
        return self.packaged
###################################################################
def rdec(r):
    decoded=''
    try:
        decoded=r.read().decode('utf-8')
    except:
        decoded=r
    return decoded

###################################################################
def communicate(url, data=None, logger=None, verb=0):
    if(data):
        if(logger): logger.info('POST URL: %s' % url)
    else:
        if(logger): logger.info('GET URL: %s' % url)

    if(verb>0):
        print(url)
        if(data): print(data)
        
    try:
        resp=''
        if(data):
            resp=urllib.request.urlopen(url, data)
        else:
            resp=urllib.request.urlopen(url)
        return resp
    except URLError:
        errMsg = 'Exiting: error at URL: %s' % url
        if(logger): logger.error(errMsg)
        return (errMsg)
###################################################################
