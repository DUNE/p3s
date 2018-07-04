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

from utils.navbar	import TopTable, HomeTable

def index(request):

    dqm_domain, dqm_host, p3s_users, p3s_jobtypes = None, None, None, None

    try:
        dqm_domain	= settings.SITE['dqm_domain']
        dqm_host	= settings.SITE['dqm_host']
        p3s_jobtypes	= settings.SITE['p3s_jobtypes']
        p3s_services	= settings.SITE['p3s_services']
    except:
        return HttpResponse("error: check local.py for dqm_domain,dqm_host,p3s_jobtypes, p3s_services")

    
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
                      'hometable':	HomeTable(domain, dqm_domain),
                  }

)

