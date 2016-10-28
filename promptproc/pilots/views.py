from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import pilot

def detail(request):
    pilot_id = request.GET.get('pilot','')
    print(pilot_id)
    ts = pilot.objects.get(id=pilot_id).ts_created
    print(ts)
    return HttpResponse("You're looking at pilot %s." % pilot_id)


@csrf_exempt
def gateway(request):
#    pilot_id = request.GET.get('pilot','')
#    print(pilot_id)
#    ts = pilot.objects.get(id=pilot_id).ts_created
#    print(ts)

    
    p=request.POST
    print(p)
    return HttpResponse("You're looking at the pilot gateway" )
