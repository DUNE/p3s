from django.db import models


# pilot timestamps:
# created, registered, last heartbeat

class pilot(models.Model):
    uuid	= models.CharField(max_length=36, default='')
    j_uuid	= models.CharField(max_length=36, default='')	# unique job id
    jpid	= models.CharField(max_length=16, default='')	# the job pid
    state	= models.CharField(max_length=16, default='')
    status	= models.CharField(max_length=16, default='')
    site	= models.CharField(max_length=32, default='')
    host	= models.CharField(max_length=32, default='')
    ts_cre	= models.DateTimeField('ts_cre',  blank=True, null=True)
    ts_reg	= models.DateTimeField('ts_reg',  blank=True, null=True)
    ts_lhb	= models.DateTimeField('ts_lhb',  blank=True, null=True)
    jobcount	= models.PositiveIntegerField(default=0) # number of jobs processed by this pilot
    jobs_done	= models.TextField(default='') # csv list - uuid's of processed jobs
    pid		= models.CharField(max_length=16, default='')
    extra	= models.CharField(max_length=256, default='')	# extra info (e.g. batch ID)


    # time autofill:
    #    auto_now=True
    
# ---    
    @classmethod
    def N(self, state=None, site=None):
        if(site):
            if(state):
                return self.objects.filter(site=site).filter(state=state).count()
            else:
                return self.objects.filter(site=site).count()
        else:
            if(state):
                if(state=='Total'): return self.objects.count()
                return self.objects.filter(state=state).count()
            else:
                return self.objects.count()
# ---
    @classmethod
    def jobsDone(self):
        cnt=0
        for p in self.objects.all():
            cnt+=p.jobcount
        return cnt
            
    
    def __str__(self):
        return self.uuid
