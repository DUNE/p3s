import json
from django.db import models
from django.core	import serializers

class monrun(models.Model):
    run		= models.PositiveIntegerField(default=0, verbose_name='Run')
    subrun	= models.PositiveIntegerField(default=0, verbose_name='SubRun')
    summary	= models.TextField(default='{}')
    j_uuid	= models.CharField(max_length=36, default='', verbose_name='Produced by job')

    @classmethod
    def TPCmonitor(self, N=None):
        tpcMonCategories = [
            ('RMS of ADC per view per APA for all channels',	'fChanRMSDist'),
            ('Mean of ADC per view per APA for all channels',	'fChanMeanDist'),
            ('RMS of ADC per channel per view per APA and per channel','fChanRMS*pfx'),
            ('Mean of ADC per channel per view per APA and per channel', 'fChanMean*pfx*'),
            ('RMS of channel ADC from slots', 'Slot*RMSpfx*'),
        ]

        if N is None:
            return tpcMonCategories
        else:
            return tpcMonCategories[N]
