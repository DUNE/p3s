import datetime

from django.shortcuts	import render
from django.http	import HttpResponse
from django.utils	import timezone
from django.conf	import settings

# Provisional, for stats - don't forget to delete
# if this view is refactored:
from jobs.models			import job
from data.models			import dataset, datatype
from pilots.models			import pilot
from workflows.models			import dag, dagVertex, dagEdge
from workflows.models			import workflow


from utils.timeUtils import uptime

def index(request):
    domain	= request.get_host()
    hostname	= settings.HOSTNAME

    timeString = datetime.datetime.now().strftime('%x %X')+' '+timezone.get_current_timezone_name()
    return render(request, 'index.html',
                  {
                      'domain':		domain,
                      'hostname':	hostname,
                      'uptime':		uptime(),
                      'time':		timeString,
                      'njobs':		job.N(),
                      'nwf':		workflow.N(),
                      'npilots':	pilot.N(),
                      'ndatasets':	dataset.N(),
                  }
    )
