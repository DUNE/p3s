#########################################################
# TZ-awarewness:					#
# The following is not TZ-aware: datetime.datetime.now()#
# so we are using timezone.now() where needed		#
#########################################################

from django.shortcuts import render

import datetime
from django.utils import timezone
from django.utils.timezone import utc

import uuid

from django.shortcuts			import render
from django.http			import HttpResponse
from django.views.decorators.csrf	import csrf_exempt
from django.utils			import timezone
from django.core			import serializers

from pilots.models	import pilot
from jobs.models	import job

# just something for later, advanced tables, not used in the first cut
from django.views.generic.base import TemplateView

try:
    from django.urls import reverse
except ImportError:
    print("FATAL IMPORT ERROR")
    exit(-3)

#########################################################    
def pilots(request):
    return data_handler(request, 'pilots')

#########################################################    
def jobs(request):
    return data_handler(request, 'jobs')

#########################################################    
def data_handler(request, what):
    uuid	= request.GET.get('uuid','')
    pk		= request.GET.get('pk','')

    now		= datetime.datetime.now()
    domain	= request.get_host()
    d=dict(domain=domain, time=str(now))

    objects = None
    if(what=='pilots'):
        template = 'pilots.html'
        objects = pilot.objects
        
    if(what=='jobs'):
        template = 'jobs.html'
        objects = job.objects
        
    if(uuid == '' and pk == ''):	d[what] = objects.all()
    if(uuid != ''):			d[what] = objects.filter(uuid=uuid)
    if(pk != ''):			d[what] = objects.filter(pk=pk)
        
    return render(request, template, d)
#########################################################    
# for later:
#    data = serializers.serialize('json', [ p, ])
