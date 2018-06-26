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
            ('RMS of ADC per view per APA for all channels',		'run%s_subrun%s_tpcmonitor_fChanRMSDist%s%s.png'),
            ('Mean of ADC per view per APA for all channels',		'run%s_subrun%s_tpcmonitor_fChanMeanDist%s%s.png'),
            
            ('RMS of ADC per channel per view per APA and per channel',	'run%s_subrun%s_tpcmonitor_fChanRMS%s%spfx.png'),
            ('Mean of ADC per channel per view per APA and per channel','run%s_subrun%s_tpcmonitor_fChanMean%s%spfx.png'),
            
            ('RMS of channel ADC from slots', 'run%s_subrun%s_tpcmonitor_Slot%sRMSpfx.png'),
            ('Mean of channel ADC from slots', 'run%s_subrun%s_tpcmonitor_Slot%sMeanpfx.png'),
        ]

        if N is None:
            return tpcMonCategories
        else:
            return tpcMonCategories[N]

    # ---
    @classmethod
    def TPCmonitorURL(self, N, domain, dqmURL, j_uuid, run, subrun, plane, apa):
        pattern	= self.TPCmonitor(N)[1]
        filename = None
        if(N<4):
            filename= pattern % (run, subrun, plane, apa)
        elif(N>3 and N<6):
            pass
        else:
            pass
        
        return ('http://%s/%s/%s/%s' % (domain, dqmURL, j_uuid, filename))
        


#        filename = 'run'+run+'_subrun'+subrun+'_tpcmonitor_'+pattern+plane+str(apa)+'.png'
