
#########################################################
#                      MONITOR                          #
#########################################################
# TZ-awarewness:					#
# The following is not TZ-aware: datetime.datetime.now()#
# so we are using timezone.now() where needed		#
#########################################################

# python utiility classes
import os
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

from logic.models			import service

# tables2 machinery
import	django_tables2 as tables
from	django_tables2			import RequestConfig
from	django_tables2.utils		import A



# The tables are defined separately
from .monitorTables import *

from django import forms

# For choice fields, first element is value, second is the label in the dropdown list
# ('All', 'All')
USERCHOICES	= [] # will be aurmented with info from the settings
JOBTYPECHOICES	= [] # ditto

PAGECHOICES	= [('25','25'), ('50','50'), ('100','100'), ('200','200'),('400','400'),]

SELECTORS	= {
    'pilot':
    {'stateLabel':'Pilot States',
     'states':[
         ('all',	'All'),		('active',	'Active'),	('running',	'Running'),	('stopped',	'Stopped'),
         ('timeout',	'Timed out'),	('no jobs',	'No Jobs'),	('DB lock',	'DB lock'),
     ],
     'userselector': None,
     'gUrl':'/monitor/pilots',
     'qUrl':'/monitor/pilots?',
     'table':'PilotTable',
    },
    
    'job':
    {'stateLabel':'Job States',
     'states':[
         ('all',	'All'),		('template',	'Template'),	('defined',	'Defined'),	('running',	'Running'),
         ('finished','Finished'),	('pilotTO','Pilot Timed Out'),
     ],
     'userselector': True,
     'typeselector': True,
     'timeselector': 'timeselector',
     'gUrl':'/monitor/jobs',
     'qUrl':'/monitor/jobs?',
     'table':'JobTable',
    },
    
    'workflow':
    {'stateLabel':'Workflow States',
     'states':[
         ('all',	'All'),         ('template',	'Template'),	('defined',	'Defined'),
         ('running',	'Running'),	('finished','Finished'),
     ],
     'userselector': 'userselector',
     'gUrl':'/monitor/workflows',
     'qUrl':'/monitor/workflows?state=%s',
     'table':'WfTable',
    },
    
    'site':	{'userselector': None,	'table': 'SiteTable',    },
    
    'dataset':	{'userselector': None,	'table': 'DataTable',    },
    
    'datatype':	{'userselector': None,	'table': 'DataTypeTable',},
    
    'dag':	{'userselector': None, },
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
class dropDownGeneric(forms.Form):
    def __init__(self, *args, **kwargs):
       self.label	= kwargs.pop('label')
       self.choices	= kwargs.pop('choices')
       self.tag		= kwargs.pop('tag')
       self.fieldname	= self.tag # 'choice'
       
       super(dropDownGeneric, self).__init__(*args, **kwargs)
       
       self.fields[self.fieldname] = forms.ChoiceField(choices = self.choices, label = self.label)

    def handleDropSelector(self):
        selection = self.cleaned_data[self.fieldname]
        if(selection=='All'):
            return ''
        else:
            return self.tag+'='+selection+'&'

#########################################################    
# general request handler for summary type of a table
def data_handler(request, what):
    dqm_domain	= settings.SITE['dqm_domain']
    dqm_host	= settings.SITE['dqm_host']



    # this is likely provisional - initialization from the local config file
    p3s_users	= settings.SITE['p3s_users']
    p3s_jobtypes= settings.SITE['p3s_jobtypes']
    
    userlist	= p3s_users.split(',')
    jobtypes	= p3s_jobtypes.split(',')
    #----------------------------------------------
    template = 'universo.html'

    uuid	= request.GET.get('uuid','')
    wfuuid	= request.GET.get('wfuuid','')
    pk		= request.GET.get('pk','')
    name	= request.GET.get('name','')
    state	= request.GET.get('state','')
    jobtype	= request.GET.get('jobtype','')
    user	= request.GET.get('user','')
    host	= request.GET.get('host','')
    perpage	= request.GET.get('perpage','25')

    states = ['all',]
    if(state != ''): states = state.split(',')

    initUser=user
    if(user==''): initUser='All'
        
    initJobType=jobtype
    if(jobtype==''): initJobType='All'
        
    domain	= request.get_host()

    now		= datetime.datetime.now().strftime('%x %X')+' '+timezone.get_current_timezone_name() # beautify later
    d		= dict(domain=domain, dqm_domain=dqm_domain, dqm_host=dqm_host, time=str(now))

    objects, t, Nfilt						= None, None, None
    stateSelector, perPageSelector, userSelector, typeSelector	= None, None, None, None

    t = None  # placeholder for the main table object
    
    if(what=='service'):
        objects = eval(what).objects
        t = ServiceTable(objects.all())

        # return HttpResponse(str(f))
    
    if(what in ['job', 'pilot', 'workflow']):
        
        uTupleList = []
        for u in userlist: uTupleList.append((u,u))
        USERCHOICES = uTupleList
            
        jTupleList = []
        for jt in jobtypes: jTupleList.append((jt,jt))
        JOBTYPECHOICES = jTupleList
        
        selector = SELECTORS[what] # IMPORTANT
        
        q = '' # stub for the query
        
        chosenTable=eval(selector['table'])

        timeselector = 'TBD'
#----------

        # HANDLE USER'S SELECTIONS HERE
        if request.method == 'POST':
            stateSelector = boxSelector(request.POST, what=what)
            if stateSelector.is_valid(): q += stateSelector.handleBoxSelector()

            try:
                if(selector['userselector']):
                    userSelector = dropDownGeneric(request.POST, label='User', choices=USERCHOICES, tag='user')
                    if userSelector.is_valid():
                        q += userSelector.handleDropSelector()
            except:
                pass

            try:
                if(selector['typeselector']):
                    typeSelector = dropDownGeneric(request.POST, label='Type', choices=JOBTYPECHOICES, tag='jobtype')
                    if typeSelector.is_valid():
                        q += typeSelector.handleDropSelector()
            except:
                pass

            # try:
            #     if(selector['timeselector'] is not None):
            #         timeselector = dropDownGeneric(request.POST, label='Time', choices=(('1','100'),('2','200'),), tag='time')
            #         # if userSelector.is_valid(): q += userSelector.handleDropSelector()
            # except:
            #     pass


            perPageSelector	= dropDownGeneric(request.POST, initial={'perpage':perpage}, label='# per page', choices = PAGECHOICES, tag='perpage')
            if perPageSelector.is_valid(): q += perPageSelector.handleDropSelector()
                    
            return makeQuery(what, q) # will go and get the query results...

        #################################################
        ###### IF NOT RESPONSE TO QUERY, ################
        ###### BUILD THE DEFAULT PAGE    ################
        #################################################
        
        stateSelector	= boxSelector(initial={'stateChoice': states}, what=what)
        
        try:
            if(selector['userselector']): userSelector	= dropDownGeneric(initial={'user':initUser},	label='User',	choices = USERCHOICES, tag='user')
        except:
            pass
            
        try:
            if(selector['typeselector']): typeSelector	= dropDownGeneric(initial={'jobtype':'All'},	label='Type',	choices = JOBTYPECHOICES, tag='jobtype')
        except:
            pass
            
        perPageSelector	= dropDownGeneric(initial={'perpage':perpage},	label='# per page',	choices = PAGECHOICES, tag='perpage')

        
#        timeselector	= dropDownGeneric(label='Time limit', choices=(('1','1h'),('2','2h'),), tag='time') # work in progress


        objects = eval(what).objects
        # there is a catch-all below, so this default is not necessary (I guess)
        # if(uuid == '' and pk == '' and wfuuid == '' and state == '' and user == ''): t = chosenTable(objects.all())
        

        # Don't forget to update this filter part as you add functionality!
        kwargs = {}
        if(uuid		!= ''): kwargs['uuid']		= uuid
        if(wfuuid	!= ''):	kwargs['wfuuid']	= wfuuid
        if(pk		!= ''): kwargs['pk']		= pk
        if(name		!= ''): kwargs['name']		= name
        if(user		!= ''): kwargs['user']		= user
        if(jobtype	!= ''): kwargs['jobtype']	= jobtype
        if(state	!= ''): kwargs['state__in']	= states # notice multiple values
        
        try:
            objs = objects.filter(**kwargs)
            Nfilt = objs.count()
            t = chosenTable(objs)
        except:
            pass
            
        if(t is None):t = chosenTable(objects.all()) # FIXME - check kwargs instead

    if(what in ['dataset', 'site', 'datatype']):
        selector = SELECTORS[what] # IMPORTANT
        chosenTable=eval(selector['table'])
        objects = eval(what).objects
        t = chosenTable(objects.all())

    if(what=='dag'):
        objects = dag.objects
        if(pk != ''):			objs = objects.filter(pk=pk)
        if(name != ''):			objs = objects.filter(name=name)
        if(pk == '' and name == ''):	objs = objects.all()
        Nfilt = objs.count()
        t = DagTable(objs)
        
    t.set_site(domain)

    RequestConfig(request, paginate={'per_page': int(perpage)}).configure(t)
    
    Ntot = objects.count()
    
    d['table']	= t # reference to "jobs" or "pilots" table, depending on the argument
    d['title']	= what
    d['stats']	= 'test'
    d['N']	= Ntot
    if(Nfilt is None): Nfilt = Ntot
    d['Nfilt']  = Nfilt
    d['host']	= settings.HOSTNAME

    selectors = []
    
    if(stateSelector):	selectors.append(stateSelector)
    if(userSelector):	selectors.append(userSelector)
    if(typeSelector):	selectors.append(typeSelector)
    if(perPageSelector):selectors.append(perPageSelector)

    d['selectors'] = selectors

    return render(request, template, d)

#########################################################    
# general request handler for detail type of a table
def detail_handler(request, what):
    dqm_domain	= settings.DQM_DOMAIN
    dqm_host	= settings.DQM_HOST

    pk 		= request.GET.get('pk','')
    name 	= request.GET.get('name','')
    o_uuid 	= request.GET.get('uuid','')
    domain	= request.get_host()
    host	= request.GET.get('host','')

    # FIXME -beautify the timestamp later -mxp-
    now		= datetime.datetime.now().strftime('%x %X')
    d		= dict(domain=domain, time=str(now))
    d		= dict(domain=domain, dqm_domain=dqm_domain, dqm_host=dqm_host, time=str(now))
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
        d['uuid']	= my_pilot.uuid

        
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

    # FIXME - make a nice "not found" page for all of these cases
    
    if(pk!=''):
        try:
            theObj = objects.get(pk=pk)
            try:
                d['uuid'] = theObj.uuid
            except:
                pass
            
            dicto = model_to_dict(theObj)
        except:
            return HttpResponse("%s pk '%s' not found" % (what, pk))
            
    if(name!=''):
        try:
            dicto = model_to_dict(objects.get(name=name))
        except:
            return HttpResponse("%s name '%s' not found" % (what, name))
            
    if(o_uuid!=''):
        try:
            d['uuid'] = o_uuid
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
def filesystem(request):
    l = os.listdir(settings.SITE['p3s_input'])
    return HttpResponse(l)
    
#########################################################    

# if selector.is_valid():
#     selectedStates = selector.cleaned_data['stateChoice']
#     if len(selectedStates):
#         state = selectedStates[0]
#         if(state=='all'): return HttpResponseRedirect('/monitor/pilots')
#         return HttpResponseRedirect('/monitor/pilots?state=%s' % state)
#     else:
#         return HttpResponseRedirect('/monitor/pilots')
######################
# class dropDown(forms.Form):
#     def __init__(self, *args, **kwargs):
#        self.label = kwargs.pop('label')
#        super(dropDown, self).__init__(*args, **kwargs)
       
#        self.fields['dropChoice'] = forms.ChoiceField(choices = CHOICES, label = self.label)

#     def handleDropSelector(self):
#         selectedUser = self.cleaned_data['dropChoice']
#         if(selectedUser=='All'):
#             return ''
#         else:
#             return 'user='+selectedUser+'&'

# ######################
# class dropDownPage(forms.Form):
#     def __init__(self, *args, **kwargs):
#        self.label = kwargs.pop('label')
#        super(dropDownPage, self).__init__(*args, **kwargs)
       
#        self.fields['dropChoicePage'] = forms.ChoiceField(choices = PAGECHOICES, label = self.label)

#     def handleDropSelector(self):
#         selectedNumber = self.cleaned_data['dropChoicePage']
#         return 'perpage='+selectedNumber+'&'

