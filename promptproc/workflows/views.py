from django.shortcuts import render
from django.http import HttpResponse

from .models import dag

def init(request):
    d = dag(name='test')
    if(dag._init):
        status = 'initialized'
    else:
        status = 'not initialized'
    dag._init = True
    return HttpResponse("WF INIT %s %s" % (d, status))

