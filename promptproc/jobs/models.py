from django.db import models

# The job class. Jobs belong to stages
class job(models.Model):
    uuid	= models.CharField(max_length=36, default='')
    p_uuid	= models.CharField(max_length=36, default='')
    stage	= models.CharField(max_length=16, default='')
    priority	= models.PositiveIntegerField(default=0)
    state	= models.CharField(max_length=16, default='')
    ts_def	= models.DateTimeField('ts_def', blank=True, null=True)
    ts_dis	= models.DateTimeField('ts_dis', blank=True, null=True)
    ts_sta	= models.DateTimeField('ts_sta', blank=True, null=True)
    ts_sto	= models.DateTimeField('ts_sto', blank=True, null=True)

    def __str__(self):
        return self.uuid
#    

class stage(models.Model):
    name	= models.CharField(max_length=32, default='')
    priority	= models.PositiveIntegerField(default=0)
    njobs	= models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.name
    
