# models for the Event Display data
# the idea is to catalog images and their paths

import json
from django.db		import models
from django.core	import serializers

class evdisp(models.Model):
    run		= models.PositiveIntegerField(default=0)
    subrun	= models.PositiveIntegerField(default=0)
    evnum	= models.PositiveIntegerField(default=0)
    changroup	= models.PositiveIntegerField(default=0)
    
    # There are six Channel Groups:
    # 0-2559
    # 2560-4639
    # 5120-7679
    # 7680-9759
    # 10240-12799
    # 12800-14879
    
    datatype	= models.CharField(max_length=16, default='') # "raw" or "prep"
    ts		= models.DateTimeField('ts', blank=True, null=True)
    path	= models.CharField(max_length=256,default='') # path to the image file
    j_uuid	= models.CharField(max_length=36, default='') # job uuid

    def __str__(self):
        return serializers.serialize("json", [self, ])

