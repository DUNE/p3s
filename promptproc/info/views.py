import datetime

from django.shortcuts	import render
from django.http	import HttpResponse
from django.utils	import timezone
from django.conf	import settings



def index(request):
    domain	= request.get_host()
    hostname	= settings.HOSTNAME

    timeString = datetime.datetime.now().strftime('%x %X')+' '+timezone.get_current_timezone_name()
    return render(request, 'index.html',
                  {
                      'domain':		domain,
                      'hostname':	hostname,
                      'time':		timeString,
                      
                      # FIXME - deal with timestamp later -mxp-
                      # 'time': str(timezone.now())
                  }
    )
