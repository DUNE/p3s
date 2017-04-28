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

def index(request):
    out		= request.GET.get('out','')

    domain	= request.get_host()
    hostname	= settings.HOSTNAME

    summaryData = []

    dataDict = collections.OrderedDict()

    dataDict['pilots']	=	{'entry':'Pilots: total/idle/running/stopped', 'data':(pilot.N(), pilot.N(state='no jobs'), pilot.N(state='running'), pilot.N(state='stopped'))}

    
    dataDict['jobs']	=	{'entry':	'Jobs: total/defined/running/finished',	'data':(job.N(),	job.Ndef(),	job.Nrun(),	job.Nfin())}
    dataDict['workflows']=	{'entry':	'Workflows: total/-/-/-',		'data':(workflow.N(),	'-',		'-',		'-')}
    dataDict['datasets']=	{'entry':	'Datasets: total/-/-/-',		'data':(dataset.N(),	'-',		'-',		'-')}

    if(out=='json'): return HttpResponse(json.dumps(dataDict))
    
    for k in dataDict.keys(): summaryData.append({'Object': dataDict[k]['entry'],'Number': "%s/%s/%s/%s" % dataDict[k]['data']})

    tSummary = SummaryTable(summaryData)
    timeString = datetime.datetime.now().strftime('%x %X')+' '+timezone.get_current_timezone_name()
    
    systemData = []
    systemData.append({'attribute': 'Current time',	'value': timeString})
    systemData.append({'attribute': 'Server',	'value': hostname})
    systemData.append({'attribute': 'Uptime',	'value': uptime()})
    systemData.append({'attribute': '>',	'value': '>'})

    
    tSystem = DetailTable(systemData)

    return render(request, 'index.html',
                  {
                      'domain':		domain,
                      'hostname':	hostname,
                      'uptime':		uptime(),
                      'time':		timeString,
                      'summary':	tSummary,
                      'system':		tSystem,
                  }
    )
#
#
def test(request):
    return HttpResponse('test')
