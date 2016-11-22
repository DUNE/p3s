import datetime

from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone

#from .models import job


def index(request):
    domain = request.get_host()
    # FIXME - deal with timestamp later -mxp-
    return render(request, 'index.html',
                  {
                      'domain':	domain,
                      'time':	datetime.datetime.now().strftime('%x %X')
#                      'time':	str(timezone.now())
                  }
    )

#    return HttpResponse("Prompt Processing Information System")
