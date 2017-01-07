from django.db import models

from data.models	import dataset, datatype
from jobs.models	import job

class manager(object):
    def __init__(self):
        self.x = 0
 
    @classmethod
    def childrenStateToggle(cls,j, state):
        for edge in dataset.objects.filter(sourceuuid=j.uuid):
            for child in job.objects.filter(uuid=edge.targetuuid):
                if(child.jobtype=='noop'):
                    child.state='finished'
                else:
                    child.state = state
                child.save()
