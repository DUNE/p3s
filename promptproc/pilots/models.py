from django.db import models


# pilot timestamps:
# created, registered, last heartbeat

class pilot(models.Model):
    uuid	= models.CharField(max_length=36, default='')
    j_uuid	= models.CharField(max_length=36, default='')	# current job id
    jpid	= models.CharField(max_length=16, default='')	# current job pid
    state	= models.CharField(max_length=16, default='')
    status	= models.CharField(max_length=16, default='')
    site	= models.CharField(max_length=32, default='')
    host	= models.CharField(max_length=32, default='')
    ts_cre	= models.DateTimeField('ts_cre',  blank=True, null=True)
    ts_reg	= models.DateTimeField('ts_reg',  blank=True, null=True)
    ts_lhb	= models.DateTimeField('ts_lhb',  blank=True, null=True)
    jobcount	= models.PositiveIntegerField(default=0) # number of processed jobs
    jobs_done	= models.TextField(default='') # uuid's of processed jobs
    pid		= models.CharField(max_length=16, default='')


    # time autofill:
    #    auto_now=True
    
    @classmethod
    def N(self):
        return self.objects.count()
    
    def __str__(self):
        return self.uuid
