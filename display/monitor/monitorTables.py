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


from purity.models import pur
from evdisp.models import evdisp
from .models import monrun

#########################################################
Planes = ('U','V','Z')
# ---
monchartHitsHeaderURL	= '<th><a href="http://%s/monitor/monchart?plane=%s&what=hits"  >%s Hits/RMS  </a></th>'
monchartChargeHeaderURL	= '<th><a href="http://%s/monitor/monchart?plane=%s&what=charge">%s Charge/RMS</a></th>'
# ---
monPatterns = {
    "hits1":	"Plane %s Mean NHits",
    "hits2":	"Plane %s Mean of Hit RMS",
    "charge1":	"Plane %s Mean of Charge",
    "charge2":	"Plane %s RMS of Charge",
    "dead":	"NDead  Channels",
    "noise1":	"NNoisy Channels 6Sigma away from mean value of the ADC RMS",
    "noise2":	"NNoisy Channels Above ADC RMS Threshold(40)"
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
    class Meta:
        model = pur
        attrs = {'class': 'paleblue'}
#---
class ShowMonTable(MonitorTable):
    items = tables.Column()

    def changeName(self, newName):
        self.base_columns['items'].verbose_name = newName

    class Meta:
        attrs = {'class': 'paleblue'}
#---
#############################################################
#############################################################
#############################################################
class MonRunTable(MonitorTable):
    def render_run(self, value, record):
        subrun_url = '<a href="http://%s/monitor/automon?run=%s&subrun=%s">%s::%s</a>' % (
            self.site, value, str(record.subrun), value, str(record.subrun)
        )
        output=mark_safe(subrun_url)+'<hr/>'+record.j_uuid
        return format_html(output)
    
    def render_summary(self, value, record):

        output = '<table width="100%"><tr>'
        
        data = json.loads(value, object_pairs_hook=OrderedDict)
        d_raw = data[0]

        d = OrderedDict()
                
        keyList = d_raw.keys()
        for k in keyList:
            if('Plane' in k):
                d[k]=d_raw[k]

        print(d)
        # column headers for hits and charge
        try:
            for plane in Planes: output+= (monchartHitsHeaderURL)	% (self.site, plane, plane)
            for plane in Planes: output+= (monchartChargeHeaderURL)	% (self.site, plane, plane)
        except:
            pass

        # column headers for dead and noisy channels
        try:
            # probe the data
            foo1 = d["NDead  Channels"]
            foo2 = d["NNoisy Channels 6Sigma away from mean value of the ADC RMS"]
            foo3 = d["NNoisy Channels Above ADC RMS Threshold(40)"]
                     
            output+=('<th><a href="http://%s/monitor/monchart?what=dead">Dead Channels</th>') % (self.site)
            output+=('<th><a href="http://%s/monitor/monchart?what=noise">Noisy 6&sigma;/1&sigma;') % (self.site)
        except:
            pass

        output+='</tr><tr>' # ready to add the data to columns
        
        # columns for hits and charge
        try:
            for plane in Planes:
                output+= '<td>'+ ('%s<hr/>%s</td>')	% (d[monPatterns['hits1']  % plane], d[monPatterns['hits2']  % plane])
            for plane in Planes:
                output+= ('<td>%s<hr/>%s</td>')	% (d[monPatterns['charge1']% plane], d[monPatterns['charge2']% plane])
        except:
            pass
        
        # columns for dead and noisy channels
        try:
            # probe the data
            foo1 = d["NDead  Channels"]
            foo2 = d["NNoisy Channels 6Sigma away from mean value of the ADC RMS"]
            foo3 = d["NNoisy Channels Above ADC RMS Threshold(40)"]

            output+='<td>%s</td>'          % (pad0four(d["NDead  Channels"]))
            output+=('<td>%s<hr/>%s</td>') % (pad0four(d["NNoisy Channels 6Sigma away from mean value of the ADC RMS"]),pad0four(d["NNoisy Channels Above ADC RMS Threshold(40)"]))
        except:
            pass
        
        output+='</tr></table>'
        
        return format_html(output)
    
    class Meta:
        model = monrun
        attrs = {'class': 'paleblue'}
        exclude = ('description','j_uuid','subrun','id',)
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

