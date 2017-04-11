import datetime

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
    
    domain	= request.get_host()
    hostname	= settings.HOSTNAME

    summaryData = []
#    pilotTot	= pilot.N()
#    pilotRun	= pilot.objects.filter(state='running').count()
#    pilotIdle	= pilot.objects.filter(state='no jobs').count()
    
    summaryData.append({'Object': 'Pilots: total/idle/running/stopped',
                        'Number': "%s/%s/%s/%s" % ( pilot.N(), pilot.Nidle(), pilot.Nrun(), pilot.Nstop())})
    
    summaryData.append({'Object': 'Jobs: total/defined/running/finished',
	                'Number':  "%s/%s/%s/%s" % ( job.N(), job.Ndef(), job.Nrun(), job.Nfin())})
    
    summaryData.append({'Object': 'Workflows',	'Number':	workflow.N()})
    summaryData.append({'Object': 'Datasets',	'Number':	dataset.N()})
    

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
