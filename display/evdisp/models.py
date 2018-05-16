# models for the Event Display data
# the idea is to catalog images and their paths

import json
from django.db		import models
from django.core	import serializers

class evdisp(models.Model):
    run		= models.PositiveIntegerField(default=0, verbose_name='Run')
    subrun	= models.PositiveIntegerField(default=0, verbose_name='SubRun')
    evnum	= models.PositiveIntegerField(default=0, verbose_name='Event')
    changroup	= models.PositiveIntegerField(default=0, verbose_name='Channel Group')
    
    # There are six Channel Groups:
    # 0-2559
    # 2560-4639
    # 5120-7679
    # 7680-9759
    # 10240-12799
    # 12800-14879
    
    datatype	= models.CharField(max_length=16, default='', verbose_name='Data Type') # "raw" or "prep"
    ts		= models.DateTimeField(blank=True, null=True, verbose_name='Timestamp')
    path	= models.CharField(max_length=256,default='', verbose_name='Path')
    j_uuid	= models.CharField(max_length=36, default='', verbose_name='Produced by job')

    def __str__(self):
        return serializers.serialize("json", [self, ])

