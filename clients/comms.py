import urllib

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
