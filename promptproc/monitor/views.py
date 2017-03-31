
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
from django.http			import HttpResponseRedirect

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
from workflows.models			import workflow

# tables2 machinery
import	django_tables2 as tables
from	django_tables2			import RequestConfig
from	django_tables2.utils		import A



# The tables are defined separately
from .monitorTables import *

# TWEAK
from django import forms

class pilotSelector(forms.Form):
    PILOT_STATES = [('all', 'All'), ('stopped', 'Stopped'), ('no jobs', 'No Jobs'),]
    pilotStates = forms.MultipleChoiceField(label='Pilot States (select one)',
                                            required=False,
#                                            widget=forms.RadioSelect(),
                                            widget=forms.CheckboxSelectMultiple,
                                            choices=PILOT_STATES,)
# END TWEAK


#########################################################    
# general request handler for summary type of a table
def data_handler(request, what):

    uuid	= request.GET.get('uuid','')
    wfuuid	= request.GET.get('wfuuid','')
    pk		= request.GET.get('pk','')
    name	= request.GET.get('name','')
    state	= request.GET.get('state','')
    host	= request.GET.get('host','')
    
    domain	= request.get_host()

    # FIXME -beautify the timestamp later -mxp-
    now		= datetime.datetime.now().strftime('%x %X')+' '+timezone.get_current_timezone_name()
    d		= dict(domain=domain, time=str(now))

    objects, t, aux1	= None, None, None
    template = 'universo.html'
    selector = None
   
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

        if request.method == 'POST':
            selector = pilotSelector(request.POST)
#            print(selector['pilotStates'])

            if selector.is_valid():
                # process the data in form.cleaned_data as required
                # ...
                # redirect to a new URL:
                selectedStates = selector.cleaned_data['pilotStates']
                print(selector.cleaned_data['pilotStates'])
                if len(selectedStates):
                    state = selectedStates[0]
                    if(state=='all'): return HttpResponseRedirect('/monitor/pilots')
                    return HttpResponseRedirect('/monitor/pilots?state=%s' % state)
                else:
                    return HttpResponseRedirect('/monitor/pilots')

        if(state!=''):
            selector = pilotSelector(initial={'pilotStates':[state,]})
        else:
            selector = pilotSelector(initial={'pilotStates':['all',]})
            
        objects = pilot.objects
        if(uuid == '' and pk == ''):	t = PilotTable(objects.all())
        if(uuid != ''):			t = PilotTable(objects.filter(uuid=uuid))
        if(pk != ''):			t = PilotTable(objects.filter(pk=pk))

        # FIXME - multiple filters needed
        if(state != ''):		t = PilotTable(objects.filter(state=state))
        if(host  != ''):		t = PilotTable(objects.filter(host=host))
        
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
    d['N']	= objects.count()
    d['selector'] = selector
    
    return render(request, template, d)

#########################################################    
# general request handler for detail type of a table
def detail_handler(request, what):
    pk 		= request.GET.get('pk','')
    name 	= request.GET.get('name','')
    o_uuid 	= request.GET.get('uuid','')
    domain	= request.get_host()

    # FIXME -beautify the timestamp later -mxp-
    now		= datetime.datetime.now().strftime('%x %X')
    d		= dict(domain=domain, time=str(now))

    template, objects, aux1, aux2 = None, None, None, None
    
    theName = ''

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
        
    if(what=='dag'):
        theName = 'Not found'
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
                             
    if(what=='workflow'):
        theName = 'Not found'
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
    if(pk!=''):
        try:
            dicto = model_to_dict(objects.get(pk=pk))
        except:
            return HttpResponse("%s pk '%s' not found" % (what, pk))
            
    if(name!=''):
        try:
            dicto = model_to_dict(objects.get(name=name))
        except:
            return HttpResponse("%s name '%s' not found" % (what, name))
            
    if(o_uuid!=''):
        try:
            dicto = model_to_dict(objects.get(uuid=o_uuid))
        except:
            return HttpResponse("%s uuid '%s' not found" % (what, o_uuid))
    
    data	= []


    # FIXME -- all this chaff to get special treatment for job uuid.
    # Need to rethink.
    for a in dicto.keys():
        if(a!='j_uuid'):
            data.append({'attribute': a, 'value': dicto[a]})
        else:
            x = mark_safe('<a href="http://%s/monitor/%s?%s=%s">%s</a>'
                         % (domain, 'jobdetail', 'uuid',dicto[a], dicto[a]))
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
