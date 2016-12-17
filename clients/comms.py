import urllib
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
    return r.read().decode('utf-8')

###################################################################
def communicate(url, data=None, logger=None):
    try:
        if(data):
            return urllib.request.urlopen(url, data)
        else:
            return urllib.request.urlopen(url)
    except URLError:
        if(logger): logger.error('exiting, error at URL: %s' % url)
        exit(1)
###################################################################
def logfail(msg, logger):
    error = ''
    try:
        error	= msg['error'] # if the server told us what the error was, log it
        logger.error('exiting, received FAIL status from server, error:%s' % error)
    except:
        logger.error('exiting, received FAIL status from server, no error returned')
    exit(2)

