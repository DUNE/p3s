#########################################################
#                      PILOTS                           #
#########################################################
import datetime
import uuid

from django.shortcuts			import render
from django.http			import HttpResponse
from django.views.decorators.csrf	import csrf_exempt
from django.utils			import timezone
from django.core			import serializers

from .models import pilot
from jobs.models import job

#########################################################
# TZ-awarewness:					#
# The following is not TZ-aware: datetime.datetime.now()#
# so we are using timzone.now() where needed		#
#########################################################

def request(request):
    j = None
    p_uuid	= request.GET.get('uuid','')
    try:
        top_jobs = job.objects.order_by('-priority')
        j = top_jobs[0]
    except:
        return HttpResponse('')
    
    if(j==None): return HttpResponse('') # extra safety

    j.state	= 'dispatched'
    j.p_uuid	= p_uuid
    j.ts_dis	= timezone.now()
    j.save()
    
    p		= pilot.objects.get(uuid=p_uuid)
    p.j_uuid	= j.uuid
    p.state	= 'dispatched'
    p.ts_lhb	= timezone.now()
    p.save()
    
    data = serializers.serialize('json', [ j, ])
    return HttpResponse(data)

    # jp = job.objects.values('priority').distinct()
    # pl =  []
    # for item in jp:
    #     val = item['priority']
    #     print(val)
    #     pl.append(val)
    # pl.sort(reverse=True)
    # print(pl)

#########################################################
@csrf_exempt
def addpilot(request):
    
    post	= request.POST
    p_uuid	= post['uuid']
    
    p = pilot(
        state		= post['state'],
        site		= post['site'],
        host		= post['host'],
        uuid		= p_uuid,
        ts_cre		= post['ts'],
        ts_reg		= timezone.now(),
        ts_lhb		= timezone.now()
    )

    p.save()
    
    return HttpResponse("%s" % p_uuid ) # FIXME - think of a meaningful response -mxp-


