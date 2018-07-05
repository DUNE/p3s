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
    def ALLmonitor(self, what, N=None):
        if(what == 'tpc'):
            common = 'run%s_%s_tpcmonitor_'
        elif(what == 'pdsphit'):
            common = 'run%s_%s_pdsphitmonitor_'
        else:
            common = ''
            
        Categories = {}
        Categories['tpc'] = [
            ('RMS of ADC per view per APA for all channels',		common+'fChanRMSDist%s%s.png'),
            ('Mean of ADC per view per APA for all channels',		common+'fChanMeanDist%s%s.png'),
            
            ('RMS of ADC per channel per view per APA and per channel',	common+'fChanRMS%s%spfx.png'),
            ('Mean of ADC per channel per view per APA and per channel',common+'fChanMean%s%spfx.png'),
            
            ('RMS of channel ADC from slots',	common+'Slot%sRMSpfx.png',	30),
            ('Mean of channel ADC from slots',	common+'Slot%sMeanpfx.png',	30),

            ('Channels Stuck Code On',		common+'fChanStuckCodeOnFrac%s%s.png'),
            ('Channels Stuck Code Off', 	common+'fChanStuckCodeOnFrac%s%s.png'),

            ('FFT',				common+'fChanFFT%s%s.png'),
            
            ('Persistent FFT fiber',		common+'PersistentFFTFiber%s.png', 120),
            ('Profiled FFT fiber',		common+'ProfiledFFTFiber%s.png', 120),
        ]

        Categories['pdsphit'] = [
            ('NHits distribution for each view and each APA',		common+'NHitsAPA%s%s.png'),
            ('Hit Charge distribution for each view and each APA',	common+'HitChargeAPA%s%s.png'),
            ('Hit RMS distribution for each view and each APA',		common+'HitRMSAPA%s%s.png'),
            ('Hit peak time for each view and each APA',		common+'HitPeakTimeAPA%s%s.png'),
            ('NHits profiled',						common+'fNHitsView%s%sprof.png'),
            ('Hit charge profiled',					common+'fChargeView%s%sprof.png'),
            ('Hit RMS profile',						common+'fRMSView%s%sprof.png'),
        ]


        if N is None:
            return Categories[what]
        else:
            return Categories[what][N]

    # ---
    @classmethod
    def planes(self):
        return ['U','V','Z']
    # ---
    @classmethod
    def PDSPHITmonitorCatURLs(self, domain, run, subrun):
        catPattern = '<a href="http://%s/monitor/showmon?run=%s&subrun=%s&pdsphitmoncat=%s">%s</a>'
        data = []
        cnt=0
        for item in monrun.ALLmonitor('pdsphit'):
            tpcmoncat_url =  catPattern % (domain, run, subrun, str(cnt), item[0])
            cnt+=1
            data.append({'items':mark_safe(tpcmoncat_url)})

        return data
    # ---
    @classmethod
    def TPCmonitorCatURLs(self, domain, run, subrun):
        catPattern = '<a href="http://%s/monitor/showmon?run=%s&subrun=%s&tpcmoncat=%s">%s</a>'
        data = []
        cnt=0
        for item in monrun.ALLmonitor('tpc'):
            tpcmoncat_url =  catPattern % (domain, run, subrun, str(cnt), item[0])
            cnt+=1
            data.append({'items':mark_safe(tpcmoncat_url)})

        return data
    # ---
    @classmethod
    def TPCmonitorURL(self, what, N, domain, dqmURL, j_uuid, run, subrun, plane, apa):
        pattern	= self.ALLmonitor(what,N)[1]
        filename= pattern % (run, subrun, plane, apa) # print('filename:',filename)
        return ('http://%s/%s/%s/%s' % (domain, dqmURL, j_uuid, filename))
    # ---
    @classmethod
    def TPCmonitorURLplanes(self, what, N, domain, dqmURL, j_uuid, run, subrun):
        rows = []
        for plane in self.planes():
            row = []
            for apa in range(6):
                plotUrl = self.TPCmonitorURL(what, N, domain, dqmURL, j_uuid, run, subrun, plane, apa)
                row.append(plotUrl)
            rows.append(row)

        return rows
    # ---
    @classmethod
    def TPCmonitorURLind(self, N, domain, dqmURL, j_uuid, run, subrun):
        row = []
        rows = []
        
        pattern	= self.ALLmonitor('tpc', N)[1]
        cnt = 0
        for ind in range(self.ALLmonitor('tpc', N)[2]):
            filename= pattern % (run, subrun, str(ind)) # print(filename)
            row.append('http://%s/%s/%s/%s' % (domain, dqmURL, j_uuid, filename))
            cnt+=1
            if cnt==6:
                cnt=0
                rows.append(row)
                row = []
        if(len(row)>0): rows.append(row) #!

        return rows
