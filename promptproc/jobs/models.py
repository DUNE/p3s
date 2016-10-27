from django.db import models

# Create your models here.
class job(models.Model):
    stage_name	= models.CharField(max_length=20)
    ts_def	= models.DateTimeField('ts_def', blank=True, null=True)
    ts_dispatch	= models.DateTimeField('ts_dispatch', blank=True, null=True)
    ts_start	= models.DateTimeField('ts_start', blank=True, null=True)
    ts_stop	= models.DateTimeField('ts_stop', blank=True, null=True)

    
    def __str__(self):
        return self.stage_name
#PositiveIntegerField
