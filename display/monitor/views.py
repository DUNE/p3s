import django.db.models
from django.db.models			import Max
from django				import forms
from django.utils.html import format_html

from django.conf			import settings
from django.utils.safestring		import mark_safe
from django_tables2			import A
from django.shortcuts			import render
from django.utils			import timezone
from django.utils.timezone		import utc
from django.utils.timezone		import activate

from django.http			import HttpResponseRedirect
from django.http			import HttpResponse

from django.views.decorators.csrf	import csrf_exempt

from django.db import models

import  django_tables2 as tables
from	django_tables2			import RequestConfig
from	django_tables2.utils		import A

import datetime
import random
import json
# import pytz

from collections import OrderedDict

from purity.models			import pur
from evdisp.models			import evdisp
from .models				import monrun

from utils.selectorUtils		import dropDownGeneric, boxSelector, twoFieldGeneric
from utils.navbar			import TopTable, HomeTable, HomeBarData


# The tables needed here are defined in a separate unit of code
from .monitorTables import *

#########################################################
JOBTYPECHOICES	= [('', 'All'), ('purity','purity'), ('monitor','monitor'), ('evdisp','evdisp'), ('crt','crt'), ]

REFRESHCHOICES	= [('', 'Never'),	('10', '10s'),	('30', '30s'),	('60','1min'),	('120', '2min'),  ]
PAGECHOICES	= [('25','25'),		('50','50'),	('100','100'),	('200','200'),	('400','400'),]
TPCCHOICES	= [('', 'All'),		('1', '1'),	('2','2'),	('5','5'),	('6','6'),	('9','9'),	('10','10'), ]

PURITYCHARTLABELS = {
    'purity':	{'main':'lifetime',	'vAxis':'Lifetime (ms)',	'extra':'lowest allowed'},
    'sn':	{'main':'s/n',		'vAxis':'S/N',			'extra':'lowest allowed'},
    }

GCHARTS2	= '[new Date(Date.UTC(%s)), %s, %s],'
T4G	= '%Y, %m-1, %d, %H, %M, %S'


TSLABEL1	= 'min. (YYYY-MM-DD HH:MM:SS)'
TSLABEL2	= 'max. (YYYY-MM-DD HH:MM:SS)'
#########################################################

# ---
def makeQuery(page, q=''):
    gUrl= '/monitor/'+page
    qUrl= '/monitor/'+page+"?"

    if(q==''): return HttpResponseRedirect(gUrl)
    return HttpResponseRedirect(qUrl+q)


#########################################################    
####################  VIEWS #############################    
#########################################################
def monchart(request):
    p3s_domain, dqm_domain, dqm_host, p3s_users, p3s_jobtypes = None, None, None, None, None

    try:
        p3s_domain	= settings.SITE['p3s_domain']
        dqm_domain	= settings.SITE['dqm_domain']
        dqm_host	= settings.SITE['dqm_host']
        p3s_jobtypes	= settings.SITE['p3s_jobtypes']
        p3s_services	= settings.SITE['p3s_services']
    except:
        return HttpResponse("error: check local.py for dqm_domain,dqm_host,p3s_jobtypes, p3s_services")

    
    host	= request.GET.get('host','')
    port	= request.get_port()

    domain	= request.get_host()
    tsmin	= request.GET.get('tsmin','')
    tsmax	= request.GET.get('tsmax','')
    
    width	= request.GET.get('width','3')
    what	= request.GET.get('what','')
    plane	= request.GET.get('plane','')

    q='what='+what+'&plane='+plane+'&'

    if request.method == 'POST':
        tsSelector = twoFieldGeneric(request.POST,
                                     label1=TSLABEL1, field1="tsmin", init1=tsmin,
	                             label2=TSLABEL2, field2="tsmax", init2=tsmax)
        if tsSelector.is_valid():
            tsmin=tsSelector.getval("tsmin")
            tsmax=tsSelector.getval("tsmax")
            if(tsmin!=''): q+= 'tsmin='+tsmin+'&'
            if(tsmax!=''): q+= 'tsmax='+tsmax+'&'

        return makeQuery('monchart', q) # will go and get the query results...
    
    #-----------
    # for the charts
    bigStruct = []
    timeSeries = []
    W=int(width)
    cnt=0

    for tpcNum in range(6):
        myDict = {}

        objs = monrun.objects.order_by('-pk')
        if(tsmin!=''):  objs = objs.filter(ts__gte=tsmin)
        if(tsmax!=''):	objs = objs.filter(ts__lte=tsmax)

        dataStr = ''
        for forChart in objs:
            try: # template: [new Date(2014, 10, 15, 7, 30), 1],
                t = forChart.ts
                s = json.loads(forChart.summary)[0]
                if(what in ('hits','charge')):
                    data1 = s[monPatterns[what+'1']%plane].split(',')
                    data2 = s[monPatterns[what+'2']%plane].split(',')
                    dataStr += ('[new Date(Date.UTC(%s)), %s, %s],') % (t.strftime("%Y, %m-1, %d, %H, %M, %S"), data1[tpcNum], data2[tpcNum])
                elif(what=='noise'):
                    data1 = s[monPatterns[what+'1']].split(',')
                    data2 = s[monPatterns[what+'2']].split(',')
                    dataStr += ('[new Date(Date.UTC(%s)), %s, %s],') % (t.strftime("%Y, %m-1, %d, %H, %M, %S"), data1[tpcNum], data2[tpcNum])
                elif(what=='dead'):
                    data3 = s[monPatterns[what]].split(',')
                    dataStr += ('[new Date(Date.UTC(%s)), %s],') % (t.strftime("%Y, %m-1, %d, %H, %M, %S"), data3[tpcNum])
                else:
                    pass
            except:
                break

        myDict["panel"] = 'tpc'+str(tpcNum)
        myDict["timeseries"]=dataStr

        if(what=='hits'):
            myDict["vAxis"]='Plane %s hits/RMS' % plane
            myDict["main"]='hits'
            myDict["extra"]='rms'
        elif(what=='charge'):
            myDict["vAxis"]='Plane %s Charge/RMS' % plane
            myDict["main"]='charge'
            myDict["extra"]='rms'
        elif(what=='noise'):
            myDict["vAxis"]='Noisy channels 6\u03C3/1\u03C3'
            myDict["main"]='noise 6\u03C3'
            myDict["extra"]='noise 1\u03C3'
        elif(what=='dead'):
            myDict["vAxis"]='Dead Channels'
            myDict["main"]='dead channels'
        else:
            pass

        
        timeSeries.append(myDict)
        cnt+=1
        if(cnt == W):
            bigStruct.append(timeSeries)
            timeSeries = []
            cnt=0
            
    bigStruct.append(timeSeries)

    d = {}
    d['rows']	= bigStruct
    d['domain']	= domain
    
    tsSelector = twoFieldGeneric(label1=TSLABEL1, field1="tsmin", init1=tsmin,
                                 label2=TSLABEL2, field2="tsmax", init2=tsmax)
    
    selectors = []
    selectors.append(tsSelector)

    d['selectors']	= selectors
    d['pageName']	= ': '+what+' timeline'
    d['navtable']	= TopTable(domain)
    d['hometable']	= HomeTable(p3s_domain, dqm_domain, domain, port)

    return render(request, 'purity_chart1.html', d)

#########################################################
def puritychart(request, what):
   
    p3s_domain, dqm_domain, dqm_host, p3s_users, p3s_jobtypes = None, None, None, None, None

    try:
        p3s_domain	= settings.SITE['p3s_domain']
        dqm_domain	= settings.SITE['dqm_domain']
        dqm_host	= settings.SITE['dqm_host']
        p3s_jobtypes	= settings.SITE['p3s_jobtypes']
        p3s_services	= settings.SITE['p3s_services']
    except:
        return HttpResponse("error: check local.py for dqm_domain,dqm_host,p3s_jobtypes, p3s_services")

    
    host	= request.GET.get('host','')
    port	= request.get_port()
    
    domain	= request.get_host()
    tsmin	= request.GET.get('tsmin','')
    tsmax	= request.GET.get('tsmax','')
    width	= request.GET.get('width','3')

    q='' # the query string will go here
    
    if request.method == 'POST':
        tsSelector = twoFieldGeneric(request.POST,
                                     label1=TSLABEL1, field1="tsmin", init1=tsmin,
                                     label2=TSLABEL2, field2="tsmax", init2=tsmax)
        if tsSelector.is_valid():
            tsmin=tsSelector.getval("tsmin")
            tsmax=tsSelector.getval("tsmax")
            if(tsmin!=''): q+= 'tsmin='+tsmin+'&'
            if(tsmax!=''): q+= 'tsmax='+tsmax+'&'

        return makeQuery('puritychart', q) # now we'll go and get the query results...

    
    ##########################################################################################################
    ########################################## QUERY RESULTS #################################################
    ##########################################################################################################

    bigPur, purSeries, W, cnt	= [], [], int(width), 0
    lowerLimit			= settings.LIMITS[what]['min']
    
    # select by TPC and the time range
    for tpcNum in (1,2,5,6,9,10):
        objs = pur.objects.order_by('-pk').filter(tpc=tpcNum)
        if(tsmin!=''):	objs = objs.filter(ts__gte=tsmin)
        if(tsmax!=''):	objs = objs.filter(ts__lte=tsmax)

        purStr='' # This string must comply with the Google Charts format

        for purEntry in objs:
            try: # template: [new Date(2014, 10, 15, 7, 30), 1], ??? Leave for now
                purStr += GCHARTS2 % (purEntry.ts.strftime(T4G), {'purity':purEntry.lifetime, 'sn':purEntry.sn}[what], lowerLimit)
            except:
                break

        # This dict takes the panel name, the above formed time series as string, and axes names/labels
        purDict = {}
        purDict["panel"]	= 'tpc'+str(tpcNum)
        purDict["timeseries"]	= purStr # !!! ship out finalized time series STRING in Google format !!!
        purDict			= {**purDict, **PURITYCHARTLABELS[what]} # merge: add axes labels etc
        purDict['extra']	= purDict['extra']+': '+str(lowerLimit)
            
        purSeries.append(purDict) # purSeries is just a row, it's an entry in the bigger list "bigPur"
        
        cnt+=1
        if(cnt == W):
            bigPur.append(purSeries)
            purSeries = []
            cnt=0
            
    bigPur.append(purSeries)

    # Finally, fill out the dictionary to be rendered in the template
    d		= {}
    d['rows']	= bigPur # the data to be rendered in the charts
    d['domain']	= domain
    
    tsSelector = twoFieldGeneric(label1=TSLABEL1, field1="tsmin", init1=tsmin, label2=TSLABEL2, field2="tsmax", init2=tsmax)
    
    selectors = []
    selectors.append(tsSelector)
    
    d['selectors']	= selectors
    d['pageName']	= ': '+what+' timeline'
    d['navtable']	= TopTable(domain)
    d['hometable']	= HomeTable(p3s_domain, dqm_domain, domain, port)
    d['dqmHome']	= HomeBarData(p3s_domain, dqm_domain, domain, port)[0]['col2']
    d['vMinmax']	= [settings.CHARTS[what]['min'], settings.CHARTS[what]['max']]
    
    return render(request, 'purity_chart2.html', d)

#########################################################    
# general request handler for summary type of a table
def data_handler2(request, what, tbl, tblHeader, url):
    p3s_domain, dqm_domain, dqm_host, p3s_users, p3s_jobtypes = None, None, None, None, None

    try:
        p3s_domain	= settings.SITE['p3s_domain']
        dqm_domain	= settings.SITE['dqm_domain']
        dqm_host	= settings.SITE['dqm_host']
        p3s_jobtypes	= settings.SITE['p3s_jobtypes']
        p3s_services	= settings.SITE['p3s_services']
    except:
        return HttpResponse("error: check local.py for dqm_domain,dqm_host,p3s_jobtypes, p3s_services")

    domain	= request.get_host()

    host	= request.GET.get('host','')
    port	= request.get_port()
    
    perpage	= request.GET.get('perpage','25')
    tsmin	= request.GET.get('tsmin','')
    tsmax	= request.GET.get('tsmax','')
    j_uuid	= request.GET.get('j_uuid','')
    jobtype	= request.GET.get('jobtype','')
    d_type	= request.GET.get('d_type','')
    run		= request.GET.get('run','')
    evnum	= request.GET.get('evnum','')
    refresh	= request.GET.get('refresh',None)
    showjob	= request.GET.get('showjob',None)
    tpc		= request.GET.get('tpc','')



    initJobType=jobtype
    if(jobtype==''): initJobType='All'

    
    q=''	# stub for a query that may be built

    if request.method == 'POST':
        refreshSelector = dropDownGeneric(request.POST, label='Refresh', choices=REFRESHCHOICES, tag='refresh')
        if refreshSelector.is_valid(): q += refreshSelector.handleDropSelector()

        perPageSelector	= dropDownGeneric(request.POST, initial={'perpage':perpage}, label='# per page', choices = PAGECHOICES, tag='perpage')
        if perPageSelector.is_valid(): q += perPageSelector.handleDropSelector()

        # ---
        # page-specific controls
        if(what=='monrun'):
            typeSelector = dropDownGeneric(request.POST, label='Type', choices=JOBTYPECHOICES, tag='jobtype')
            if typeSelector.is_valid(): q += typeSelector.handleDropSelector()

        
        if(what=='pur'):
            tpcSelector = dropDownGeneric(request.POST, initial={'tpc':tpc}, label='tpc', choices = TPCCHOICES, tag='tpc')
            if tpcSelector.is_valid(): q += tpcSelector.handleDropSelector()
            
        # ---
        tsSelector = twoFieldGeneric(request.POST,
                                     label1=TSLABEL1, field1="tsmin", init1=tsmin,
                                     label2=TSLABEL2, field2="tsmax", init2=tsmax)
        if tsSelector.is_valid():
            tsmin=tsSelector.getval("tsmin")
            tsmax=tsSelector.getval("tsmax")
            
            if(tsmin!=''): q+= 'tsmin='+tsmin+'&'
            if(tsmax!=''): q+= 'tsmax='+tsmax+'&'

        if(what=='evdisp'):
            juuidSelector = twoFieldGeneric(request.POST,
                                            label1="Job UUID",	field1="j_uuid",	init1=j_uuid,
                                            label2="Data Type",	field2="d_type",	init2=d_type)
            if juuidSelector.is_valid():
                j_uuid=juuidSelector.getval("j_uuid")
                if(j_uuid!=''): q+= 'j_uuid='+j_uuid+'&'
                
                d_type=juuidSelector.getval("d_type")
                if(d_type!=''): q+= 'd_type='+d_type+'&'
                
            runSelector =  twoFieldGeneric(request.POST,
                                           label1="Run",	field1="run",	init1=run,
                                           label2="Event",	field2="event",	init2=evnum)
            
            if runSelector.is_valid():
                run=runSelector.getval("run")
                if(run!=''): q+= 'run='+run+'&'
                
                event=runSelector.getval("event")
                if(event!=''): q+= 'evnum='+event+'&'
                

        return makeQuery(url, q) # We have built a query and will come to same page/view with the query parameters


    ###########################################################################
    # -------------------------------------------------------------------------
    ###########################################################################
    

    now		= datetime.datetime.now().strftime('%x %X')+' '+timezone.get_current_timezone_name() # beautify later
    d		= dict(domain=domain, time=str(now))
#    objs	= eval(what).objects.order_by('-pk').all()
    objs	= eval(what).objects.all()

    if(tsmin!=''):	objs = eval(what).objects.filter(ts__gte=tsmin)
    if len(objs)==0: return("No objects found according to your citeria")
    if(tsmax!=''):	objs = objs.filter(ts__lte=tsmax)
    if(j_uuid!=''):	objs = objs.filter(j_uuid=j_uuid)
    if(jobtype!=''):	objs = objs.filter(jobtype=jobtype)
    if(d_type!=''):	objs = objs.filter(datatype=d_type)
    if(run!=''):	objs = objs.filter(run=run)
    if(evnum!=''):	objs = objs.filter(evnum=evnum)
    if(tpc!=''):	objs = objs.filter(tpc=tpc)


    # safety:
    if len(objs)==0: return("No objects found according to your citeria")

    
    #-------------
    # Initialize the table object, fill essential info in the dictionary for the template (d)
    t = None # placeholder for the table
    if(tbl=='RunTable'): # special case
        RunData = []
        distinct_run = objs.order_by('-run').distinct("run").all()
        if(run!=''): distinct_run = objs.filter(run=run).distinct("run").all()

        for e in distinct_run:
            selected = []
            for e in objs.filter(run=e.run).distinct("evnum"): selected.append(makeEvLink(domain, e.run, e.evnum))
                
            RunData.append({'Run': e.run, 'ts': e.ts, 'evs': mark_safe(','.join(selected)) })
            t = RunTable(RunData)
    else:
        t = eval(tbl)(objs.order_by('-pk'))

    if(tbl=='EvdispTable' and showjob is None): t.exclude = ('j_uuid',)
    
    t.set_site(domain)
    
    RequestConfig(request, paginate={'per_page': int(perpage)}).configure(t)

    d['table']	= t
    d['N']	= str(len(objs))
    d['domain']	= domain
    
    d['pageName']	= ': '+tbl
    try:
        d['message']	= eval(what).message()
    except:
        pass

    ############################################
    # Populate the selectors
    selectors = []
    # ---
    refreshSelector = dropDownGeneric(label='Refresh', initial={'refresh': refresh}, choices=REFRESHCHOICES, tag='refresh')
    selectors.append(refreshSelector)
    # ---
    perPageSelector = dropDownGeneric(initial={'perpage':perpage}, label='# per page', choices = PAGECHOICES, tag='perpage')
    selectors.append(perPageSelector)

    if(what=='monrun'):
        typeSelector	= dropDownGeneric(initial={'jobtype':initJobType}, label='Type', choices = JOBTYPECHOICES, tag='jobtype')
        selectors.append(typeSelector)
        
    # ---
    tsSelector = twoFieldGeneric(label1=TSLABEL1, field1="tsmin", init1=tsmin, label2=TSLABEL2, field2="tsmax", init2=tsmax)
    
    selectors.append(tsSelector)
    # ---
    if(what=='pur'):
        tpcSelector = dropDownGeneric(initial={'tpc':tpc}, label='tpc', choices = TPCCHOICES, tag='tpc')
        selectors.append(tpcSelector)
    # ---
    if(what=='evdisp'):
        juuidSelector = twoFieldGeneric(label1="Job UUID", field1="j_uuid", init1=j_uuid, label2="Data Type", field2="d_type", init2=d_type)
        selectors.append(juuidSelector)
        
        runSelector =  twoFieldGeneric(label1="Run",
                                       field1="run",
                                       init1=run,
                                       label2="Event",
                                       field2="event",
                                       init2=evnum)
        selectors.append(runSelector)

    # -------------------------------------------------------------
    u1, u2, r, e, g = None, None, None, None, None
    
    if(tbl=='EvdispTable'):
        last_image = None
        try:
            last_image = evdisp.objects.last()
            r, e, j	= last_image.run, last_image.evnum, last_image.j_uuid
            g =	random.randint(1,6)
    
            u1 = makeImageLink(domain, settings.SITE['dqm_evdisp_url'], j, r, e, 'raw', g)
            u2 = makeImageLink(domain, settings.SITE['dqm_evdisp_url'], j, r, e, 'prep', g)

        except: # fail or empty - bail
            pass   #   if(last_image is None): return render(request, 'unitable2.html', d)


    if(tbl=='MonRunTable'): t.modifyName('run','Run::SubRun/Job')
        
    d['selectors']	= selectors
    d['refresh']	= refresh
    d['host']		= domain
    d['img_url1']	= u1
    d['img_url2']	= u2
    d['run']		= r
    d['event']		= e
    d['group']		= g

    d['tblHeader']	= tblHeader
    d['navtable']	= TopTable(domain)
    d['hometable']	= HomeTable(p3s_domain, dqm_domain, domain, port)
    d['dqmHome']	= HomeBarData(p3s_domain, dqm_domain, domain, port)[0]['col2']
    
    return render(request, 'unitable2.html', d)

#########################################################    
@csrf_exempt
def eventdisplay(request):
    
    domain	= request.get_host()
    run		= request.GET.get('run','')
    event	= request.GET.get('event','')

    d = {}

    d['display'] = (event!='' and run!='')
    d['chList'] = ('0-2559','2560-5119','5120-7679','7680-10239','10240-12799','12800-15359')

    d['domain']		= domain
    d['evdispURL']	= 'evdisp'
    d['run']		= run
    d['event']		= event
    
    d['pageName']	= ': Event Display'
    d['navtable']	= TopTable(domain)
    d['hometable']	= HomeTable(domain, dqm_domain)

    return render(request, 'display.html', d)

#########################################################    
@csrf_exempt
def addmon(request):
    post	= request.POST
    
    summary	= post.get('summary', '')

    s = {}
    try:
        s = json.loads(summary)
    except:
        pass
    
    m=monrun()

    # we are counting on the defaults defined in the class...
    # m.run=post.get('run',0), m.subrun=post.get('subrun',0)
    
    m.summary		= summary
    m.description	= post.get('description', '')
    m.j_uuid		= post.get('j_uuid', '')
    m.jobtype		= post.get('jobtype', '')
    m.ts		= post.get('ts', timezone.now())
    
    m.save()

    return HttpResponse('Adding mon entry for run '+str(m.run)+' subrun '+str(m.subrun))
#########################################################    
@csrf_exempt
def delmon(request):
    post	= request.POST
    pk		= post.get('pk', '')
    run		= post.get('run', '')
    subrun	= post.get('subrun', '')

    if(run=='' and pk==''): return HttpResponse('Did not delete mon entries, run/ID unspecified')
    
    if(run=='ALL' or pk=='ALL'):
        try:
            obj = monrun.objects.all().delete()
            return HttpResponse('Deleted ALL mon entries')
        except:
            return HttpResponse('Failed to delete ALL mon entries ')
       
    
    if(pk!=''):
        try:
            obj = monrun.objects.get(pk=int(pk))
            obj.delete()
            return HttpResponse('Deleted the mon entry for ID '+pk)
        except:
            return HttpResponse('Failed to delete mon entry for ID '+pk)
        
    # at this point we assume we must delete entries
    # based on the run number or run/subrun numbers:
    try:
        objs = None
        if(subrun==''):
            objs = monrun.objects.filter(run=run)
        else:
            objs = monrun.objects.filter(run=run).filter(subrun=subrun)
            
        l = str(len(objs))
        objs.delete()
        
        return HttpResponse('Deleted '+l+' mon entries for run '+run+'::'+subrun)
    except:
        return HttpResponse('Failed to delete mon entries for run '+run+'::'+subrun)

#########################################################    
def automon(request):
    domain	= request.get_host()
    host	= request.GET.get('host','')
    port	= request.get_port()
    run		= request.GET.get('run','')
    subrun	= request.GET.get('subrun','')
    category	= request.GET.get('category','')
    filetype	= request.GET.get('filetype','')

    # Get JSON out of the database and prepare to load the dictionary
    entry = None
    try:
        entry	= monrun.objects.filter(run=run).filter(subrun=subrun)[0]
    except:
        return 'not found'

    # Create a dictionary describing files from JSON we just located
    description = json.loads(entry.description, object_pairs_hook=OrderedDict)
    
    url2images, p3s_domain, dqm_domain, dqm_host, p3s_users, p3s_jobtypes = None, None, None, None, None, None

    try:
        url2images	= settings.SITE['dqm_monitor_url']
        p3s_domain	= settings.SITE['p3s_domain']
        dqm_domain	= settings.SITE['dqm_domain']
        dqm_host	= settings.SITE['dqm_host']
        p3s_jobtypes	= settings.SITE['p3s_jobtypes']
        p3s_services	= settings.SITE['p3s_services']
    except:
        return HttpResponse("error: check local.py")

    # construct UI items
    d = {}
    d['navtable']	= TopTable(domain)
    d['hometable']	= HomeTable(p3s_domain, dqm_domain, domain)
    d['tblHeader']	= 'Run::Subrun '+run+'::'+subrun
    d['footer']		= 'Produced by job '+entry.j_uuid+' at '+entry.ts.strftime('%x %X')
    # ---
    
    # IF THE CATEGORY HAS BEEN DEFINED, SERVE THE CONTENT:
    if(category!=''):
        j_uuid	= entry.j_uuid

        files = None
        for item in description:
            if(item['Category']==category): files=item['Files'][filetype]
        if(files is None): return 'error'
        
        d['rows'] = monrun.autoMonImgURLs(domain, url2images, j_uuid, files)
        return render(request, 'unitable3.html', d)
    
    # ---
    # ok, so no category - present choices ... of menus... for each "item"
    lengths = []
    for item in description: lengths.append(len(item['Files'].keys()))
    mxLen = max(lengths) # this is for padding with empty rows for cleaner look

    cats, tbls = ([], [])
    
    for item in description:
        category, files  = item['Category'], item['Files']
        
        list4table = []
        for fileType in files.keys():
            list4table.append({'items':monrun.autoMonLink(domain,run,subrun,category,fileType)})

        # padding with empty rows for better look
        for i in range(mxLen - len(files.keys())): list4table.append({'items':format_html('&nbsp;')})
                              
        t = ShowMonTable(list4table, show_header=False)
        tbls.append(t)
        cats.append(category)

    d['tables']		= tbls
    d['headers']	= cats
    d['dqmHome']	= HomeBarData(p3s_domain, dqm_domain, domain, port)[0]['col2']

    return render(request, 'unitable4.html', d)



#########################################################    
############# EVENT DISPLAY #############################    
#########################################################    
@csrf_exempt
def display6(request):
    p3s_domain, dqm_domain, dqm_host, p3s_users, p3s_jobtypes = None, None, None, None, None

    try:
        p3s_domain	= settings.SITE['p3s_domain']
        dqm_domain	= settings.SITE['dqm_domain']
        dqm_host	= settings.SITE['dqm_host']
        p3s_jobtypes	= settings.SITE['p3s_jobtypes']
        p3s_services	= settings.SITE['p3s_services']
    except:
        return HttpResponse("error: check local.py for dqm_domain,dqm_host,p3s_jobtypes, p3s_services")

    
    domain	= request.get_host()
    run		= request.GET.get('run','')
    event	= request.GET.get('event','')


    objs = evdisp.objects.filter(run=run).filter(evnum=event)
    
    d = {}
    d['domain']		= domain
    d['changroups']	= [1,2,3,4,5,6]

    ts = None
    d['rows'] = []
    for N in d['changroups']:
        raw	= objs.filter(changroup=N).filter(datatype='raw')[0]
        prep	= objs.filter(changroup=N).filter(datatype='prep')[0]

        ts = raw.ts
        rawUrl = ('http://%s/%s/%s/%s'
                         % (domain, # this needs to point to the image, also below
                            settings.SITE['dqm_evdisp_url'],
                            raw.j_uuid,
                            evdisp.makename(int(event), 'raw', N)
                         ))

        prepUrl = ('http://%s/%s/%s/%s'
                         % (domain, # this needs to point to the image, also below
                            settings.SITE['dqm_evdisp_url'],
                            raw.j_uuid,
                            evdisp.makename(int(event), 'prep', N)
                         ))
        d['rows'].append([rawUrl,prepUrl])

    d['run']		= run
    d['event']		= event
    d['ts']		= ts
    d['pageName']	= ': Event Display'
    d['message']	= evdisp.message()
    d['navtable']	= TopTable(domain)
    d['hometable']	= HomeTable(p3s_domain, dqm_domain)
    
    return render(request, 'display6.html', d)

#########################################################    
@csrf_exempt
def display1(request):
    p3s_domain, dqm_domain, dqm_host, p3s_users, p3s_jobtypes = None, None, None, None, None

    try:
        p3s_domain	= settings.SITE['p3s_domain']
        dqm_domain	= settings.SITE['dqm_domain']
        dqm_host	= settings.SITE['dqm_host']
        p3s_jobtypes	= settings.SITE['p3s_jobtypes']
        p3s_services	= settings.SITE['p3s_services']
    except:
        return HttpResponse("error: check local.py for dqm_domain,dqm_host,p3s_jobtypes, p3s_services")

    
    domain	= request.get_host()
    url		= request.GET.get('url','')
    run		= request.GET.get('run','')
    event	= request.GET.get('event','')
    changroup	= request.GET.get('changroup','')
    datatype	= request.GET.get('datatype','')

    d = {}
    d['domain']		= domain

    for item in ('url', 'run', 'event', 'changroup', 'datatype'):
        stuff = request.GET.get(item,'')
        if(item=='changroup'):
            d[item] = stuff+' ('+evdisp.group2string(int(stuff))+')'
        else:
            d[item]	= stuff
    
    d['pageName']	= ': Event Display'
    d['message']	= evdisp.message()
    d['navtable']	= TopTable(domain)
    d['hometable']	= HomeTable(p3s_domain, dqm_domain)
    
    return render(request, 'display1.html', d)
#########################################################    
# purStr += ('[new Date(%s), %s],') % (t.strftime("%Y, %m-1, %d, %H, %M, %S"), forChart.lifetime)

