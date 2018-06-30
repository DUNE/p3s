import datetime
import collections
import json

from django.shortcuts	import render
from django.http	import HttpResponse
from django.http	import HttpResponseRedirect # for future dev
from django.utils	import timezone
from django.conf	import settings


from django.utils.safestring		import mark_safe

# Provisional, for stats - don't forget to delete
# if this view is refactored:
from jobs.models			import job
from data.models			import dataset, datatype
from pilots.models			import pilot
from workflows.models			import dag, dagVertex, dagEdge
from workflows.models			import workflow
from monitor.monitorTables		import *
from logic.models			import user

from utils.selectorUtils 		import dropDownGeneric, boxSelector
from utils.timeUtils import uptime
from utils.timeUtils import loadavg

from utils.navbar			import TopTable, HomeTable

refreshChoices = [('', 'Never'), ('5', '5s'), ('10', '10s'), ('30', '30s'), ('60','1min') ]

###############################################################################################
# ---
def makeJobLink(domain, what):
    if(what=='Total'or what=='started'):
        return mark_safe('<a href="http://'+domain+'/monitor/jobs">'+what+'</a>')
    else:
        return mark_safe('<a href="http://'+domain+'/monitor/jobs?state='+what+'">'+what+'</a>')
# ---
def makePilotLink(domain, what):
    if(what=='Total'):
        return mark_safe('<a href="http://'+domain+'/monitor/pilots">'+what+'</a>')
    else:
        return mark_safe('<a href="http://'+domain+'/monitor/pilots?state='+what+'">'+what+'</a>')
#######################
def index(request):
    if request.method == 'POST':
        q = '?'
        try:
            refreshSelector = dropDownGeneric(request.POST,
                                              label='Refresh',
                                              choices=refreshChoices,
                                              tag='refresh')
            
            if refreshSelector.is_valid():
                a = refreshSelector.handleDropSelector()
                if(a!=''): q+=a
        except:
            pass

        return HttpResponseRedirect(q)


    # ---

    refresh		= request.GET.get('refresh', None)
    refreshSelector	= None
    try:
        refreshSelector = dropDownGeneric(label='Refresh',
                                          initial={'refresh': refresh},
                                          choices=refreshChoices,
                                          tag='refresh')
            
    except:
        pass


    summaryData = []
    jobsData = []
    
    out		= request.GET.get('out','') # format

    domain	= request.get_host()
    upt		= uptime()
    ldavg	= loadavg()

    hostname	= settings.HOSTNAME
    dirpath	= settings.SITE['dirpath']
    dqm_domain	= settings.SITE['dqm_domain']

    # Accomodate testing on the custom ssh tunnel
    if(domain=='localhost:8008') : dqm_domain = 'localhost:8009'
    
    dataDict = collections.OrderedDict()

    # Note to self - the N method also takes site, must think about how to use it 
    dataDict['pilots']	=	{'entry':'Pilots:_____total_____idle___running__stopped____TO',
                                 'data':(
                                     pilot.N(),
                                     pilot.N(state='no jobs'),
                                     pilot.N(state='running'),
                                     pilot.N(state='stopped'),
                                     pilot.N(state='timeout'),

                                 )}
    
    dataDict['jobs']	=	{'entry': 'Jobs:_____total___defined__running___finished____TO',
                                 'data':(
                                     job.N(),
                                     job.N(state='defined'),
                                     job.N(state='running'),
                                     job.N(state='finished'),
                                     job.N(state='pilotTO')
                                 )}

    
    dataDict['workflows']=	{'entry':'Workflows: total', 'data':(workflow.N(),)}
    
    dataDict['datasets']=	{'entry':'Datasets:  total', 'data':(dataset.N(),)}
    
    dataDict['domain']	= domain
    dataDict['host']	= hostname
    dataDict['uptime']	= upt

    if(out=='json'): return HttpResponse(json.dumps(dataDict))


    for k in dataDict.keys():
        try:
            string = ''
            for element in dataDict[k]['data']:
                myStr=str(element)
                missing=7-len(myStr)
                expanded=''
                if(missing>0):
                    for i in range(0,missing): expanded+='_'
                string+=expanded+myStr
                    
            summaryData.append({'Object': dataDict[k]['entry'],'Number': string })
        except:
            pass

    summaryData.append({'Object': 'Jobs finished as reported by pilots' , 'Number': "%s" % pilot.jobsDone() })

    tSummary	= SummaryTable(summaryData)
    timeString	= datetime.datetime.now().strftime('%X %x')+' '+timezone.get_current_timezone_name()


    # Pilot summary
    pilotSummaryData = []

    for what in ('Total','no jobs', 'running', 'active', 'timeout'):
        pilotSummaryData.append({'State':(makePilotLink(domain, what)),	'Count': pilot.N(what)})
    
    pilotSummaryData.append({'State':' ',	'Count': ' '}) # placeholder
    pilotSummaryData.append({'State':' ',	'Count': ' '}) # placeholder
    
    pilotSummary = ShortSummaryTable(pilotSummaryData)
    
    # Job summary
    jobSummaryData = []

    for what in ('Total','defined', 'running', 'finished','pilotTO'):
        jobSummaryData.append({'State':(makeJobLink(domain, what)),	'Count': job.N(what)})
    
    jobSummaryData.append({'State':' ',	'Count': ' '}) # placeholder
    jobSummaryData.append({'State':' ',	'Count': ' '}) # placeholder
    
    jobSummary = ShortSummaryTable(jobSummaryData)

    times	= (('OneMin',60),('TenMin',600),('OneHour',3600),('TwoHours',7200),('Day',24*3600))
    
    states	= (
        (makeJobLink(domain, 'defined'),	'ts_def',None),
        (makeJobLink(domain, 'started'),	'ts_sta',None),
        (makeJobLink(domain, 'finished'),	'ts_sto',None),
        (makeJobLink(domain, 'pilotTO'),	'ts_sto','pilotTO'),
        (makeJobLink(domain, 'timelimit'),	'ts_sto','timelimit'),
        (makeJobLink(domain, 'error'),		'ts_sto','error'),
#        (mark_safe('<a href="http://'+domain+'/monitor/jobs?state=error">'+'errors</a>'),'ts_sto','error'),
    )
    
    for s in states:
        tmpDict = collections.OrderedDict()
        tmpDict['State']=s[0]
        for t in times: tmpDict[t[0]]=job.timeline(s[1], t[1], s[2])
        jobsData.append(tmpDict)
    
    
    tJobs = TimelineTable(jobsData)

    
    systemData = []
    systemData.append({'attribute': 'Uptime',		'value': upt})
    systemData.append({'attribute': 'Load',		'value': ldavg})
    systemData.append({'attribute': 'Sites',		'value': ",".join(site.list())})
    systemData.append({'attribute': 'Data location',	'value': dirpath})

    
    tSystem = DetailTable(systemData)

    users = user.all()

    selectors = []
    selectors.append(refreshSelector)
    
    return render(request, 'index.html',
                  {
                      'domain':		domain,
                      'host':		hostname,
                      'dqm_domain':	dqm_domain,
                      'dqm_host':	settings.SITE['dqm_host'],
                      'uptime':		uptime(),
                      'time':		timeString,
                      'jobsummary':	jobSummary,
                      'pilotsummary':	pilotSummary,
                      'jobs':		tJobs,
                      'system':		tSystem,
                      'time':		timeString,
                      'users':		users,
                      'selectors':	selectors,
                      'refresh':	refresh,
                      'navtable':	TopTable(domain, dqm_domain),
                      'hometable':	HomeTable(domain, dqm_domain),
                  }
    )

####
def pilotinfo(request):
    activePilots = pilot.N(state='running')+pilot.N(state='no jobs')+pilot.N(state='active')+pilot.N(state='finished')
    return HttpResponse(str(activePilots))
