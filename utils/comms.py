import urllib
class data2post():
    def __init__(self, myDict):
        encoding = urllib.parse.urlencode(myDict)
        encoding = encoding.encode('UTF-8')
        self.packaged = encoding

    def utf8(self):
        return self.packaged
