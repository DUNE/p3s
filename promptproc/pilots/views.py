import datetime

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


@csrf_exempt
def addpilot(request):
    
    post	= request.POST
    ts_created	= post['ts']
    uuid	= post['uuid']
    host	= post['host']
    cluster	= 'default' # fixme
    
    ts_created	= post['ts']

    ts_reg	= timezone.now() # This is not TZ-aware: ts_reg = datetime.datetime.now()

    p = pilot(cluster=cluster, host=host, uuid=uuid, ts_created=ts_created, ts_reg=ts_reg)

    p.save()
    
    return HttpResponse("You're looking at the pilot gateway" )
