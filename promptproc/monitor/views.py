
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
from django.utils.timezone		import activate
from django.http			import HttpResponse
from django.views.decorators.csrf	import csrf_exempt
from django.core			import serializers
from django.utils.safestring		import mark_safe
from django.forms.models		import model_to_dict
from django.conf			import settings

# Models used in the application:
from jobs.models			import job
from data.models			import dataset, datatype
from pilots.models			import pilot
from workflows.models			import dag, dagVertex, dagEdge
from workflows.models			import workflow, wfVertex, wfEdge

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
    
    def set_site(self, site=''):
        self.site=site
    class Meta:
        attrs	= {'class': 'paleblue'}

#--------------------------------------------------------
class MonitorTable(tables.Table):
    def set_site(self, site=''):
        self.site=site

    def makelink(self, what, key, value):
        return mark_safe('<a href="http://%s%s?%s=%s">%s</a>'
                         % (self.site, reverse(what), key, value, value))

    def renderDateTime(self, dt): # common format defined here.
        return timezone.localtime(dt).strftime(settings.TIMEFORMAT)
        

#########################################################    
############### SUMMARY TABLES ##########################    
#########################################################    
# NOTE THAT WE INSTRUMENT SOME COLUMNS WHILE DECIDING TO#
# NOT DISPLAY THEM. THIS IS TEMPORARY/HISTORICAL        #
#########################################################    
class JobTable(MonitorTable):

    ts_def	= tables.Column(verbose_name='defined')
    ts_dis	= tables.Column(verbose_name='dispatched')
    ts_sta	= tables.Column(verbose_name='started')
    ts_sto	= tables.Column(verbose_name='stopped')
    jobtype	= tables.Column(verbose_name='type')
    priority	= tables.Column(verbose_name='Pri.')
    timelimit	= tables.Column(verbose_name='t.limit')

    def render_uuid(self,value):	return self.makelink('jobs',	'uuid',	value)
    def render_p_uuid(self,value):	return self.makelink('pilots',	'uuid',	value)
    def render_id(self,value):		return self.makelink('jobdetail','pk',	value)
    def render_ts_def(self, value):	return self.renderDateTime(value)
    def render_ts_dis(self, value):	return self.renderDateTime(value)
    def render_ts_sta(self, value):	return self.renderDateTime(value)
    def render_ts_sto(self, value):	return self.renderDateTime(value)
    
    class Meta:
        model = job
        attrs = {'class': 'paleblue'}
        exclude	= ('p_uuid', )
#--------------------------------------------------------
class DataTable(MonitorTable):
    def render_uuid(self,value):	return self.makelink('datadetail','uuid', value)
    def render_wfuuid(self,value):	return self.makelink('wfdetail','uuid', value)
    def render_datatype(self,value):	return self.makelink('datatypes','', value)

    class Meta:
        model = dataset
        attrs = {'class': 'paleblue'}
#--------------------------------------------------------
class DataTypeTable(MonitorTable):

    class Meta:
        model = datatype
        attrs = {'class': 'paleblue'}
#--------------------------------------------------------
class PilotTable(MonitorTable):
    ts_cre	= tables.Column(verbose_name='created')
    ts_reg	= tables.Column(verbose_name='registered')
    ts_lhb	= tables.Column(verbose_name='last heartbeat')
    jobcount	= tables.Column(verbose_name='jobs')
    
    def render_uuid(self,value):	return self.makelink('pilots',	'uuid',	value)
    def render_j_uuid(self,value):	return self.makelink('jobs',	'uuid',	value)
    def render_id(self,value):		return self.makelink('pilotdetail','pk', value)

    def render_ts_cre(self, value):	return self.renderDateTime(value)
    def render_ts_reg(self, value):	return self.renderDateTime(value)
    def render_ts_lhb(self, value):	return self.renderDateTime(value)

    class Meta:
        model	= pilot
        attrs	= {'class': 'paleblue'}
        exclude	= ('uuid', 'j_uuid', )

#--------------------------------------------------------
class DagTable(MonitorTable):
    # def render_id(self,value):	return self.makelink('dagdetail', 'pk', value)


    def render_ts_def(self, value):	return self.renderDateTime(value)
    
    ts_def	= tables.Column(verbose_name='defined')
    nvertices	= tables.Column(verbose_name='nvert')
    
    def render_name(self,value):return self.makelink('dagdetail', 'name', value)
        
    class Meta:
        model = dag
        attrs = {'class': 'paleblue'}

#--------------------------------------------------------
class WfTable(MonitorTable):
    # FIXME rendering later
    # def render_id(self,value):	return self.makelink('dagdetail', 'pk', value)


    def render_ts_def(self, value):	return self.renderDateTime(value)
    
    ts_def	= tables.Column(verbose_name='defined')
    dag		= tables.Column(verbose_name='DAG')
    
    def render_uuid(self,value):return self.makelink('wfdetail', 'uuid', value)
    def render_dag(self,value):return self.makelink('dagdetail', 'name', value)
        
    class Meta:
        model = workflow
        attrs = {'class': 'paleblue'}
        # we actually want that: exclude	= ('uuid', )

#--------------------------------------------------------
# Simpler inheritance (compared to jobs etc) is provisional
class DagVertexTable(tables.Table):
#    def render_id(self,value):	return self.makelink('dagdetail', 'pk', value)
#    def render_name(self,value):return self.makelink('dags', 'name', value)
        
    class Meta:
        model = dagVertex
        exclude = ('dag',)
        attrs = {'class': 'paleblue'}

#--------------------------------------------------------
# Simpler inheritance (compared to jobs etc) is provisional
class DagEdgeTable(tables.Table):
#    def render_id(self,value):	return self.makelink('dagdetail', 'pk', value)
#    def render_name(self,value):return self.makelink('dags', 'name', value)
        
    class Meta:
        model = dagEdge
        exclude = ('dag',)
        attrs = {'class': 'paleblue'}

#--------------------------------------------------------
# Simpler inheritance (compared to jobs etc) is provisional
class WfVertexTable(tables.Table):
#    def render_id(self,value):	return self.makelink('dagdetail', 'pk', value)
#    def render_name(self,value):return self.makelink('dags', 'name', value)
        
    class Meta:
        model = wfVertex
        exclude = ('wf','wfuuid',)
        attrs = {'class': 'paleblue'}

#--------------------------------------------------------
# Simpler inheritance (compared to jobs etc) is provisional
class WfEdgeTable(tables.Table):
#    def render_id(self,value):	return self.makelink('dagdetail', 'pk', value)
#    def render_name(self,value):return self.makelink('dags', 'name', value)
        
    class Meta:
        model = wfEdge
        exclude = ('wf','wfuuid',)
        attrs = {'class': 'paleblue'}

######## REQUEST ROUTERS (SUMMARIES) ####################    
def jobs(request):
    return data_handler(request, 'jobs')
#--------------------------------------------------------
def data(request):
    return data_handler(request, 'data')
#--------------------------------------------------------
def datatypes(request):
    return data_handler(request, 'datatypes')
#--------------------------------------------------------
def pilots(request):
    return data_handler(request, 'pilots')
#--------------------------------------------------------
def workflows(request):
    return data_handler(request, 'workflows')
#--------------------------------------------------------
def dags(request):
    return data_handler(request, 'dags')

#########################################################    
def data_handler(request, what):
    uuid	= request.GET.get('uuid','')
    wfuuid	= request.GET.get('wfuuid','')
    pk		= request.GET.get('pk','')
    name	= request.GET.get('name','')

    # FIXME -beautify the timestamp later -mxp-
    now		= datetime.datetime.now().strftime('%x %X')+' '+timezone.get_current_timezone_name()
    domain	= request.get_host()
    d		= dict(domain=domain, time=str(now))

    objects, t, aux1	= None, None, None
    template = 'universo.html'
    
    if(what=='jobs'):
        objects = job.objects
        if(uuid == '' and pk == '' and wfuuid == ''):	t = JobTable(objects.all())
        
        if(uuid != ''):			t = JobTable(objects.filter(uuid=uuid))
        if(wfuuid != ''):		t = JobTable(objects.filter(wfuuid=wfuuid))
        if(pk != ''):			t = JobTable(objects.filter(pk=pk))

    if(what=='data'):
        objects = dataset.objects
        t = DataTable(objects.all())

    if(what=='datatypes'):
        objects = datatype.objects
        t = DataTypeTable(objects.all())

    if(what=='pilots'):
        objects = pilot.objects
        if(uuid == '' and pk == ''):	t = PilotTable(objects.all())
        if(uuid != ''):			t = PilotTable(objects.filter(uuid=uuid))
        if(pk != ''):			t = PilotTable(objects.filter(pk=pk))

    if(what=='dags'):
        objects = dag.objects
        if(pk != ''):			t = DagTable(objects.filter(pk=pk))
        if(name != ''):			t = DagTable(objects.filter(name=name))
        if(pk == '' and name == ''):	t = DagTable(objects.all())
        
    if(what=='workflows'):
        objects = workflow.objects
        if(pk != ''):			t = WfTable(objects.filter(pk=pk))
        if(name != ''):			t = WfTable(objects.filter(name=name))
        if(pk == '' and name == ''):	t = WfTable(objects.all())
        
    t.set_site(domain)
    RequestConfig(request).configure(t)
    d['table']	= t # reference to "jobs" or "pilots" table, depending on the argument
    d['title']	= what
    
    return render(request, template, d)

########## REQUEST ROUTERS (DETAILS) ####################    
def jobdetail(request):
    return detail_handler(request, 'job')
#--------------------------------------------------------
def datadetail(request):
    return detail_handler(request, 'data')
#--------------------------------------------------------
def pilotdetail(request):
    return detail_handler(request, 'pilot')
#--------------------------------------------------------
def dagdetail(request):
    return detail_handler(request, 'dag')

#--------------------------------------------------------
def wfdetail(request):
    return detail_handler(request, 'workflow')

#########################################################    
def detail_handler(request, what):
    pk 		= request.GET.get('pk','')
    name 	= request.GET.get('name','')
    o_uuid 	= request.GET.get('uuid','')
    domain	= request.get_host()

    # FIXME -beautify the timestamp later -mxp-
    now		= datetime.datetime.now().strftime('%x %X')
    d		= dict(domain=domain, time=str(now))

    template, objects, aux1, aux2 = None, None, None, None
    
    
    if(what=='job'):
        template = 'detail.html'
        d['title']	= what
        objects		= job.objects
        
    if(what=='data'):
        template = 'detail.html'
        d['title']	= what
        objects		= dataset.objects

    if(what=='pilot'):
        template = 'detail.html'
        d['title']	= what
        objects = pilot.objects
        
    theName = 'Not found'
    if(what=='dag'):
        template = 'detail2.html'
        objects = dag.objects
        try:
            theDag = objects.get(name=name)
            theName = theDag.name
        except:
            return HttpResponse("DAG '%s' not found" % name)

        aux1 = DagVertexTable(dagVertex.objects.filter(dag=theName))
        aux2 = DagEdgeTable(dagEdge.objects.filter(dag=theName))
        d['title']	= what+' name: '+theName
                             
    theName = 'Not found'
    if(what=='workflow'):
        template = 'detail2.html'
        objects = workflow.objects
        try:
            theWF = objects.get(uuid=o_uuid)
            theName = theWF.name
        except:
            return HttpResponse("Workflow '%s' not found" % o_uuid)
        
        aux1 = JobTable(job.objects.filter(wfuuid=o_uuid))
        aux1.set_site(domain)
        
        aux2 = DataTable(dataset.objects.filter(wfuuid=o_uuid))
        aux2.set_site(domain)
        d['title']	= what+' name: '+theName+', uuid: '+o_uuid
                             
    dicto = {}
    if(pk!=''):		dicto	= model_to_dict(objects.get(pk=pk))
    if(name!=''):	dicto	= model_to_dict(objects.get(name=name))
    if(o_uuid!=''):	dicto	= model_to_dict(objects.get(uuid=o_uuid))
    data	= []

    for a in dicto.keys():
        if(a!='j_uuid'):
            data.append({'attribute': a, 'value': dicto[a]})
        else:
            x = mark_safe('<a href="http://%s%s?%s=%s">%s</a>'
                         % (domain, reverse(jobdetail), 'uuid',dicto[a], dicto[a]))
            data.append({'attribute': a, 'value': x})

    t = DetailTable(data)
    t.set_site(domain)
    RequestConfig(request).configure(t)
    d['detail'] = t

    # FIXME - admittedly hacky but we best improve a more final version
    if(aux1):
        d['aux1'] = aux1
        d['aux1title'] = 'Jobs for "'+theName+'"'
    if(aux2):
        d['aux2'] = aux2
        d['aux2title'] = 'Data for "'+theName+'"'

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
#    print(timezone.get_current_timezone_name())
#        aux1 = WfVertexTable(wfVertex.objects.filter(wfuuid=o_uuid))
        #        aux2 = WfEdgeTable(wfEdge.objects.filter(wfuuid=o_uuid))
