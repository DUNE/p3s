import datetime
import collections
import json

from django.shortcuts	import render
from django.http	import HttpResponse
from django.http	import HttpResponseRedirect # for future dev
from django.utils	import timezone
from django.conf	import settings

def index(request):
    hostname	= settings.HOSTNAME

    return render(request, 'index.html',
                  {
                      'domain':		'domain',
                      'hostname':	hostname,
                      'uptime':		'uptime()',
                      'time':		'timeString',
                      'summary':	{'tSummary':'summary'},
                      'system':		{'tSystem':'system'},
                      'sites':		'",".join(site.list())',
                  }

)
########    return HttpResponse('test index')
