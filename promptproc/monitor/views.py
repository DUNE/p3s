
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
    {'label':'Pilot States',
     'states':[
         ('all',	'All'),
         ('active',	'Active'),
         ('running',	'Running'),
         ('stopped',	'Stopped'),
         ('timeout',	'Timed out'),
         ('no jobs',	'No Jobs'),
     ],
     'gUrl':'/monitor/pilots',
     'qUrl':'/monitor/pilots?state=%s',
     'table':'PilotTable',
    },
    'job':
    {'label':'Job States',
     'states':[
         ('all',	'All'),
         ('template',	'Template'),
         ('defined',	'Defined'),
         ('running',	'Running'),
         ('finished','Finished'),
         ('pilotTO','Pilot Timed Out'),
     ],
     'gUrl':'/monitor/jobs',
     'qUrl':'/monitor/jobs?state=%s&user=%s',
     'table':'JobTable',
    },
    'workflow':
    {'label':'Workflow States',
     'states':[
         ('all',	'All'),
         ('template',	'Template'),
         ('defined',	'Defined'),
         ('running',	'Running'),
         ('finished','Finished'),
     ],
     'gUrl':'/monitor/workflows',
     'qUrl':'/monitor/workflows?state=%s',
     'table':'WfTable',
    },
}

# 
#########################################################    
class stateSelector(forms.Form):

    def __init__(self, *args, **kwargs):
       self.what = kwargs.pop('what')

       super(stateSelector, self).__init__(*args, **kwargs)
       self.fields['stateChoice'].choices	= SELECTORS[self.what]['states']
       self.fields['stateChoice'].label		= SELECTORS[self.what]['label']
       self.gUrl				= SELECTORS[self.what]['gUrl']
       self.qUrl				= SELECTORS[self.what]['qUrl']

    def handleStateSelector(self, user=''):
        selectedStates = self.cleaned_data['stateChoice']
        if len(selectedStates):
            if('all' in selectedStates):
                return HttpResponseRedirect(self.gUrl)
            
            return HttpResponseRedirect(self.qUrl % (",".join(selectedStates), user))

        return HttpResponseRedirect(self.gUrl)
           
    stateChoice = forms.MultipleChoiceField(label='DUMMY',
                                            required=False,
                                            widget=forms.CheckboxSelectMultiple,
                                            choices=[('place', 'holder'),])

######################
class userSelector(forms.Form):
    userChoice = forms.ChoiceField(choices = CHOICES, label = "User")

    def handleUserSelector(self):
        selectedUser = self.cleaned_data['userChoice']
        if(selectedUser=='All'): selectedUser=''
        return selectedUser


        
#    def __init__(self, *args, **kwargs):

#        super(userSelector, self).__init__(*args, **kwargs)
#        self.fields['users'].choices = ['maxim','brett']
#        self.fields['users'].lable = "User"
    

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

    objects, t, aux1	= None, None, None
    template = 'universo.html'
    selector = None

    # FIXME - now that multiple selectors work, need to init the checkboxes correctly
   
    if(what in ['job', 'pilot', 'workflow']):
        t = None # placeholder for the table object
        
        x=eval(SELECTORS[what]['table'])
        
        if request.method == 'POST':
            selector = stateSelector(request.POST, what=what)
            if selector.is_valid():
                users = userSelector(request.POST)
                selectedUser = ''
                if users.is_valid(): selectedUser = users.handleUserSelector()
                return selector.handleStateSelector(selectedUser)

        if(state!=''): # from the HTTP request with exception of 'all'
            selector = stateSelector(initial={'stateChoice':[state,]}, what=what)
        else:
            selector = stateSelector(initial={'stateChoice':['all',]}, what=what)

        if(user!=''):
            userselector = userSelector()
        else:
            userselector = userSelector()


        objects = eval(what).objects
        if(uuid == '' and pk == '' and wfuuid == '' and state == '' and user == ''):
            t = x(objects.all())
        
        if(uuid		!= ''):		t = x(objects.filter(uuid=uuid))
        if(wfuuid	!= ''):		t = x(objects.filter(wfuuid=wfuuid))
        if(pk		!= ''):		t = x(objects.filter(pk=pk))
        if(name		!= ''):		t = x(objects.filter(name=name))
        if(state != '' and user == ''):	t = x(objects.filter(state__in=state.split(',')))
        if(state != '' and user != ''):	t = x(objects.filter(state__in=state.split(','), user=user))
        if(user  != ''):		t = x(objects.filter(user=user))
        
        if(t is None):			t = x(objects.all())
            
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
        if(pk != ''):			t = DagTable(objects.filter(pk=pk))
        if(name != ''):			t = DagTable(objects.filter(name=name))
        if(pk == '' and name == ''):	t = DagTable(objects.all())
       
    t.set_site(domain)
    RequestConfig(request).configure(t)
    d['table']	= t # reference to "jobs" or "pilots" table, depending on the argument
    d['title']	= what
    d['N']	= objects.count()
    d['selector'] = selector
    d['userselector'] = userselector
    
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
    
    theName = 'Not Found'
    objects = eval(what).objects

    if(what in ('job', 'dataset', 'pilot', 'site')):
        template = 'detail.html'
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
    if(aux2):
        d['aux2'] = aux2
        d['aux2title'] = 'Data for "'+theName+'"'

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
