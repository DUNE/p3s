
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
from sites.models			import site
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

from django import forms

# Users - first element is value, second is the label in the dropdown list
CHOICES = (('All', 'All'), ('maxim','maxim'), ('brett','brett'),)


SELECTORS	= {
    'pilot':
    {'stateLabel':'Pilot States',
     'states':[
         ('all',	'All'),
         ('active',	'Active'),
         ('running',	'Running'),
         ('stopped',	'Stopped'),
         ('timeout',	'Timed out'),
         ('no jobs',	'No Jobs'),
     ],
     'userselector': None,
     'gUrl':'/monitor/pilots',
     'qUrl':'/monitor/pilots?',
     'table':'PilotTable',
    },
    'job':
    {'stateLabel':'Job States',
     'states':[
         ('all',	'All'),
         ('template',	'Template'),
         ('defined',	'Defined'),
         ('running',	'Running'),
         ('finished','Finished'),
         ('pilotTO','Pilot Timed Out'),
     ],
     'userselector': 'userselector',
     'gUrl':'/monitor/jobs',
     'qUrl':'/monitor/jobs?',
     'table':'JobTable',
    },
    'workflow':
    {'stateLabel':'Workflow States',
     'states':[
         ('all',	'All'),
         ('template',	'Template'),
         ('defined',	'Defined'),
         ('running',	'Running'),
         ('finished','Finished'),
     ],
     'userselector': 'userselector',
     'gUrl':'/monitor/workflows',
     'qUrl':'/monitor/workflows?state=%s',
     'table':'WfTable',
    },
    'site':
    {'userselector': None,
    },
    'dataset':
    {'userselector': None,
    },
    'datatype':
    {'userselector': None,
    },
    'dag':
    {'userselector': None,
    },
}

#
def makeQuery(what, q=''):
    gUrl= SELECTORS[what]['gUrl']
    qUrl= SELECTORS[what]['qUrl']

    if(q==''):
        return HttpResponseRedirect(gUrl)
    
    return HttpResponseRedirect(qUrl+q)
#########################################################    
class boxSelector(forms.Form):

    def __init__(self, *args, **kwargs):
       self.what = kwargs.pop('what')

       super(boxSelector, self).__init__(*args, **kwargs)
       self.fields['stateChoice'].choices	= SELECTORS[self.what]['states']
       self.fields['stateChoice'].label		= SELECTORS[self.what]['stateLabel']

    def handleBoxSelector(self):
        selectedStates = self.cleaned_data['stateChoice']
        if len(selectedStates):
            if('all' in selectedStates):
                return ''
            else:
                return 'state='+",".join(selectedStates)+'&'
        return ''

    stateChoice = forms.MultipleChoiceField(label='DUMMY',
                                            required=False,
                                            widget=forms.CheckboxSelectMultiple,
                                            choices=[('place', 'holder'),])

######################
class dropDown(forms.Form):
    def __init__(self, *args, **kwargs):
       self.label = kwargs.pop('label')
       super(dropDown, self).__init__(*args, **kwargs)
       
       self.fields['dropChoice'] = forms.ChoiceField(choices = CHOICES, label = self.label)

    def handleDropSelector(self):
        selectedUser = self.cleaned_data['dropChoice']
        if(selectedUser=='All'):
            return ''
        else:
            return 'user='+selectedUser+'&'

#########################################################    
# general request handler for summary type of a table
def data_handler(request, what):

    uuid	= request.GET.get('uuid','')
    wfuuid	= request.GET.get('wfuuid','')
    pk		= request.GET.get('pk','')
    name	= request.GET.get('name','')
    state	= request.GET.get('state','')
    user	= request.GET.get('user','')
    host	= request.GET.get('host','')

    domain	= request.get_host()

    # FIXME -beautify the timestamp later -mxp-
    now		= datetime.datetime.now().strftime('%x %X')+' '+timezone.get_current_timezone_name()
    d		= dict(domain=domain, time=str(now))

    objects, t, aux1, selector1, selector2 = None, None, None, None, None
    template = 'universo.html'
    Nfilt    = None

    # FIXME - now that multiple selectors work, need to init the checkboxes correctly

    stateselector = None
    if(what in ['job', 'pilot', 'workflow']):
        t = None # placeholder for the table object
        q = ''
        x=eval(SELECTORS[what]['table'])
        
#----------
        if request.method == 'POST':
            stateselector = boxSelector(request.POST, what=what)
            if stateselector.is_valid():
                q += stateselector.handleBoxSelector()
                
            if(SELECTORS[what]['userselector'] is not None):
                userselector = dropDown(request.POST,label='User')
                if userselector.is_valid():
                    q += userselector.handleDropSelector()
            
            return makeQuery(what, q)
#----------


        if(state!=''): # from the HTTP request with exception of 'all'
            stateselector = boxSelector(initial={'stateChoice':[state,]}, what=what)
        else:
            stateselector = boxSelector(initial={'stateChoice':['all',]}, what=what)

        if(user!=''):
            userselector = dropDown(initial={'dropChoice':[user,]}, label='User')
        else:
            userselector = dropDown(label='User')


        objects = eval(what).objects
        if(uuid == '' and pk == '' and wfuuid == '' and state == '' and user == ''):
            t = x(objects.all())
        
        kwargs = {}
        if(uuid		!= ''): kwargs['uuid']	= uuid
        if(wfuuid	!= ''):	kwargs['wfuuid']= wfuuid
        if(pk		!= ''): kwargs['pk']	= pk
        if(name		!= ''): kwargs['name']	= name
        if(user		!= ''): kwargs['user']	= user
        if(state	!= ''): kwargs['state__in']=state.split(',')
        
        try:
            objs = objects.filter(**kwargs)
            Nfilt = objs.count()
            t = x(objs)
        except:
            pass
            
        if(t is None):t = x(objects.all()) # FIXME - check kwargs instead
            
    if(what=='dataset'):
        objects = dataset.objects
        t = DataTable(objects.all())

    if(what=='site'):
        objects = site.objects
        t = SiteTable(objects.all())

    if(what=='datatype'):
        objects = datatype.objects
        t = DataTypeTable(objects.all())

    if(what=='dag'):
        objects = dag.objects
        if(pk != ''):			objs = objects.filter(pk=pk)
        if(name != ''):			objs = objects.filter(name=name)
        if(pk == '' and name == ''):	objs = objects.all()
        Nfilt = objs.count()
        t = DagTable(objs)
        
    t.set_site(domain)
    RequestConfig(request).configure(t)

    Ntot = objects.count()
    
    d['table']	= t # reference to "jobs" or "pilots" table, depending on the argument
    d['title']	= what
    d['N']	= Ntot
    if(Nfilt is None): Nfilt = Ntot
    d['Nfilt']  = Nfilt
    d['host']	= settings.HOSTNAME

    if(stateselector is not None):
        d['selector1'] = stateselector
    if(SELECTORS[what]['userselector'] is not None):
        d['selector2'] = eval(SELECTORS[what]['userselector'])
    
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
    d['host']	= settings.HOSTNAME

    template, objects, aux1, aux2 = None, None, None, None
    
    theName	= 'Not Found'
    objects	= eval(what).objects

    if(what in ('job', 'dataset', 'site')):
        template = 'detail.html'
        d['title']	= what
        
    if(what=='pilot'):
        template = 'detail3.html'
        my_pilot = None
        
        try:
            my_pilot = objects.get(pk=pk)
        except:
            pass
        
        try:
            my_pilot = objects.get(uuid=o_uuid)
        except:
            pass

        if(my_pilot):
            pass
        else:
            return HttpResponse("pilot not found")
        
        aux1 = JobTable(job.objects.filter(p_uuid=my_pilot.uuid))
        aux1.set_site(domain)
        theName = 'pilot '+my_pilot.uuid
        d['title']	= what

        
    if(what=='dag'):
        template = 'detail2.html'
        try:
            theDag = objects.get(name=name)
            theName = theDag.name
        except:
            return HttpResponse("DAG '%s' not found" % name)

        aux1 = DagVertexTable(dagVertex.objects.filter(dag=theName))
        aux2 = DagEdgeTable(dagEdge.objects.filter(dag=theName))
        d['title']	= what+' name: '+theName
                             
    if(what=='workflow'):
        template = 'detail2.html'
        try:
            kwargs = {'uuid':o_uuid}
            found = objects.get(**kwargs)
            theName = found.name
        except:
            return HttpResponse("%s '%s' not found" % (what, o_uuid))
        
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


    # FIXME -- perhaps I can make it more OO
    for a in dicto.keys():
        if(a=='j_uuid'):
            x = mark_safe('<a href="http://%s/monitor/%s?%s=%s">%s</a>'
                         % (domain, 'jobdetail',	'uuid',	dicto[a], dicto[a]))
        elif(a=='p_uuid'):
            x = mark_safe('<a href="http://%s/monitor/%s?%s=%s">%s</a>'
                         % (domain, 'pilotdetail',	'uuid',	dicto[a], dicto[a]))
        elif(a=='jobs_done'): # we have created a separate table for the job list
            continue
        else:
            x = dicto[a]
            
        data.append({'attribute': a, 'value': x})

    t = DetailTable(data)
    t.set_site(domain)
    RequestConfig(request).configure(t)
    d['detail'] = t

    # FIXME - admittedly hacky but we best improve a more final version
    if(aux1):
        d['aux1'] = aux1
        d['aux1title'] = 'Jobs for "'+theName+'"'
        RequestConfig(request).configure(aux1)
    if(aux2):
        d['aux2'] = aux2
        d['aux2title'] = 'Data for "'+theName+'"'
        RequestConfig(request).configure(aux2)

    return render(request, template, d)
###################################################################################
# if selector.is_valid():
#     selectedStates = selector.cleaned_data['stateChoice']
#     if len(selectedStates):
#         state = selectedStates[0]
#         if(state=='all'): return HttpResponseRedirect('/monitor/pilots')
#         return HttpResponseRedirect('/monitor/pilots?state=%s' % state)
#     else:
#         return HttpResponseRedirect('/monitor/pilots')
