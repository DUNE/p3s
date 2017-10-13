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
    
    out		= request.GET.get('out','') # format

    domain	= request.get_host()
    hostname	= settings.HOSTNAME
    dirpath	= settings.DIRPATH
    upt		= uptime()
    ldavg	= loadavg()

    dataDict = collections.OrderedDict()

    dataDict['domain']	= domain
    dataDict['host']= hostname
    dataDict['uptime']	= upt

    # Note to self - the N method also takes site, must think about
    # how to use it 
    dataDict['pilots']	=	{'entry':'Pilots: total/idle/running/stopped/TO',
                                 'data':(
                                     pilot.N(),
                                     pilot.N(state='no jobs'),
                                     pilot.N(state='running'),
                                     pilot.N(state='stopped'),
                                     pilot.N(state='timeout'),

                                 )}
    
    dataDict['jobs']	=	{'entry': 'Jobs: total/defined/running/finished',
                                 'data':(
                                     job.N(),
                                     job.N(state='defined'),
                                     job.N(state='running'),job.N(state='finished')
                                 )}
    
    dataDict['workflows']=	{'entry':'Workflows: total/-/-/-', 'data':(workflow.N(),'-','-','-','-')}
    
    dataDict['datasets']=	{'entry':'Datasets:  total/-/-/-', 'data':(dataset.N(),	'-','-','-','-')}
    

    if(out=='json'): return HttpResponse(json.dumps(dataDict))
    
    for k in dataDict.keys():
        try:
            summaryData.append({'Object': dataDict[k]['entry'],'Number': "%s/%s/%s/%s/%s" % dataDict[k]['data']})
        except:
            pass

    summaryData.append({'Object': 'Jobs finished as reported by pilots' , 'Number': "%s" % pilot.jobsDone() })

    tSummary = SummaryTable(summaryData)
    timeString = datetime.datetime.now().strftime('%x %X')+' '+timezone.get_current_timezone_name()
    
    systemData = []
    systemData.append({'attribute': 'Current time',	'value': timeString})
    systemData.append({'attribute': 'Server',	'value': hostname})
    systemData.append({'attribute': 'Uptime',	'value': upt})
    systemData.append({'attribute': 'Load',	'value': ldavg})
    systemData.append({'attribute': '>',	'value': '>'})

    
    tSystem = DetailTable(systemData)

    return render(request, 'index.html',
                  {
                      'domain':		domain,
                      'host':		hostname,
                      'uptime':		uptime(),
                      'time':		timeString,
                      'summary':	tSummary,
                      'system':		tSystem,
                      'sites':		",".join(site.list()),
                      'dirpath':	dirpath,
                  }
    )
#
#
def pilotinfo(request):
    activePilots = pilot.N(state='running')+pilot.N(state='no jobs')+pilot.N(state='active')+pilot.N(state='finished')
    return HttpResponse(str(activePilots))
