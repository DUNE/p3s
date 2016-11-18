
#########################################################
#                      MONITOR                          #
#########################################################
# TZ-awarewness:					#
# The following is not TZ-aware: datetime.datetime.now()#
# so we are using timezone.now() where needed		#
#########################################################

from django.shortcuts import render

import datetime
from django.utils import timezone
from django.utils.timezone import utc

import uuid

from django.shortcuts			import render
from django.http			import HttpResponse
from django.views.decorators.csrf	import csrf_exempt
from django.utils			import timezone
from django.core			import serializers
from django.utils.safestring		import mark_safe

from pilots.models	import pilot
from jobs.models	import job

# machinery for customizing tables
import django_tables2 as tables
from django_tables2 import RequestConfig
from django_tables2.utils import A

# just something for later, advanced tables, not used in the first cut
from django.views.generic.base import TemplateView

try:
    from django.urls import reverse
except ImportError:
    print("FATAL IMPORT ERROR")
    exit(-3)




    
#########################################################    
# Code sample for later:
#    uuid = tables.LinkColumn(viewname='dummy',
#    args=[A('pk')], text='foo', orderable=False,
#    empty_values=())
#########################################################    
class PilotTable(tables.Table):
    def set_site(self, site=''):
        self.site=site
        
    def render_uuid(self,value):
        return mark_safe('<a href="http://%s%s?uuid=%s">%s</a>'
                         % (self.site, reverse('pilots'), value, value))
    
    class Meta:
        model = pilot
        attrs = {'class': 'paleblue'} # add class="paleblue" to <table> tag
#########################################################    
class JobTable(tables.Table):
    def set_site(self, site=''):
        self.site=site
        
    def render_uuid(self,value):
        return mark_safe('<a href="http://%s%s?uuid=%s">%s</a>'
                         % (self.site, reverse('jobs'), value, value))
    
    class Meta:
        model = job
        attrs = {'class': 'paleblue'} # add class="paleblue" to <table> tag
#########################################################    
def pilots(request):
    return data_handler(request, 'pilots')

#########################################################    
def jobs(request):
    return data_handler(request, 'jobs')

#########################################################    
def data_handler(request, what):
    uuid	= request.GET.get('uuid','')
    pk		= request.GET.get('pk','')

    now		= datetime.datetime.now()
    domain	= request.get_host()
    d=dict(domain=domain, time=str(now))

    objects	= None
    t		= None
    
    if(what=='pilots'):
        template = 'pilots.html'
        objects = pilot.objects
        t=PilotTable(objects.all())
        
    if(what=='jobs'):
        template = 'jobs.html'
        objects = job.objects
        t=JobTable(objects.all())
        
    t.set_site(domain)
    
    if(uuid == '' and pk == ''):
        d[what]=t
    if(uuid != ''):			d[what] = objects.filter(uuid=uuid)
    if(pk != ''):			d[what] = objects.filter(pk=pk)
        
    return render(request, template, d)

def dummy(a):
    return HttpResponse("!")

#########################################################    
# for later:
#    data = serializers.serialize('json', [ p, ])
