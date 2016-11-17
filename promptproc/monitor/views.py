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
    pilot_uuid	= request.GET.get('uuid','')
    pilot_pk	= request.GET.get('pk','')

    now		= datetime.datetime.now()
    domain	= request.get_host()
    d=dict(domain=domain, time=str(now))
    po = pilot.objects
    if(pilot_uuid == '' and pilot_pk == ''):
        d['pilots'] = po.all()

    if(pilot_uuid != ''):
        d['pilots'] = po.filter(uuid=pilot_uuid)
        
    if(pilot_pk != ''):
        d['pilots'] = po.filter(pk=pilot_pk)
        
    return render(request, 'pilots.html', d)
    
#    return HttpResponse(data)
# for later:
#    data = serializers.serialize('json', [ p, ])
###################################################
#def data_handler(request):
###################################################
def jobs(request):
    job_id = request.GET.get('job','')
    latest = request.GET.get('latest','')
    if(latest!=''):
        add()
        j = job.objects.latest(latest)
        return HttpResponse("Job %s" % j.uuid)

    if(job_id == ''):
        now = datetime.datetime.now()
        return render(request, 'jobs.html',
                      {
                          'jobs': job.objects.all(),
                          'time': str(now)
                      }
        )


    print(job_id)
    ts = job.objects.get(id=job_id).ts_def
    print(ts)
    return HttpResponse("You're looking at job %s." % job_id)
