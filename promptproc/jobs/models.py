from django.db import models

# The job class. Jobs belong to stages
class job(models.Model):
    uuid	= models.CharField(max_length=36, default='')
    stage	= models.CharField(max_length=16, default='')
    priority	= models.PositiveIntegerField(default=0)
    state	= models.CharField(max_length=16, default='')
    ts_def	= models.DateTimeField('ts_def', blank=True, null=True)
    ts_dispatch	= models.DateTimeField('ts_dispatch', blank=True, null=True)
    ts_start	= models.DateTimeField('ts_start', blank=True, null=True)
    ts_stop	= models.DateTimeField('ts_stop', blank=True, null=True)

    def __str__(self):
        return self.uuid
#    

class stage(models.Model):
    name	= models.CharField(max_length=32, default='')
    priority	= models.PositiveIntegerField(default=0)
    njobs	= models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.name
    
