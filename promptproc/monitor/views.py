
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
from datetime				import timedelta

# core django
from django.shortcuts			import render
from django.utils			import timezone
from django.utils.timezone		import utc
from django.http			import HttpResponse
from django.views.decorators.csrf	import csrf_exempt
from django.core			import serializers
from django.utils.safestring		import mark_safe
from django.forms.models		import model_to_dict

# Models used in the application:
from pilots.models			import pilot
from jobs.models			import job
from workflows.models			import dag, dagVertex, dagEdge

# tables2 machinery
import	django_tables2 as tables
from	django_tables2			import RequestConfig
from	django_tables2.utils		import A


# We need this to make links to this service itself.
try:
    from django.urls import reverse
except ImportError:
    print("FATAL IMPORT ERROR")
    exit(-3)



#########################################################    
##### BASE CLASSES FOR MONITOR AND DETAIL TABLES ########
class DetailTable(tables.Table):
    attribute	= tables.Column()
    value	= tables.Column()
    class Meta:
        attrs	= {'class': 'paleblue'}

#--------------------------------------------------------
class MonitorTable(tables.Table):
    def set_site(self, site=''):
        self.site=site

    def makelink(self, what, key, value):
        return mark_safe('<a href="http://%s%s?%s=%s">%s</a>'
                         % (self.site, reverse(what), key, value, value))
        

#########################################################    
############### SUMMARY TABLES ##########################    
#########################################################    
# NOTE THAT WE INSTRUMENT SOME COLUMNS WHILE DECIDING TO#
# NOT DISPLAY THEM. THIS IS TEMPORARY/HISTORICAL        #
#########################################################    
class PilotTable(MonitorTable):
    def render_uuid(self,value):	return self.makelink('pilots',	'uuid',	value)
    def render_j_uuid(self,value):	return self.makelink('jobs',	'uuid',	value)
    def render_id(self,value):		return self.makelink('pilotdetail',
                                                             'pk', value)

    class Meta:
        model	= pilot
        attrs	= {'class': 'paleblue'}
        exclude	= ('uuid', 'j_uuid', )

#--------------------------------------------------------
class JobTable(MonitorTable):
    def render_uuid(self,value):	return self.makelink('jobs',	'uuid',	value)
    def render_p_uuid(self,value):	return self.makelink('pilots',	'uuid',	value)
    def render_id(self,value):		return self.makelink('jobdetail',
	                                                     'pk', value)
        
    class Meta:
        model = job
        attrs = {'class': 'paleblue'}
        exclude	= ('uuid', 'p_uuid', )
#--------------------------------------------------------
class DagTable(MonitorTable):
    def render_id(self,value):	return self.makelink('dagdetail', 'pk', value)
    def render_name(self,value):return self.makelink('dags', 'name', value)
        
    class Meta:
        model = dag
        attrs = {'class': 'paleblue'}

#--------------------------------------------------------
# Simpler inheritance (compared to jobs etc) is provisional
class DagVertexTable(tables.Table):
#    def render_id(self,value):	return self.makelink('dagdetail', 'pk', value)
#    def render_name(self,value):return self.makelink('dags', 'name', value)
        
    class Meta:
        model = dagVertex
        attrs = {'class': 'paleblue'}

#--------------------------------------------------------
# Simpler inheritance (compared to jobs etc) is provisional
class DagEdgeTable(tables.Table):
#    def render_id(self,value):	return self.makelink('dagdetail', 'pk', value)
#    def render_name(self,value):return self.makelink('dags', 'name', value)
        
    class Meta:
        model = dagEdge
        attrs = {'class': 'paleblue'}

######## REQUEST ROUTERS (SUMMARIES) ####################    
def pilots(request):
    return data_handler(request, 'pilots')

#--------------------------------------------------------
def jobs(request):
    return data_handler(request, 'jobs')
#--------------------------------------------------------
def workflows(request):
    return data_handler(request, 'workflows')
#--------------------------------------------------------
def dags(request):
    return data_handler(request, 'dags')

#########################################################    
def data_handler(request, what):
    uuid	= request.GET.get('uuid','')
    pk		= request.GET.get('pk','')
    name	= request.GET.get('name','')

    # FIXME -beautify the timestamp later -mxp-
    now		= datetime.datetime.now().strftime('%x %X')
    domain	= request.get_host()
    d		= dict(domain=domain, time=str(now))

    objects, t, aux1	= None, None, None
    template = 'universo.html'
    
    if(what=='pilots'):
        objects = pilot.objects
        if(uuid == '' and pk == ''):	t = PilotTable(objects.all())
        if(uuid != ''):			t = PilotTable(objects.filter(uuid=uuid))
        if(pk != ''):			t = PilotTable(objects.filter(pk=pk))

    if(what=='jobs'):
        objects = job.objects
        if(uuid == '' and pk == ''):	t = JobTable(objects.all())
        if(uuid != ''):			t = JobTable(objects.filter(uuid=uuid))
        if(pk != ''):			t = JobTable(objects.filter(pk=pk))

    if(what=='workflows' or what=='dags'): # FIXME
        objects = dag.objects
        if(pk != ''):			t = DagTable(objects.filter(pk=pk))
        if(name != ''):			t = DagTable(objects.filter(name=name))
        if(pk == '' and name == ''):	t = DagTable(objects.all())
        
    t.set_site(domain)
    RequestConfig(request).configure(t)
    d['table']	= t # reference to "jobs" or "pilots" table, depending on the argument
    d['title']	= what
    
    return render(request, template, d)

########## REQUEST ROUTERS (DETAILS) ####################    
def jobdetail(request):
    return detail_handler(request, 'job')
#--------------------------------------------------------
def pilotdetail(request):
    return detail_handler(request, 'pilot')
#--------------------------------------------------------
def dagdetail(request):
    return detail_handler(request, 'dag')

#########################################################    
def detail_handler(request, what):
    pk 		= request.GET.get('pk','')
    domain	= request.get_host()

    # FIXME -beautify the timestamp later -mxp-
    now		= datetime.datetime.now().strftime('%x %X')
    d		= dict(domain=domain, time=str(now))

    template, objects, aux1 = None, None, None
    
    template = 'detail.html'
    
    if(what=='job'):
        d['title']	= what
        objects		= job.objects

    if(what=='pilot'):
        d['title']	= what
        objects = pilot.objects

    if(what=='dag'):
        objects = dag.objects
        theDag = objects.get(pk=pk)
        theDagName = theDag.name
        aux1 = DagVertexTable(dagVertex.objects.filter(dag=theDagName))
        aux2 = DagEdgeTable(dagEdge.objects.filter(dag=theDagName))
        d['title']	= what+' name: '+theDagName
                             
    dicto	= model_to_dict(objects.get(pk=pk))
    data	= []


    for a in dicto.keys(): data.append({'attribute': a, 'value': dicto[a]})

    t = DetailTable(data)
    RequestConfig(request).configure(t)
    d['detail'] = t

    # FIXME - admittedly hacky but we best improve a more final version
    if(aux1):
        d['aux1'] = aux1
        d['aux1title'] = 'Vertices for '+theDagName
    if(aux2):
        d['aux2'] = aux2
        d['aux2title'] = 'Edges for '+theDagName

    return render(request, template, d)


#########################################################    
# just something for later - advanced tables:
# from django.views.generic.base import TemplateView
#
# for later:  data = serializers.serialize('json', [ p, ])
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

# handling time and time difference etc
# yest = datetime.datetime.now() - timedelta(days=1)
#        for o in objects.filter(ts_lhb__gte=yest):
#            print(o.ts_lhb)
