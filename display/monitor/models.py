import json
from django.db import models
from django.core	import serializers
from django.utils.safestring		import mark_safe

class monrun(models.Model):
    run		= models.PositiveIntegerField(default=0, verbose_name='Run')
    subrun	= models.PositiveIntegerField(default=0, verbose_name='SubRun')
    summary	= models.TextField(default='{}')
    j_uuid	= models.CharField(max_length=36, default='', verbose_name='Produced by job')

    # ---
    @classmethod
    def TPCmonitor(self, N=None):
        common = 'run%s_subrun%s_tpcmonitor_'
        tpcMonCategories = [
            ('RMS of ADC per view per APA for all channels',		common+'fChanRMSDist%s%s.png'),
            ('Mean of ADC per view per APA for all channels',		common+'fChanMeanDist%s%s.png'),
            
            ('RMS of ADC per channel per view per APA and per channel',	common+'fChanRMS%s%spfx.png'),
            ('Mean of ADC per channel per view per APA and per channel',common+'fChanMean%s%spfx.png'),
            
            ('RMS of channel ADC from slots',	common+'Slot%sRMSpfx.png',	30),
            ('Mean of channel ADC from slots',	common+'Slot%sMeanpfx.png',	30),

            ('Channels Stuck Code On',		common+'fChanStuckCodeOnFrac%s%s.png'),
            ('Channels Stuck Code Off', 	common+'fChanStuckCodeOnFrac%s%s.png'),

            ('FFT',				common+'fChanFFT%s%s.png'),
        ]

        if N is None:
            return tpcMonCategories
        else:
            return tpcMonCategories[N]

    # ---
    @classmethod
    def planes(self):
        return ['U','V','Z']
    # ---
    @classmethod
    def TPCmonitorCatURLs(self, domain, run, subrun):
        # eval('self.test(1)')
        catPattern = '<a href="http://%s/monitor/showmon?run=%s&subrun=%s&tpcmoncat=%s">%s</a>'
        data = []
        cnt=0
        for item in monrun.TPCmonitor():
            tpcmoncat_url =  catPattern % (domain, run, subrun, str(cnt), item[0])
            cnt+=1
            data.append({'items':mark_safe(tpcmoncat_url)})

        return data
    # ---
    @classmethod
    def TPCmonitorURL(self, N, domain, dqmURL, j_uuid, run, subrun, plane, apa):
        pattern	= self.TPCmonitor(N)[1]
        filename= pattern % (run, subrun, plane, apa) # print('filename:',filename)
        return ('http://%s/%s/%s/%s' % (domain, dqmURL, j_uuid, filename))
    # ---
    @classmethod
    def TPCmonitorURLplanes(self, N, domain, dqmURL, j_uuid, run, subrun):
        rows = []
        for plane in self.planes():
            row = []
            for apa in range(6):
                plotUrl = self.TPCmonitorURL(N, domain, dqmURL, j_uuid, run, subrun, plane, apa)
                row.append(plotUrl)
            rows.append(row)

        return rows
    # ---
    @classmethod
    def TPCmonitorURLind(self, N, domain, dqmURL, j_uuid, run, subrun):
        row = []
        rows = []
        
        pattern	= self.TPCmonitor(N)[1]
        cnt = 0
        for ind in range(self.TPCmonitor(N)[2]):
            filename= pattern % (run, subrun, str(ind)) # print(filename)
            row.append('http://%s/%s/%s/%s' % (domain, dqmURL, j_uuid, filename))
            cnt+=1
            if cnt==6:
                cnt=0
                rows.append(row)
                row = []
        if(len(row)>0): rows.append(row) #!

        return rows
