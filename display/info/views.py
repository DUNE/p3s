import datetime
import collections
import json

from django.shortcuts	import render
from django.http	import HttpResponse
from django.http	import HttpResponseRedirect # for future dev
from django.utils	import timezone
from django.conf	import settings


from utils.timeUtils	import uptime
from utils.timeUtils	import loadavg

from utils.navbar	import TopTable

def index(request):
    hostname	= settings.HOSTNAME
    domain	= request.get_host()
    upt		= uptime()
    ldavg	= loadavg()

    
    return render(request, 'index.html',
                  {
                      'domain':		domain,
                      'hostname':	hostname,
                      'uptime':		upt,
                      'navtable':	TopTable(domain),
                  }

)
########    return HttpResponse('test index')
