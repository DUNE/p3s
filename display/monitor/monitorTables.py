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

patternHits1	= "Plane %s Mean NHits"
patternHits2	= "Plane %s Mean of Hit RMS"

patternCharge1	= "Plane %s Mean of Charge"
patternCharge2	= "Plane %s RMS of Charge"

monPatterns = {
    "hits1":	"Plane %s Mean NHits",
    "hits2":	"Plane %s Mean of Hit RMS",
    "charge1":	"Plane %s Mean of Charge",
    "charge2":	"Plane %s RMS of Charge",
    "dead":	"NDead  Channels"
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
class MonRunTable(MonitorTable):
    def render_subrun(self, value, record):

        subrun_url = '<a href="http://%s/monitor/showmon?run=%s&subrun=%s">%s (old)</a> <br/><a href="http://%s/monitor/automon?run=%s&subrun=%s">%s (new)</a>' % (
            self.site, str(record.run), str(record.subrun), value,
            self.site, str(record.run), str(record.subrun), value
        )

        return mark_safe(subrun_url)

    def render_run(self, value, record):
        subrun_url = '<a href="http://%s/monitor/automon?run=%s&subrun=%s">%s::%s</a>' % (
            self.site, value, str(record.subrun), value, str(record.subrun)
        )
        output=mark_safe(subrun_url)+'<hr/>'+record.j_uuid
        return format_html(output)
    
    def render_summary(self, value, record):

        output = '<table><tr>'
        
        data = json.loads(value, object_pairs_hook=OrderedDict)
        d = data[0]

        for plane in Planes: output+= ('<th><a href="http://%s/monitor/monchart?plane=%s&what=hits">%s Hits/RMS</a></th>') % (self.site, plane, plane)
        
        for plane in Planes: output+= ('<th><a href="http://%s/monitor/monchart?plane=%s&what=charge">%s Charge/RMS</a></th>') % (self.site, plane, plane)

        output+='<th>Dead Channels</th><th>Noisy 6&sigma;/1&sigma;'
        output+='</tr><tr>'
            
        for plane in Planes: output+= ('<td>%s<hr/>%s</td>') % (d[patternHits1%plane],d[patternHits2%plane])
        for plane in Planes: output+= ('<td>%s<hr/>%s</td>') % (d[patternCharge1%plane],d[patternCharge2%plane])

        output+='<td>%s</td>' % pad0four(d["NDead  Channels"])
        output+=('<td>%s<hr/>%s</td>') % (pad0four(d["NNoisy Channels 6Sigma away from mean value of the ADC RMS"]),pad0four(d["NNoisy Channels Above ADC RMS Threshold(40)"]))
        output+='</tr></table>'
        
        return format_html(output)
    
    class Meta:
        model = monrun
        attrs = {'class': 'paleblue'}
        exclude = ('description','j_uuid','subrun','id',)
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



