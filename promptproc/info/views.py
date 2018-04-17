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
from logic.models			import user


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


    times	= (('OneMin',60),('TenMin',600),('OneHour',3600),('TwoHours',7200),('Day',24*3600))
    states	= (
        ('defined','ts_def',None),
        ('started','ts_sta',None),
        ('stopped','ts_sto',None),
        ('pilotTO','ts_sto','pilotTO'),
        ('over time limit','ts_sto','timelimit'),
        ('errors','ts_sto','error'),
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
    return render(request, 'index.html',
                  {
                      'domain':		domain,
                      'host':		hostname,
                      'dqm_domain':	dqm_domain,
                      'dqm_host':	settings.SITE['dqm_host'],
                      'uptime':		uptime(),
                      'time':		timeString,
                      'summary':	tSummary,
                      'jobs':		tJobs,
                      'system':		tSystem,
                      'time':		timeString,
                      'users':		users,
                  }
    )

####
def pilotinfo(request):
    activePilots = pilot.N(state='running')+pilot.N(state='no jobs')+pilot.N(state='active')+pilot.N(state='finished')
    return HttpResponse(str(activePilots))
