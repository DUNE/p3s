import datetime
import collections
import json

from django.shortcuts	import render
from django.http	import HttpResponse
from django.http	import HttpResponseRedirect # for future dev
from django.utils	import timezone
from django.conf	import settings

# Provisional, for stats - don't forget to delete
# if this view is refactored:
from jobs.models			import job
from data.models			import dataset, datatype
from pilots.models			import pilot
from workflows.models			import dag, dagVertex, dagEdge
from workflows.models			import workflow
from monitor.monitorTables		import *



from utils.timeUtils import uptime
from utils.timeUtils import loadavg

def index(request):
    summaryData = []
    jobsData = []
    
    out		= request.GET.get('out','') # format

    domain	= request.get_host()
    upt		= uptime()
    ldavg	= loadavg()

    hostname	= settings.HOSTNAME
    dirpath	= settings.DIRPATH
    dqm_domain	= settings.DQM_DOMAIN

    # Accomodate testing on the custom ssh tunnel
    if(domain=='localhost:8008') : dqm_domain = 'localhost:8009'
    
    dqm_host	= settings.DQM_HOST
    
    dataDict = collections.OrderedDict()

    # Note to self - the N method also takes site, must think about how to use it 
    dataDict['pilots']	=	{'entry':'Pilots: total/idle/running/stopped/TO',
                                 'data':(
                                     pilot.N(),
                                     pilot.N(state='no jobs'),
                                     pilot.N(state='running'),
                                     pilot.N(state='stopped'),
                                     pilot.N(state='timeout'),

                                 )}
    
    dataDict['jobs']	=	{'entry': 'Jobs: total/defined/running/finished/TO',
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
                if(missing>0):
                    for i in range(0,missing): myStr+='_'
                    
                string+=myStr
            summaryData.append({'Object': dataDict[k]['entry'],'Number': string })
        except:
            pass

    summaryData.append({'Object': 'Jobs finished as reported by pilots' , 'Number': "%s" % pilot.jobsDone() })

    tSummary = SummaryTable(summaryData)
    timeString = datetime.datetime.now().strftime('%X %x')+' '+timezone.get_current_timezone_name()

    jobsData.append(
        {
            'State':'Defined',
            'OneMin':job.timeline('ts_def', 60),
            'TenMin':job.timeline('ts_def', 600),
            'OneHour':job.timeline('ts_def', 3600),
            'TwoHours':job.timeline('ts_def', 7200),
            'Day':job.timeline('ts_def', 24*3600)
        }
    )
    
    jobsData.append(
        {
            'State':'Started',
            'OneMin':job.timeline('ts_sta', 60),
            'TenMin':job.timeline('ts_sta', 600),
            'OneHour':job.timeline('ts_sta', 3600),
            'TwoHours':job.timeline('ts_sta', 7200),
            'Day':job.timeline('ts_sta', 24*3600)
        }
    )
    
    jobsData.append(
        {
            'State':'Stopped',
            'OneMin':job.timeline('ts_sto', 60),
            'TenMin':job.timeline('ts_sto', 600),
            'OneHour':job.timeline('ts_sto', 3600),
            'TwoHours':job.timeline('ts_sto', 7200),
            'Day':job.timeline('ts_sto', 24*3600)
        }
    )
    
    tJobs = TimelineTable(jobsData)

    
    systemData = []
    systemData.append({'attribute': 'Uptime',		'value': upt})
    systemData.append({'attribute': 'Load',		'value': ldavg})
    systemData.append({'attribute': 'Sites',		'value': ",".join(site.list())})
    systemData.append({'attribute': 'Data location',	'value': dirpath})

    
    tSystem = DetailTable(systemData)

    return render(request, 'index.html',
                  {
                      'domain':		domain,
                      'host':		hostname,
                      'dqm_domain':	dqm_domain,
                      'dqm_host':	dqm_host,
                      'uptime':		uptime(),
                      'time':		timeString,
                      'summary':	tSummary,
                      'jobs':		tJobs,
                      'system':		tSystem,
                      'time':		timeString,
                  }
    )

####
def pilotinfo(request):
    activePilots = pilot.N(state='running')+pilot.N(state='no jobs')+pilot.N(state='active')+pilot.N(state='finished')
    return HttpResponse(str(activePilots))
