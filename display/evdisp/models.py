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
    # 1. 0-2559
    # 2. 2560-4639
    # 3. 5120-7679
    # 4. 7680-9759
    # 5. 10240-12799
    # 6. 12800-14879
    
    datatype	= models.CharField(max_length=16, default='', verbose_name='Data Type') # "raw" or "prep"
    ts		= models.DateTimeField(blank=True, null=True, verbose_name='Timestamp')
    path	= models.CharField(max_length=256,default='', verbose_name='Path')
    j_uuid	= models.CharField(max_length=36, default='', verbose_name='Produced by job')

    def __str__(self):
        return serializers.serialize("json", [self, ])

    @classmethod
    def message(self):
        return "Channel Groups - 1:0-2559, 2:2560-4639, 3:5120-7679, 4:7680-9759, 5:10240-12799, 6:12800-14879"

    @classmethod
    def group2string(self, N=None):
        if(N==1):	return("0-2559")
        if(N==2):	return("2560-4639")
        if(N==3):	return("5120-7679")
        if(N==4):	return("7680-9759")
        if(N==5):	return("10240-12799")
        if(N==6):	return("12800-14879")

    @classmethod
    def makename(self, event=None, datatype=None, group=None):
        channels = evdisp.group2string(group)
        return ("adc%s_evt%s_ch%s.png" % (datatype, str(event), evdisp.group2string(group)))
    # sample: adcraw_evt112_ch7680-9759.png
        
