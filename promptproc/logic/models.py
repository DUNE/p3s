from django.db		import models
from django.utils	import timezone

from data.models	import dataset, datatype
from jobs.models	import job



class user(models.Model):
    name	= models.CharField(max_length=64, primary_key = True, default='')

    def __str__(self):
        return self.name

    @classmethod
    def all(self):
        allUsers=[]
        for u in user.objects.all():
            allUsers.append(u.name)
        return ", ".join(allUsers)

class service(models.Model):
    name	= models.CharField(max_length=32, default='')
    ts		= models.DateTimeField('ts',  blank=True, null=True)
    info	= models.TextField(default='')



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
                    t = timezone.now()
                    child.ts_dis	= t
                    child.ts_sta	= t
                    child.ts_sto	= t
                    child.state		='finished'
                    ndone+=1
                else:
                    child.state = state
                child.save()
        return ndone
