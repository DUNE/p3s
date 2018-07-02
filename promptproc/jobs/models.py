import json
import datetime
from datetime		import timedelta

from django.db		import models
from django.core	import serializers
from django.utils	import timezone

########################################################################
class job(models.Model):
    uuid	= models.CharField(max_length=36, default='')
    user	= models.CharField(max_length=64, default='')		# who submitted the job
    site	= models.CharField(max_length=32, default='')
    host	= models.CharField(max_length=32, default='')
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
    ts_sto	= models.DateTimeField('ts_sto', blank=True, null=True) # stop
    env		= models.TextField(default='{}')			# optional - env for the job
    pid		= models.CharField(max_length=16, default='')
    errcode	= models.CharField(max_length=16, default='')		#
    directive	= models.CharField(max_length=16, default='')		# for future development

    # ---
    def __str__(self):
        return serializers.serialize("json", [self, ])
   
    # ---
    def augmentEnv(self, d):# add to the existing job environment from the dictionary provided
        self.env = json.dumps({**json.loads(self.env), **d})

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
    def timeline(self, timestamp, seconds, state=None):
        cutoff = timezone.now() - timedelta(seconds=seconds)
        kwargs = {'{0}__{1}'.format(timestamp, 'gte'): str(cutoff),}
        if(state):
            if(state=='error'):
                cnt=0
                for o in self.objects.filter(**kwargs):
                    if(o.errcode!='' and int(o.errcode)!=0): cnt+=1
                return cnt
            else:
                return self.objects.filter(**kwargs).filter(state=state).count()
        else:
            return self.objects.filter(**kwargs).count()

 
###############################################################################    
class jobtype(models.Model):
    name	= models.CharField(max_length=32, default='')
    priority	= models.PositiveIntegerField(default=0)
    njobs	= models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.name

# ---
# The priority policy
class prioritypolicy(models.Model):
    name	= models.CharField(max_length=32, default='')
    value	= models.CharField(max_length=32, default='')
    
    def __str__(self):
        return self.name

   
    # @classmethod
    # def Nrun(self):
    #     return self.objects.filter(state='running').count()
    
    # @classmethod
    # def Nfin(self):
    #     return self.objects.filter(state='finished').count()
    
    # @classmethod
    # def Ndef(self):
    #     return self.objects.filter(state='defined').count()

