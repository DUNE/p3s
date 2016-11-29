import datetime

from django.shortcuts	import render
from django.http	import HttpResponse
from django.utils	import timezone
from django.conf	import settings



def index(request):
    domain	= request.get_host()
    hostname	= settings.HOSTNAME
    
    return render(request, 'index.html',
                  {
                      'domain':		domain,
                      'hostname':	hostname,
                      'time':		datetime.datetime.now().strftime('%x %X')
                      
                      # FIXME - deal with timestamp later -mxp-
                      # 'time': str(timezone.now())
                  }
    )
