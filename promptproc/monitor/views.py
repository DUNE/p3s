
#########################################################
#                      MONITOR                          #
#########################################################
# TZ-awarewness:					#
# The following is not TZ-aware: datetime.datetime.now()#
# so we are using timezone.now() where needed		#
#########################################################

# python utiility classes
import uuid
import datetime
from datetime import timedelta

# core django
from django.shortcuts			import render
from django.utils			import timezone
from django.utils.timezone		import utc
from django.http			import HttpResponse
from django.views.decorators.csrf	import csrf_exempt
from django.core			import serializers
from django.utils.safestring		import mark_safe
from django.forms.models		import model_to_dict

# models used in the application:
from pilots.models			import pilot
from jobs.models			import job

# tables2 machinery
import	django_tables2 as tables
from	django_tables2			import RequestConfig
from	django_tables2.utils		import A


# we need this to make links to this service itse.
try:
    from django.urls import reverse
except ImportError:
    print("FATAL IMPORT ERROR")
    exit(-3)

# just something for later - advanced tables:
# from django.views.generic.base import TemplateView


#########################################################    
class MonitorTable(tables.Table):
    def set_site(self, site=''):
        self.site=site

    def makelink(self, what, key, value):
        return mark_safe('<a href="http://%s%s?%s=%s">%s</a>'
                         % (self.site, reverse(what), key, value, value))
        
#########################################################    
class PilotTable(MonitorTable):
    def render_uuid(self,value):	return self.makelink('pilots',	'uuid',	value)
    def render_j_uuid(self,value):	return self.makelink('jobs',	'uuid',	value)
    def render_id(self,value):		return self.makelink('pilots',	'pk',	value)

    class Meta:
        model = pilot
        attrs = {'class': 'paleblue'}

#########################################################    
class JobTable(MonitorTable):
    def set_site(self, site=''):
        self.site=site

    # devnote - shifting to "jobdetail"
    def render_uuid(self,value):	return self.makelink('jobs',	'uuid',	value)
    def render_p_uuid(self,value):	return self.makelink('pilots',	'uuid',	value)
    def render_id(self,value):		return self.makelink('jobdetail',	'pk',	value)
        
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

        yest = datetime.datetime.now() - timedelta(days=1)

        for o in objects.filter(ts_lhb__gte=yest):
            print(o.ts_lhb)
        
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
def jobdetail(request):
    pk	= request.GET.get('pk','')

    j = model_to_dict(job.objects.get(pk=pk))
    print(j.keys())
    data = []

    for a in j.keys():
        data.append({'attribute': a, 'value': j[a]})
#        data.append({'value': j[a]})
    
#    data = [
#        {'name': 'Bradley'},
#        {'name': 'Stevie'},
#    ]

    class NameTable(tables.Table):
        attribute = tables.Column()
        value = tables.Column()
        class Meta:
            attrs = {'class': 'paleblue'}

    table = NameTable(data)
    
    return render(request, 'jobdetail.html', {'jobdetail' : table})


#########################################################    
# for later:
#    data = serializers.serialize('json', [ p, ])
#########################################################    
# Code sample for later:
#    uuid = tables.LinkColumn(viewname='dummy',
#    args=[A('pk')], text='foo', orderable=False,
#    empty_values=())
#
# def render_uuid(self,value): return mark_safe('<a
# href="http://%s%s?uuid=%s">%s</a>' % (self.site, reverse('pilots'),
# value, value))

#     def render_j_uuid(self,value): return mark_safe('<a
#     href="http://%s%s?uuid=%s">%s</a>' % (self.site, reverse('jobs'),
#     value, value))
    
#     def render_id(self,value): return mark_safe('<a
#     href="http://%s%s?pk=%s">%s</a>' % (self.site, reverse('pilots'),
#     value, value))

