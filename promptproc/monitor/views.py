
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
    
    def render_id(self,value):
        return mark_safe('<a href="http://%s%s?pk=%s">%s</a>'
                         % (self.site, reverse('pilots'), value, value))
    class Meta:
        model = pilot
        attrs = {'class': 'paleblue'}
#########################################################    
class JobTable(tables.Table):
    def set_site(self, site=''):
        self.site=site
        
    def render_uuid(self,value):
        return mark_safe('<a href="http://%s%s?uuid=%s">%s</a>'
                         % (self.site, reverse('jobs'), value, value))
    
    def render_id(self,value):
        return mark_safe('<a href="http://%s%s?pk=%s">%s</a>'
                         % (self.site, reverse('jobs'), value, value))
    
    class Meta:
        model = job
        attrs = {'class': 'paleblue'}
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

    # FIXME -beautify the timestamp later -mxp-
    now		= datetime.datetime.now().strftime('%x %X')
    domain	= request.get_host()
    d		= dict(domain=domain, time=str(now))

    objects, t	= None, None
    
    if(what=='pilots'):
        template = 'pilots.html'
        objects = pilot.objects
        if(uuid == '' and pk == ''):	t = PilotTable(objects.all())
        if(uuid != ''):			t = PilotTable(objects.filter(uuid=uuid))
        if(pk != ''):			t = PilotTable(objects.filter(pk=pk))
        
    if(what=='jobs'):
        template = 'jobs.html'
        objects = job.objects
        if(uuid == '' and pk == ''):	t = JobTable(objects.all())
        if(uuid != ''):			t = JobTable(objects.filter(uuid=uuid))
        if(pk != ''):			t = JobTable(objects.filter(pk=pk))

    t.set_site(domain)
    RequestConfig(request).configure(t)
    d[what]=t

    return render(request, template, d)


#########################################################    
# for later:
#    data = serializers.serialize('json', [ p, ])
