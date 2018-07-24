import django.db.models
from django.db.models			import Max
from django				import forms

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
from utils.navbar			import TopTable, HomeTable


# The tables needed here are defined in a separate unit of code
from .monitorTables import *

#########################################################
JOBTYPECHOICES	= [('', 'All'), ('monitor','monitor'), ('test','test'),]

REFRESHCHOICES	= [('', 'Never'),	('10', '10s'),	('30', '30s'),	('60','1min'),	('120', '2min'),  ]
PAGECHOICES	= [('25','25'),		('50','50'),	('100','100'),	('200','200'),	('400','400'),]
TPCCHOICES	= [('', 'All'),		('1', '1'),	('2','2'),	('5','5'),	('6','6'),	('9','9'),	('10','10'), ]


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

    domain	= request.get_host()
    tsmin	= request.GET.get('tsmin','')
    tsmax	= request.GET.get('tsmax','')
    
    width	= request.GET.get('width','3')
    what	= request.GET.get('what','')
    plane	= request.GET.get('plane','')

    q='what='+what+'&plane='+plane+'&'

    if request.method == 'POST':
        tsSelector = twoFieldGeneric(request.POST,
                                     label1="min. (YYYY-MM-DD HH:MM:SS)",
                                     field1="tsmin",
                                     init1=tsmin,
                                     label2="max. (YYYY-MM-DD HH:MM:SS)",
                                     field2="tsmax",
                                     init2=tsmax)
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
        if(tsmin!=''):
            objs = objs.filter(ts__gte=tsmin)
            for o in objs: print(o.ts)
        if(tsmax!=''):	objs = objs.filter(ts__lte=tsmax)

        dataStr = ''
        for forChart in objs:
            try: # template: [new Date(2014, 10, 15, 7, 30), 1],
                t = forChart.ts
                s = json.loads(forChart.summary)[0]
                data1 = s[patternHits1%plane].split(',')
                data2 = s[patternHits2%plane].split(',')
                dataStr += ('[new Date(Date.UTC(%s)), %s, %s],') % (t.strftime("%Y, %m-1, %d, %H, %M, %S"), data1[tpcNum], data2[tpcNum])
            except:
                break


        myDict["panel"] = 'tpc'+str(tpcNum)
        myDict["timeseries"]=dataStr

        if(what=='hits'):
            myDict["vAxis"]='hits/RMS'
            myDict["main"]='hits'
            myDict["extra"]='rms'
        else:
            myDict["vAxis"]='S/N'
        
        timeSeries.append(myDict)
        cnt+=1
        if(cnt == W):
            bigStruct.append(timeSeries)
            timeSeries = []
            cnt=0
            
    bigStruct.append(timeSeries)

    print(bigStruct)
    
    d = {}
    d['rows']	= bigStruct
    d['domain']	= domain
    
    tsSelector = twoFieldGeneric(label1="min. (YYYY-MM-DD HH:MM:SS)",
                                 field1="tsmin",
                                 init1=tsmin,
                                 label2="max. (YYYY-MM-DD HH:MM:SS)",
                                 field2="tsmax",
                                 init2=tsmax)
    
    selectors = []
    selectors.append(tsSelector)

    d['selectors']	= selectors
    d['pageName']	= ': '+what+' timeline'
    d['navtable']	= TopTable(domain)
    d['hometable']	= HomeTable(p3s_domain, dqm_domain, domain)

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
    
    domain	= request.get_host()
    tsmin	= request.GET.get('tsmin','')
    tsmax	= request.GET.get('tsmax','')
    width	= request.GET.get('width','3')

    # tz = pytz.timezone('Europe/Berlin')
    # print(tz)
    #    if(tsmin!=''): tsminFixed = datetime.datetime(tsmin) # , tzinfo=tz)
    #    tsminFixed.replace(tzinfo=tz)    

    q=''

    if request.method == 'POST':
        tsSelector = twoFieldGeneric(request.POST,
                                     label1="min. (YYYY-MM-DD HH:MM:SS)",
                                     field1="tsmin",
                                     init1=tsmin,
                                     label2="max. (YYYY-MM-DD HH:MM:SS)",
                                     field2="tsmax",
                                     init2=tsmax)
        if tsSelector.is_valid():
            tsmin=tsSelector.getval("tsmin")
            tsmax=tsSelector.getval("tsmax")
            if(tsmin!=''): q+= 'tsmin='+tsmin+'&'
            if(tsmax!=''): q+= 'tsmax='+tsmax+'&'

        return makeQuery('puritychart', q) # will go and get the query results...
    
    #-----------
    # for the charts

    bigPur = []
    purSeries = []
    W=int(width)
    cnt=0
    for tpcNum in (1,2,5,6,9,10):
        purDict = {}

        objs = pur.objects.order_by('-pk').filter(tpc=tpcNum)
        if(tsmin!=''):	objs = objs.filter(ts__gte=tsmin)
        if(tsmax!=''):	objs = objs.filter(ts__lte=tsmax)

        purStr=''

        for forChart in objs:
            try: # template: [new Date(2014, 10, 15, 7, 30), 1],
                t = forChart.ts
                
                if(what=='purity'):
#                    purStr += ('[new Date(%s), %s],') % (t.strftime("%Y, %m-1, %d, %H, %M, %S"), forChart.lifetime)
                    purStr += ('[new Date(Date.UTC(%s)), %s],') % (t.strftime("%Y, %m-1, %d, %H, %M, %S"), forChart.lifetime)
                else:
                    purStr += ('[new Date(Date.UTC(%s)), %s],') % (t.strftime("%Y, %m-1, %d, %H, %M, %S"), forChart.sn)
            except:
                break
    
        purDict["panel"] = 'tpc'+str(tpcNum)
        purDict["timeseries"]=purStr
        
        if(what=='purity'):
            purDict["main"]='lifetime'
            purDict["vAxis"]='Lifetime (ms)'
        else:
            purDict["vAxis"]='S/N'
            purDict["main"]='s/n'
            
        purSeries.append(purDict)
        cnt+=1
        if(cnt == W):
            bigPur.append(purSeries)
            purSeries = []
            cnt=0
            
    bigPur.append(purSeries)

    # print(bigPur)
    d = {}
    d['rows']	= bigPur #purSeries
    d['domain']	= domain
    
    tsSelector = twoFieldGeneric(label1="min. (YYYY-MM-DD HH:MM:SS)",
                                 field1="tsmin",
                                 init1=tsmin,
                                 label2="max. (YYYY-MM-DD HH:MM:SS)",
                                 field2="tsmax",
                                 init2=tsmax)
    
    selectors = []
    selectors.append(tsSelector)


    
    d['selectors']	= selectors
    d['pageName']	= ': '+what+' timeline'
    d['navtable']	= TopTable(domain)
    d['hometable']	= HomeTable(p3s_domain, dqm_domain, domain)

    # d['vAxis']	=garnish[what]['vAxis']
    #    print(what,d['vAxis'])

    return render(request, 'purity_chart1.html', d)

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
        refreshSelector = dropDownGeneric(request.POST,
                                          label='Refresh',
                                          choices=REFRESHCHOICES,
                                          tag='refresh')
            
        if refreshSelector.is_valid(): q += refreshSelector.handleDropSelector()

        perPageSelector	= dropDownGeneric(request.POST,
                                          initial={'perpage':perpage},
                                          label='# per page',
                                          choices = PAGECHOICES,
                                          tag='perpage')
        
        if perPageSelector.is_valid(): q += perPageSelector.handleDropSelector()

        if(what=='monrun'):
            typeSelector = dropDownGeneric(request.POST, label='Type', choices=JOBTYPECHOICES, tag='jobtype')
            if typeSelector.is_valid(): q += typeSelector.handleDropSelector()

        
        if(what=='pur'):
            tpcSelector = dropDownGeneric(request.POST,
                                          initial={'tpc':tpc},
                                          label='tpc',
                                          choices = TPCCHOICES,
                                          tag='tpc')
            if tpcSelector.is_valid(): q += tpcSelector.handleDropSelector()
        
        tsSelector = twoFieldGeneric(request.POST,
                                     label1="min. (YYYY-MM-DD HH:MM:SS)",
                                     field1="tsmin",
                                     init1=tsmin,
                                     label2="max. (YYYY-MM-DD HH:MM:SS)",
                                     field2="tsmax",
                                     init2=tsmax)
        if tsSelector.is_valid():
            tsmin=tsSelector.getval("tsmin")
            tsmax=tsSelector.getval("tsmax")
            
            if(tsmin!=''): q+= 'tsmin='+tsmin+'&'
            if(tsmax!=''): q+= 'tsmax='+tsmax+'&'

        if(what=='evdisp'):
            juuidSelector = twoFieldGeneric(request.POST,
                                            label1="Job UUID",
                                            field1="j_uuid",
                                            init1=j_uuid,
                                            label2="Data Type",
                                            field2="d_type",
                                            init2=d_type)
            if juuidSelector.is_valid():
                
                j_uuid=juuidSelector.getval("j_uuid")
                if(j_uuid!=''): q+= 'j_uuid='+j_uuid+'&'
                
                d_type=juuidSelector.getval("d_type")
                if(d_type!=''): q+= 'd_type='+d_type+'&'
                
            runSelector =  twoFieldGeneric(request.POST,
                                           label1="Run",
                                           field1="run",
                                           init1=run,
                                           label2="Event",
                                           field2="event",
                                           init2=evnum)
            
            if runSelector.is_valid():
                run=runSelector.getval("run")
                if(run!=''): q+= 'run='+run+'&'
                
                event=runSelector.getval("event")
                if(event!=''): q+= 'evnum='+event+'&'
                

        return makeQuery(url, q) # We built a query and will come to same page/view with the query parameters


    ###########################################################################
    # -------------------------------------------------------------------------
    ###########################################################################
    

    now		= datetime.datetime.now().strftime('%x %X')+' '+timezone.get_current_timezone_name() # beautify later
    d		= dict(domain=domain, time=str(now))
#    objs	= eval(what).objects.order_by('-pk').all()
    objs	= eval(what).objects.all()

    if(tsmin!=''):	objs = eval(what).objects.filter(ts__gte=tsmin)# .order_by('-pk')
    if(tsmax!=''):	objs = objs.filter(ts__lte=tsmax)	# .order_by('-pk')
    if(j_uuid!=''):	objs = objs.filter(j_uuid=j_uuid)
    if(jobtype!=''):	objs = objs.filter(jobtype=jobtype)
    if(d_type!=''):	objs = objs.filter(datatype=d_type)
    if(run!=''):	objs = objs.filter(run=run)
    if(evnum!=''):	objs = objs.filter(evnum=evnum)
    if(tpc!=''):	objs = objs.filter(tpc=tpc)

    #-------------

    t = None
    if(tbl=='RunTable'):
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

    selectors = []
    # ---
    refreshSelector = dropDownGeneric(label='Refresh',
                                      initial={'refresh': refresh},
                                      choices=REFRESHCHOICES,
                                      tag='refresh')
    selectors.append(refreshSelector)
    # ---
    perPageSelector = dropDownGeneric(initial={'perpage':perpage},
                                      label='# per page',
                                      choices = PAGECHOICES,
                                      tag='perpage')
    selectors.append(perPageSelector)

    if(what=='monrun'):
        typeSelector	= dropDownGeneric(initial={'jobtype':initJobType},
	                                  label='Type',
	                                  choices = JOBTYPECHOICES,
                                          tag='jobtype')
        selectors.append(typeSelector)
        
    # ---
    tsSelector = twoFieldGeneric(
        label1="min. (YYYY-MM-DD HH:MM:SS)",
        field1="tsmin",
        init1=tsmin,
        label2="max. (YYYY-MM-DD HH:MM:SS)",
        field2="tsmax",
        init2=tsmax
    )
    
    selectors.append(tsSelector)
    # ---
    if(what=='pur'):
        tpcSelector = dropDownGeneric(initial={'tpc':tpc},
                                      label='tpc',
                                      choices = TPCCHOICES,
                                      tag='tpc')
        selectors.append(tpcSelector)
    # ---
    if(what=='evdisp'):
        juuidSelector = twoFieldGeneric(label1="Job UUID",
                                        field1="j_uuid",
                                        init1=j_uuid,
                                        label2="Data Type",
                                        field2="d_type",
                                        init2=d_type)
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
    d['hometable']	= HomeTable(p3s_domain, dqm_domain, domain)
    
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
@csrf_exempt
def plot18(request):
    domain	= request.get_host()
    run		= request.GET.get('run','')
    return HttpResponse('work in progress')

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
def addmon(request):
    post	= request.POST
    
    summary	= post.get('summary', '')

    s = json.loads(summary)
    # print(s)
    
    m=monrun()
    
    m.run		= post.get('run', '')
    m.subrun		= post.get('subrun', '')
    m.summary		= summary
    m.description	= post.get('description', '')
    m.j_uuid		= post.get('j_uuid', '')
    m.jobtype		= post.get('jobtype', '')

    
    m.ts		= post.get('ts', timezone.now())
    
    # print(m.summary)
    m.save()
        
    return HttpResponse('Adding mon entry for run '+m.run+' subrun '+m.subrun)
#########################################################    
@csrf_exempt
def delmon(request):
    post	= request.POST
    pk		= post.get('pk', '')
    run		= post.get('run', '')

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

    try:
        objs = monrun.objects.filter(run=run)
        l = str(len(objs))
        objs.delete()
        return HttpResponse('Deleted '+l+' mon entries for run '+run)
    except:
        return HttpResponse('Failed to delete mon entries for run '+run)

#########################################################    
def showmon(request):
    domain	= request.get_host()
    host	= request.GET.get('host','')
    run		= request.GET.get('run','')
    subrun	= request.GET.get('subrun','')
    tpcmoncat	= request.GET.get('tpcmoncat','')
    ssprawcat	= request.GET.get('ssprawcat','')
    timingrawcat= request.GET.get('timingrawcat','')
    pdsphitmoncat	= request.GET.get('pdsphitmoncat','')

    url2images = settings.SITE['dqm_monitor_url']

    p3s_domain, dqm_domain, dqm_host, p3s_users, p3s_jobtypes = None, None, None, None, None

    try:
        p3s_domain	= settings.SITE['p3s_domain']
        dqm_domain	= settings.SITE['dqm_domain']
        dqm_host	= settings.SITE['dqm_host']
        p3s_jobtypes	= settings.SITE['p3s_jobtypes']
        p3s_services	= settings.SITE['p3s_services']
    except:
        return HttpResponse("error: check local.py for dqm_domain,dqm_host,p3s_jobtypes, p3s_services")


    
    # This page serves two purposes - if the TPC monitor category
    # is defined, then it shows a page with graphics (depending
    # on the category. If there is no category provided, it shows
    # a choice of catogeries in a table.
    
    d = {}
    d['navtable']	= TopTable(domain)
    d['hometable']	= HomeTable(domain, dqm_domain, domain)
    
    r6 = ("%06d"%int(run))
    s3 = ("%03d"%int(subrun))
    
    if(ssprawcat!=''):
        # print('here')
        obj	= monrun.objects.filter(run=run).filter(subrun=subrun)
        entry	= obj[0]
        j_uuid	= entry.j_uuid
        
        d['tblHeader']	= 'SSP raw decoder  -- run:'+run+' subrun:'+subrun
        d['rows'] = monrun.SSPRawImgURLs(domain, url2images, j_uuid, r6, s3)
        return render(request, 'unitable3.html', d)

    if(timingrawcat!=''):
        item	= monrun.ALLmonitor('timingrawdecoder', int(timingrawcat))
        cat	= item[0]
        obj	= monrun.objects.filter(run=run).filter(subrun=subrun)
        entry	= obj[0]
        j_uuid	= entry.j_uuid
        
        d['tblHeader']	= cat+'  -- run:'+run+' subrun:'+subrun
        d['rows'] = monrun.TimingRawImgURLs(domain, url2images, j_uuid, r6, s3)
        return render(request, 'unitable3.html', d)

        
    if(tpcmoncat!=''):
        item	= monrun.ALLmonitor('tpc', int(tpcmoncat))
        cat	= item[0]
        obj	= monrun.objects.filter(run=run).filter(subrun=subrun)
        entry	= obj[0]
        j_uuid	= entry.j_uuid
        
        d['tblHeader']	= cat+'  -- run:'+run+' subrun:'+subrun

        Ncat = int(tpcmoncat)
        if Ncat in (0,1,2,3,6,7,8):
           d['rows'] = monrun.TPCmonitorURLplanes('tpc', Ncat, domain, url2images, j_uuid, r6, s3)
        elif Ncat in (4,5,9,10):
            d['rows'] = monrun.TPCmonitorURLind(Ncat, domain, url2images, j_uuid, r6, s3)
        else:
           pass
        
        return render(request, 'unitable3.html', d)
    # ---
    if(pdsphitmoncat!=''):
        item	= monrun.ALLmonitor('pdsphit', int(pdsphitmoncat))
        cat	= item[0]
        obj	= monrun.objects.filter(run=run).filter(subrun=subrun)
        entry	= obj[0]
        j_uuid	= entry.j_uuid
        
        d['tblHeader']	= cat+'  -- run:'+run+' subrun:'+subrun

        Ncat = int(pdsphitmoncat)
        if Ncat in (0,1,2,3,4,5,6):
           d['rows'] = monrun.TPCmonitorURLplanes('pdsphit', Ncat, domain, url2images, j_uuid,  r6 , s3)
        else:
           pass
        
        return render(request, 'unitable3.html', d)
    # - we just served a graphic page according to the chosen category

    # ------------------
    # this table presents the categories available (clickable)
    d['tblHeader']	= 'Run:'+run+' subrun:'+subrun

    d['tables']		= []
    
    t = ShowMonTable(monrun.TPCmonitorCatURLs(domain, run, subrun))
    t.changeName('TPC monitor items')
    d['tables'].append(t)
    
    t2 = ShowMonTable(monrun.PDSPHITmonitorCatURLs(domain, run, subrun))
    t2.changeName('PDSP HIT monitor items')
    d['tables'].append(t2)
    
    t3 = ShowMonTable(monrun.TimingRawCatURLs(domain, run, subrun))
    t3.changeName('Timing Raw Decoder and SSP raw decoder')
    d['tables'].append(t3)

    d['navtable']	= TopTable(domain)
    d['hometable']	= HomeTable(p3s_domain, dqm_domain, domain)

    return render(request, 'unitable3.html', d)
    
#########################################################    
def automon(request):
    domain	= request.get_host()
    host	= request.GET.get('host','')
    run		= request.GET.get('run','')
    subrun	= request.GET.get('subrun','')
    category	= request.GET.get('category','')
    filetype	= request.GET.get('filetype','')

    entry = None
    try:
        entry	= monrun.objects.filter(run=run).filter(subrun=subrun)[0]
    except:
        return 'not found'
        
    description = json.loads(entry.description, object_pairs_hook=OrderedDict)
    
    # print('***',category)


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
    
    d = {}
    d['navtable']	= TopTable(domain)
    d['hometable']	= HomeTable(p3s_domain, dqm_domain, domain)
    d['tables']		= []

    if(category!=''):
        j_uuid	= entry.j_uuid

        files = None
        for item in description:
            if(item['Category']==category): files=item['Files'][filetype]
        if(files is None): return 'error'
        
        d['rows'] = monrun.autoMonImgURLs(domain, url2images, j_uuid, files)
        return render(request, 'unitable3.html', d)
    

    for item in description:
        # print(item['Category'])
        list4table = []
        for fileType in item['Files'].keys():
            list4table.append({'items':monrun.autoMonLink(domain,run,subrun,item['Category'],fileType)})
            
        t = ShowMonTable(list4table)
        t.changeName(item['Category'])
        d['tables'].append(t)

    return render(request, 'unitable3.html', d)
#########################################################    
