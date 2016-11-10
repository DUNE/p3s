import datetime
import uuid

from django.shortcuts			import render
from django.http			import HttpResponse
from django.views.decorators.csrf	import csrf_exempt
from django.utils			import timezone
from django.core			import serializers

from .models import pilot

def detail(request):
    pilot_uuid	= request.GET.get('uuid','')
    pilot_pk	= request.GET.get('pk','')

    if(pilot_uuid == '' and pilot_pk == ''):
        return HttpResponse("Empty pilot id")

    if(pilot_uuid != ''):
        p = pilot.objects.get(uuid=pilot_uuid)
    else:
        p = pilot.objects.get(pk=pilot_pk)
        
    data = serializers.serialize('json', [ p, ]) #    print(data)
    
    return HttpResponse(data)


def req_work(request):
    pilot_uuid	= request.GET.get('uuid','')
    print(pilot_uuid)
    return HttpResponse('')


@csrf_exempt
def addpilot(request):
    
    post	= request.POST
    p_uuid	= post['uuid']
    
    p = pilot(
        cluster		= 'default', # fixme
        host		= post['host'],
        uuid		= p_uuid,
        ts_created	= post['ts'],
        ts_reg		= timezone.now() # The following is not TZ-aware: ts_reg = datetime.datetime.now()
    )

    p.save()
    
    return HttpResponse("%s" % p_uuid )
