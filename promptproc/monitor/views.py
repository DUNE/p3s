
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

from logic.models			import service, user
from logic.models			import user as p3sUser

# tables2 machinery
import	django_tables2 as tables
from	django_tables2			import RequestConfig
from	django_tables2.utils		import A



# The tables are defined separately
from .monitorTables import *

from utils.selectorUtils 		import dropDownGeneric, boxSelector
from utils.miscUtils			import makeTupleList
from utils.navbar			import TopTable, HomeTable

from django import forms

# For choice fields, first element is value, second is the label in the dropdown list
# ('All', 'All')
USERCHOICES	= [] # will be aurmented with info from the settings
JOBTYPECHOICES	= [] # ditto

PAGECHOICES	= [('25','25'), ('50','50'), ('100','100'), ('200','200'),('400','400'),]

refreshChoices = [('', 'Never'), ('5', '5s'), ('10', '10s'), ('30', '30s'), ('60','1min'), ]

SELECTORS	= {
    'pilot':
    {'stateLabel':'Pilot States',
     'states':[
         ('all',	'All'),		('active',	'Active'),	('running',	'Running'),	('stopped',	'Stopped'),
         ('timeout',	'Timed out'),	('no jobs',	'No Jobs'),	('DB lock',	'DB lock'),
     ],
     'stateselector':True,
     'userselector': None,
     'gUrl':'/monitor/pilots',
     'qUrl':'/monitor/pilots?',
     'table':'PilotTable',
    },
    
    'job':
    {'stateLabel':'Job States',
     'states':[
         ('all',	'All'),		('template',	'Template'),	('defined',	'Defined'),	('running',	'Running'),
         ('finished','Finished'),	('pilotTO','Pilot Timed Out'),	('timelimit',	'Time Limit'),  ('error',	'Error'),
     ],
     'stateselector':True,
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
     'stateselector':True,
     'userselector': 'userselector',
     'gUrl':'/monitor/workflows',
     'qUrl':'/monitor/workflows?',
     'table':'WfTable',
    },
    
    'site':	{'stateselector':None,	'userselector': None,	'table': 'SiteTable',    },
    
    'dataset':	{'stateselector':None,	'userselector': None,	'table': 'DataTable',    },
    
    'datatype':	{'stateselector':None,	'userselector': None,	'table': 'DataTypeTable',},
    
    'dag':	{'stateselector':None,	'userselector': None,	'table': 'DagTable',
     'gUrl':'/monitor/dags',
     'qUrl':'/monitor/dags?',
    },

    'service':	{'stateselector':None,	'userselector': None,	'table': 'ServiceTable', 'serviceselector': True,
     'gUrl':'/monitor/services',
     'qUrl':'/monitor/services?',
    },
}


#########################################################    
def makeQuery(what, q=''):
    gUrl= SELECTORS[what]['gUrl']
    qUrl= SELECTORS[what]['qUrl']

    if(q==''):
        return HttpResponseRedirect(gUrl)
    
    return HttpResponseRedirect(qUrl+q)

#########################################################    
# general request handler for summary type of a table
def data_handler(request, what):

    dqm_domain, dqm_host, p3s_users, p3s_jobtypes = None, None, None, None

    try:
        dqm_domain	= settings.SITE['dqm_domain']
        dqm_host	= settings.SITE['dqm_host']
        p3s_jobtypes	= settings.SITE['p3s_jobtypes']
        p3s_services	= settings.SITE['p3s_services']
    except:
        return HttpResponse("error: check local.py for dqm_domain,dqm_host,p3s_jobtypes, p3s_services")

    p3s_users	= 'All,'+p3sUser.all()
    
    userlist	= p3s_users.split(',')
    jobtypes	= p3s_jobtypes.split(',')
    services	= p3s_services.split(',')
    
    #----------------------------------------------
    template = 'universo.html'

    uuid	= request.GET.get('uuid','')
    wfuuid	= request.GET.get('wfuuid','')
    pk		= request.GET.get('pk','')
    name	= request.GET.get('name','')
    state	= request.GET.get('state','')
    error	= request.GET.get('error','')
    jobtype	= request.GET.get('jobtype','')
    user	= request.GET.get('user','')
    refresh	= request.GET.get('refresh', '')

    serviceName	= request.GET.get('service','')
    
    host	= request.GET.get('host','')

    
    perpage	= request.GET.get('perpage','25')

    states = ['all',]
    stateD = {'all':True}
    if(state != ''):
        states = state.split(',')
        stateD = {}
        for st in states:
            stateD[st] = True

    initUser=user
    if(user==''): initUser='All'
        
    initJobType=jobtype
    if(jobtype==''): initJobType='All'

    initService=serviceName
    if(serviceName==''): initService='All'
        
    domain	= request.get_host()

    now		= datetime.datetime.now().strftime('%x %X')+' '+timezone.get_current_timezone_name() # beautify later
    d		= dict(domain=domain, dqm_domain=dqm_domain, dqm_host=dqm_host, time=str(now))

    objects, t, Nfilt						= None, None, None
    stateSelector, perPageSelector, userSelector, typeSelector, serviceSelector, refreshSelector = None, None, None, None, None, None

    t = None  # placeholder for the main table object
    
    if(what in ['job', 'pilot', 'dag', 'workflow', 'service']):

        USERCHOICES	= makeTupleList(userlist)
        JOBTYPECHOICES	= makeTupleList(jobtypes)
        SERVICECHOICES	= makeTupleList(services)
        
        selector = SELECTORS[what] # IMPORTANT
        
        q = '' # stub for the query
        
        chosenTable=eval(selector['table'])

        timeselector = 'TBD'

        #----------

        if request.method == 'POST':
            
            try:
                if(selector['stateselector']):
                    stateSelector = boxSelector(request.POST,
                                                what=what,
                                                states=SELECTORS[what]['states'],
                                                label=SELECTORS[what]['stateLabel'])
                
                    
                    if stateSelector.is_valid():q += stateSelector.handleBoxSelector()
            except:
                pass

            # PLEASE HASH ME! Will remove redundant code later -mxp-
            try:
                if(selector['userselector']):
                    userSelector = dropDownGeneric(request.POST, label='User', choices=USERCHOICES, tag='user')
                    if userSelector.is_valid():	q += userSelector.handleDropSelector()
            except:
                pass

            try:
                if(selector['typeselector']):
                    typeSelector = dropDownGeneric(request.POST, label='Type', choices=JOBTYPECHOICES, tag='jobtype')
                    if typeSelector.is_valid(): q += typeSelector.handleDropSelector()
            except:
                pass

            try:
                if(selector['serviceselector']):
                    serviceSelector = dropDownGeneric(request.POST, label='Service', choices=SERVICECHOICES, tag='service')
                    if serviceSelector.is_valid(): q += serviceSelector.handleDropSelector()
            except:
                pass

            # try:
            #     if(selector['timeselector'] is not None):
            #         timeselector = dropDownGeneric(request.POST, label='Time', choices=(('1','100'),('2','200'),), tag='time')
            #         # if userSelector.is_valid(): q += userSelector.handleDropSelector()
            # except:
            #     pass


            perPageSelector = dropDownGeneric(request.POST, initial={'perpage':perpage}, label='# per page', choices = PAGECHOICES, tag='perpage')
            if perPageSelector.is_valid(): q += perPageSelector.handleDropSelector()

            refreshSelector = dropDownGeneric(request.POST, label='Refresh', choices=refreshChoices, tag='refresh')
            if refreshSelector.is_valid(): q += refreshSelector.handleDropSelector()
            
            return makeQuery(what, q) # will go and get the query results...

        #######################################################################################
        ##### IF IT'S NOT RESPONSE TO a "POST", BUILD THE INITIAL PAGE AND/OR RUN A QUERY #####
        #######################################################################################
        
        refresh		= request.GET.get('refresh', '')
        try:
            if(selector['stateselector']):
                stateSelector	= boxSelector(what=what,initial={'stateChoice':stateD},
                                              states=SELECTORS[what]['states'],
                                              label=SELECTORS[what]['stateLabel'])
        except:
            pass
            
        try:
            if(selector['userselector']):
                userSelector	= dropDownGeneric(initial={'user':initUser},
                                                  label='User',
                                                  choices = USERCHOICES,
                                                  tag='user')
        except:
            pass
            
        try:
            if(selector['typeselector']):
                typeSelector	= dropDownGeneric(initial={'jobtype':initJobType},
	                                          label='Type',
	                                          choices = JOBTYPECHOICES,
                                                  tag='jobtype')
        except:
            pass
            
        try:
            if(selector['serviceselector']):
                serviceSelector	= dropDownGeneric(initial={'service':initService},
	                                          label='Service',
                                                  choices = SERVICECHOICES,
                                                  tag='service')
        except:
            pass

        
        refreshSelector = dropDownGeneric(label='Refresh',	initial={'refresh': refresh},	choices=refreshChoices,	tag='refresh')
        perPageSelector	= dropDownGeneric(label='# per page',	initial={'perpage':perpage},	choices = PAGECHOICES,	tag='perpage')
        
        # 4 later: timeselector	= dropDownGeneric(label='Time limit', choices=(('1','1h'),('2','2h'),), tag='time')

        ###############################
        # initiate the  query
        ###############################
        
        objects = eval(what).objects.order_by('-pk') # newest on top
        kwargs = {}

        for selectionKey in ('uuid','wfuuid','pk','name','user','jobtype'):
            val = eval(selectionKey)
            if(val!=''): kwargs[selectionKey] = val

        # corner cases
        if(serviceName	!= ''):	kwargs['name']		= serviceName
        if(state	!= ''):
            if(state=='error'):
                pass
            else:
                kwargs['state__in']	= states # note multiple values
#        if(error	!= '')

        try:
            objs = objects.filter(**kwargs)
            if(state=='error'):
                kwargs['errcode__in'] = ['0','']
                objs = objs.exclude(**kwargs)

            Nfilt = objs.count()
            t = chosenTable(objs)
        except:
            pass
            
        if(t is None):t = chosenTable(objects.all()) # FIXME - check kwargs instead

    if(what in ['dataset', 'site', 'datatype']):
        selector = SELECTORS[what]               # IMPORTANT
        chosenTable=eval(selector['table'])
        objects = eval(what).objects.order_by('-pk') # newest on top
        t = chosenTable(objects.all())

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

    for s in (stateSelector, userSelector, typeSelector, serviceSelector, refreshSelector, perPageSelector):
        if(s):	selectors.append(s)

    d['selectors']	= selectors
    d['refresh']	= refresh
    d['navtable']	= TopTable(domain, dqm_domain)
    d['hometable']	= HomeTable(domain, dqm_domain)

    return render(request, template, d)

#########################################################    
# general request handler for detail type of a table
def detail_handler(request, what):
    try:
        dqm_domain	= settings.SITE['dqm_domain']
        dqm_host	= settings.SITE['dqm_host']
        p3s_users	= settings.SITE['p3s_users']
        p3s_jobtypes	= settings.SITE['p3s_jobtypes']
        p3s_services	= settings.SITE['p3s_services']
    except:
        return HttpResponse("error: check local.py for dqm_domain,dqm_host,p3s_users,p3s_jobtypes, p3s_services")
    
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

    d['navtable']	= TopTable(domain, dqm_domain)
    d['hometable']	= HomeTable(domain, dqm_domain)
        
    return render(request, template, d)


###################################################################################
def filesystem(request):
    l = os.listdir(settings.SITE['p3s_input'])
    return HttpResponse(l)
    
#################################### THE END ######################################

        
