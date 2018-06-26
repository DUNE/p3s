import json
from django.db import models
from django.core	import serializers

class monrun(models.Model):
    run		= models.PositiveIntegerField(default=0, verbose_name='Run')
    subrun	= models.PositiveIntegerField(default=0, verbose_name='SubRun')
    summary	= models.TextField(default='{}')
    j_uuid	= models.CharField(max_length=36, default='', verbose_name='Produced by job')

    # ---
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

    # ---
    @classmethod
    def TPCmonitorURL(self, N, domain, dqmURL, j_uuid, run, subrun, plane, apa):
        # print(self.TPCmonitor(0))
        
        pattern = self.TPCmonitor(N)[1]

        myPattern = ('run%s_subrun%s_tpcmonitor_fChanRMSDist%s%s.png'
                     % (run, subrun, plane, apa))
        filename = 'run'+run+'_subrun'+subrun+'_tpcmonitor_'+pattern+plane+str(apa)+'.png'
        plotUrl = ('http://%s/%s/%s/%s'
                   % (domain, dqmURL, j_uuid, filename)
        )
        
        print(plotUrl)
        return plotUrl
        
