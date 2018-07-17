from django.shortcuts			import render
from django.utils.safestring		import mark_safe
from django.utils			import timezone
from django.utils.timezone		import utc
from django.conf			import settings

from django.db.models import F

import	django_tables2 as tables


from purity.models import pur
from evdisp.models import evdisp
from .models import monrun


# We need this to make links to this service itself.
try:
    from django.urls import reverse
except ImportError:
    print("FATAL IMPORT ERROR")
    exit(-3)


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

        subrun_url = '<a href="http://%s/monitor/showmon?run=%s&subrun=%s">%s</a>' % (
            self.site, str(record.run), str(record.subrun), value
        )

        return mark_safe(subrun_url)

    class Meta:
        model = monrun
        attrs = {'class': 'paleblue'}
        exclude = ('description',)
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



