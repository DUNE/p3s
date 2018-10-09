import json
from collections			import OrderedDict

from django.shortcuts			import render
from django.utils.safestring		import mark_safe
from django.utils			import timezone
from django.utils.timezone		import utc
from django.conf			import settings

from django.db.models import F

import	django_tables2 as tables
from django.utils.html import format_html


from purity.models			import pur
from evdisp.models			import evdisp
from .models				import monrun

from utils.tpcMap			import *

#########################################################
Planes = ('U','V','Z')

# ---
monchartHitsHeaderURL	= '<th><a href="http://%s/monitor/monchart?plane=%s&what=hits"  >%s Hits/RMS  </a></th>'
monchartChargeHeaderURL	= '<th><a href="http://%s/monitor/monchart?plane=%s&what=charge">%s Charge/RMS</a></th>'
monchartRawRmsURL	= '<th><a href="http://%s/monitor/monchart?plane=%s&what=meanrawrms">%s Mean of Raw RMS</a></th>'

# ---
monPatterns = {
    "hits1":	"Plane %s Mean NHits",
    "hits2":	"Plane %s Mean of Hit RMS",
    "charge1":	"Plane %s Mean of Charge",
    "charge2":	"Plane %s RMS of Charge",
    "dead":	"NDead  Channels",
    "noise1":	"NNoisy Channels 6Sigma away from mean value of the ADC RMS",
    "noise2":	"NNoisy Channels Above ADC RMS Threshold",
    "meanrawrms":	"Plane %s Mean of Raw RMS",
}


monTags = {
    'evdisp':	'<td>EVENT DISPLAY</td></tr></table>',
    'femb':	'<td>FEMB monitor</td></tr></table>',
    'crt':	'<td>CRT</td></tr></table>',
    'purity':	'<td>PURITY</td></tr></table>',
}

#########################################################
# We need this to make links to this service itself.
try:
    from django.urls import reverse
except ImportError:
    print("FATAL IMPORT ERROR")
    exit(-3)


#########################################################
#########################################################
#########################################################
def pad0four(input):
        mylist = input.split(',')
        newList = []
        for item in mylist: newList.append('{0:0>4}'.format(item))
        return ",".join(newList)

#########################################################    
################## LINK UTILS ###########################    
#########################################################

def makeImageLink(site, evdispURL, j_uuid, run, evnum, datatype, group):
    filename =  evdisp.makename(evnum, datatype, group)
    # debug only:  print(evnum, datatype, group)
    # debug only:  print("filename", filename)
    return "http://"+site+"/"+evdispURL+"/"+j_uuid+"/"+filename


def makeEvLink(site, run, evnum):
    return mark_safe('<a href="http://%s/monitor/display6?run=%s&event=%s">%s</a>' % (site, run, evnum, evnum))


#########################################################    
###################  TABLES #############################    
#########################################################

class RunTable(tables.Table):
    Run	= tables.Column()
    ts	= tables.Column(verbose_name='Time Added to DB')
    evs	= tables.Column(verbose_name='Event Numbers')
    
    def set_site(self, site=''):
        self.site=site
    class Meta:
        attrs	= {'class': 'paleblue'}

#---
class MonitorTable(tables.Table):
    def set_site(self, site=''):
        self.site=site

    def makelink(self, what, key, value):
        return mark_safe('<a href="http://%s%s?%s=%s">%s</a>'
                         % (self.site, reverse(what), key, value, value))

    def renderDateTime(self, dt): # common format defined here.
        return timezone.localtime(dt).strftime(settings.TIMEFORMAT)

    def modifyName(self, oldName, newName):
        self.base_columns[oldName].verbose_name = newName

#---
class PurityTable(MonitorTable):
    def render_tpc(self, value):
        return str(value)+': '+tpcMap[value]
    class Meta:
        model = pur
        attrs = {'class': 'paleblue'}
#---
class ShowMonTable(MonitorTable):
    
#    def __init__(self, *args, **kwargs):
#        self.hdr = kwargs.pop('hdr')
#        super(ShowMonTable, self).__init__(*args, **kwargs)

    def changeName(self, newName):
        self.base_columns['items'].verbose_name = newName

    items = tables.Column()

    
    class Meta:
        attrs = {'class': 'paleblue'}
#---
#############################################################
#############################################################
#############################################################
class MonRunTable(MonitorTable):
    def render_run(self, value, record):
        subrun_url = '<a href="http://%s/monitor/automon?run=%s&subrun=%s&dl=%s&jobtype=%s">%s::%s::%s::%s</a>' % (
            self.site, value, str(record.subrun), str(record.dl), record.jobtype, value, str(record.subrun), str(record.dl), record.jobtype
        )
        output=mark_safe(subrun_url)+'<hr/>'+record.j_uuid # +'<hr/>'+str(record.ts.strftime(settings.TIMEFORMAT))

        return format_html(output)
    
    # ---
    # we now have the processing type in the metadata (e.g. "monitor")
    # which should allow us to simplify the code
    #
    #
    # this is the most important (and crafty) method of all, we parse json
    # and populate tables within the monrun table dynamically
    
    def render_summary(self, value, record):
        # this better be moved to the template...
        output = '<table width="100%"><tr>'
        
        data = json.loads(value, object_pairs_hook=OrderedDict)
        d = data[0]

        monType = None
        try:
            monType = d['Type']
        except:
            pass

        # ---
        if monType is None:
            output+='<td>ERROR PARSING JSON</td></tr></table>'
            return format_html(output)
        
        # ---
        if monType=='monitor':
            try:
                # column headers for hits and charge
                try:
                    for plane in Planes: output+= (monchartHitsHeaderURL)	% (self.site, plane, plane)
                except:
                    pass

                try:
                    for plane in Planes: output+= (monchartChargeHeaderURL)	% (self.site, plane, plane)
                except:
                    pass

                try:
                    for plane in Planes:
                        testing = d[monPatterns['meanrawrms'] % plane]
                        output+= (monchartRawRmsURL) % (self.site, plane, plane)
                except:
                    pass

                # column headers for dead and noisy channels
                output+=('<th><a href="http://%s/monitor/monchart?what=dead">Dead Channels</th>') % (self.site)
                output+=('<th><a href="http://%s/monitor/monchart?what=noise">Noisy over 6&sigma; vs over the threshold') % (self.site)

                output+='</tr><tr>' # ready to add the data to columns
            
                # columns for hits and charge
                try:
                    for plane in Planes: output+= ('<td>%s<hr/>%s</td>')	% (d[monPatterns['hits1']	% plane], d[monPatterns['hits2']  % plane])
                except:
                    pass
                
                try:
                    for plane in Planes: output+= ('<td>%s<hr/>%s</td>')	% (d[monPatterns['charge1']	% plane], d[monPatterns['charge2']% plane])
                except:
                    pass
                    
                try:
                    for plane in Planes: output+= ('<td>%s</td>')		% (d[monPatterns['meanrawrms']	% plane])
                except:
                    pass
                    
                # columns for dead and noisy channels
                output+='<td>%s</td>'          % (pad0four(d["NDead  Channels"]))
                output+=('<td>%s<hr/>%s</td>') % (pad0four(d["NNoisy Channels 6Sigma away from mean value of the ADC RMS"]),pad0four(d["NNoisy Channels Above ADC RMS Threshold"]))
        
                output+='</tr></table>'
            except:
                output+='<td>ERROR PARSING JSON</td></tr></table>'

            return format_html(output)
        
        # ---
        if monType=='reco':
            try:
                output+='<td>Number of reconstructed tracks: %s</td><td>Number of long reconstructed tracks: %s</td>' % (d['Number of reconstructed tracks'], d['Number of long reconstructed tracks'])
                output+='</tr></table>'
            except:
                output+='<td>ERROR PARSING JSON</td></tr></table>'
            return format_html(output)

        # ---
        try:
            output+=monTags[monType]
        except:            
            output+='<td>ERROR LOOKING UP PROCESSING TYPE</td></tr></table>'
           
        return format_html(output)


# Sample summary for the "reco" product:
# [
#    {
#       "Number of reconstructed tracks": "52.80",
#       "Number of long reconstructed tracks": "19.80",
#       "run": "run005077_0045_dl08",
#       "TimeStamp": "Tue Oct  9 05:10:28 2018",
#       "Type": "reco"
#    }
# ]

# Sample summary for the "monitor" product:
# [
#    {
#       "Plane U Mean NHits": "14.00,0.00,0.00,0.00,0.00,0.00",
#       "Plane V Mean NHits": "0.00,0.00,0.00,0.00,0.00,0.00",
#       "Plane Z Mean NHits": "0.00,0.00,0.00,0.00,0.00,0.00",
#       "Plane U Mean of Charge": "139.53,0.00,0.00,0.00,0.00,0.00",
#       "Plane V Mean of Charge": "0.00,0.00,0.00,0.00,0.00,0.00",
#       "Plane Z Mean of Charge": "653.67,0.00,0.00,0.00,0.00,0.00",
#       "Plane U RMS of Charge": "77.52,0.00,0.00,0.00,0.00,0.00",
#       "Plane V RMS of Charge": "0.00,0.00,0.00,0.00,0.00,0.00",
#       "Plane Z RMS of Charge": "383.14,0.00,0.00,0.00,0.00,0.00",
#       "Plane U Mean of Hit RMS": "5.02,0.00,0.00,0.00,0.00,0.00",
#       "Plane V Mean of Hit RMS": "0.00,0.00,0.00,0.00,0.00,0.00",
#       "Plane Z Mean of Hit RMS": "4.04,0.00,0.00,0.00,0.00,0.00",
#       "Plane U RMS of Hit RMS": "1.14,0.00,0.00,0.00,0.00,0.00",
#       "Plane V RMS of Hit RMS": "0.00,0.00,0.00,0.00,0.00,0.00",
#       "Plane Z RMS of Hit RMS": "1.85,0.00,0.00,0.00,0.00,0.00",
#       "NDead  Channels": "2432,2560,2560,2560,2560,   0",
#       "NNoisy Channels 6Sigma away from mean value of the ADC RMS": " 128,   0,   0,   0,   0,   0",
#       "NNoisy Channels Above ADC RMS Threshold": "  71,   0,   0,   0,   0,   0",
#       "run": "run003611_0001",
#       "TimeStamp": "Thu Aug 23 21:03:34 2018",
#       "Type": "monitor",
#       "APA": "1, 2, 3, 4, 5, 6"
#    }
# ]


    
    class Meta:
        model = monrun
        attrs = {'class': 'paleblue'}
        exclude = ('description','j_uuid','subrun','jobtype','dl',)
#############################################################
#############################################################
#############################################################
#---
class EvdispTable(MonitorTable):
    changroup = tables.Column(verbose_name='Grp')
#    ts = tables.Column(attrs={'td': {'bgcolor': 'red'}})

    def render_changroup(self, value, record):

        u = makeImageLink(self.site,
                          settings.SITE['dqm_evdisp_url'],
                          record.j_uuid, record.run, record.evnum, record.datatype, record.changroup)
        
        image_url = ('<a href="http://%s/monitor/display1?url=%s&run=%s&event=%s&changroup=%s&datatype=%s">%s</a>'
                         % (self.site,
                            u,
                            record.run,
                            record.evnum,
                            record.changroup,
                            record.datatype,
                            value
                         ))

        return mark_safe(image_url)

    def render_evnum(self, value, record):
        event_url = ('<a href="http://%s/monitor/display6?run=%s&event=%s">%s</a>'
                         % (self.site,
                            record.run,
                            record.evnum,
                            str(value)
                         ))
#        event_url='<a href="">'+str(record.evnum)+'</a>'
        return mark_safe(event_url)
    
    class Meta:
        model = evdisp
        attrs = {'class': 'paleblue'}
        exclude = ('path',)
        template_name = 'django_tables2/bootstrap4.html'
#########################################################    


# Keep for later if you want to display the subrun column in the monrun table
# Right now it's just unused anyway
    # def render_subrun(self, value, record):

    #     subrun_url = '<a href="http://%s/monitor/showmon?run=%s&subrun=%s">%s (old)</a> <br/><a href="http://%s/monitor/automon?run=%s&subrun=%s">%s (new)</a>' % (
    #         self.site, str(record.run), str(record.subrun), value,
    #         self.site, str(record.run), str(record.subrun), value
    #     )

    #     return mark_safe(subrun_url)

