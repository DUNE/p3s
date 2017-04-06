from django.db import models

from data.models	import dataset, datatype
from jobs.models	import job

class manager(object):
    def __init__(self):
        self.x = 0
 
    @classmethod
    def childrenStateToggle(cls, j, state):
        ndone = 0
        # traverse the edges originating in the job 'uuid'
        for edge in dataset.objects.filter(sourceuuid=j.uuid):
            # for each such edge find verices where it terminates
            for child in job.objects.filter(uuid=edge.targetuuid):
                if(child.jobtype=='noop'): # dummy job, automatically tagged complete
                    child.state='finished'
                    ndone+=1
                else:
                    child.state = state
                child.save()
        return ndone
