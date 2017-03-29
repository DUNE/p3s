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
    return r

###################################################################
def communicate(url, data=None, logger=None):
    try:
        resp=''
        if(data):
            resp=urllib.request.urlopen(url, data)
        else:
            resp=urllib.request.urlopen(url)
        return resp
    except URLError:
        if(logger): logger.error('exiting, error at URL: %s' % url)
        return 'ERROR'
###################################################################
def logfail(msg, logger):
    error = ''
    try:
        error	= msg['error'] # if the server told us what the error was, log it
        logger.error('exiting, received FAIL status from server, error:%s' % error)
    except:
        logger.error('exiting, received FAIL status from server, no error returned')
    exit(2)

