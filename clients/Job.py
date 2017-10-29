from django.utils	import timezone
import uuid
import socket
import os
import json

class Job(dict):
    def __init__(self,
                 json_in={},
                 name='',
                 priority=0,
                 jobtype='default',
                 payload='/bin/true',
                 env='',
                 state='defined'):
        
        self['name']	= name
        self['user']	= os.environ['USER']
        self['uuid']	= str(uuid.uuid1())
        self['jobtype']	= jobtype
        self['payload']	= payload
        self['env']	= env
        self['priority']= priority
        self['state']	= state
        self['subhost']	= socket.gethostname() # submission host
        self['ts']	= str(timezone.now()) # see TZ note on top

        for k in json_in.keys():
            if isinstance(json_in[k], dict):
                self[k] = json.dumps(json_in[k])
            else:
                self[k] = json_in[k]

