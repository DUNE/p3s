from django.utils	import timezone
import uuid
import socket
import os
class Pilot(dict):
    def __init__(self, jobcount=0, cycles=1, period=5, site='default', extra=''):
        self['state']	= 'active' # start as active
        self['status']	= '' # status of server comms
        self['host']	= socket.gethostname()
        self['site']	= site
        self['ts']	= str(timezone.now())
        self['uuid']	= uuid.uuid1()
        self['event']	= '' # what just happned in the pilot
        self['jobcount']= jobcount
        self.cycles	= cycles
        self.period	= period
        self.job	= '' # job uuid (to be yet received)
        self['jpid']	= '' # ditto
        self['errcode']	= '' # ditto
        self['extra']	= extra
        self['pid']	= os.getpid()

