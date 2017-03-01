import json
from django.db		import models

class job(models.Model):
    uuid	= models.CharField(max_length=36, default='')
    name	= models.CharField(max_length=64, default='')		# human-readable
    p_uuid	= models.CharField(max_length=36, default='')		# pilot uuid
    wfuuid	= models.CharField(max_length=36, default='')		# workflow uuid
    jobtype	= models.CharField(max_length=16, default='')		#
    payload	= models.CharField(max_length=256,default='')		# provisional, url/path
    params	= models.CharField(max_length=256,default='')		# cmd line args
    priority	= models.PositiveIntegerField(default=0)		# higher wins
    timelimit	= models.PositiveIntegerField(default=1000)		# in seconds
    state	= models.CharField(max_length=16, default='')		# e.g. 'running'
    ts_def	= models.DateTimeField('ts_def', blank=True, null=True)	# definition
    ts_dis	= models.DateTimeField('ts_dis', blank=True, null=True)	# dispatch
    ts_sta	= models.DateTimeField('ts_sta', blank=True, null=True)	# start
    ts_sto	= models.DateTimeField('ts_sto', blank=True, null=True)	# optional - env for the job
    env		= models.TextField(default='{}')

    def __str__(self):
        return self.uuid

    
    def augmentEnv(self, d):# add to the existing job environment from the dictionary provided
        self.env = json.dumps({**json.loads(self.env), **d})

    @classmethod
    def N(self):
        return self.objects.count()
    
class jobtype(models.Model):
    name	= models.CharField(max_length=32, default='')
    priority	= models.PositiveIntegerField(default=0)
    njobs	= models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.name
    
# The priority policy
class prioritypolicy(models.Model):
    name	= models.CharField(max_length=32, default='')
    value	= models.CharField(max_length=32, default='')
    
    def __str__(self):
        return self.name

