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
    # FIXME - the "order_by" is slow an is included here provisionally
    # until I create a more optimal way to get the top priority jobs -mxp-

    j = None
    pilot_uuid	= request.GET.get('uuid','')
    try:
        j = job.objects.order_by('-priority')
        print(j[0].uuid)
    except:
        return HttpResponse('')
    
    if(j==None): return HttpResponse('') # extra safety

    p		= pilot.objects.get(uuid=pilot_uuid)
    p.ts_lhb	= timezone.now()
    p.save()
    
    data = serializers.serialize('json', [ j[0], ])
    return HttpResponse(data)

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


######### CODE SAMPLES TEMPORARILY KEPT #################
#     data = serializers.serialize('json', [ p, ])
#     return HttpResponse(data)


