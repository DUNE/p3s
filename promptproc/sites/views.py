#########################################################
################## SITES VIEW ###########################
#########################################################
# TZ-awarewness:					#
# The following is not TZ-aware: datetime.datetime.now()#
# so we are using timezone.now() where needed		#
#########################################################

import uuid
import datetime
import json

from datetime import datetime
from datetime import time
from datetime import timedelta

from django.shortcuts			import render
from django.http			import HttpResponse
from django.views.decorators.csrf	import csrf_exempt
from django.utils			import timezone
from django.core			import serializers

from .models import site as S

from utils.timeUtils import dt

def index(request):
    return HttpResponse("Placeholder")


###################################################
@csrf_exempt
def wns(request):
    
    return HttpResponse("wns")

###################################################
@csrf_exempt
def delete(request):
    post	= request.POST
    name	= post['site']
    
    if(name!=''):
        try:
            S.objects.get(name=name).delete()
            return HttpResponse("Successfully deleted "+name)
        except:
            return HttpResponse("Error deleting "+name)
###################################################
@csrf_exempt
def define(request):
    
    siteInfo	= None
    
    post	= request.POST
    siteJson	= post['site']

    if(siteJson==''):
        return HttpResponse("No data provided for site definition")

    try:
        siteInfo = json.loads(siteJson)
    except:
        return HttpResponse("Error parsing JSON")

    s = S()
    for k in siteInfo.keys():
        setattr(s, k, siteInfo[k])
    s.save()

    return HttpResponse(serializers.serialize("json", [s,]))
###################################################
def sites(request):
    name	= request.GET.get('name','')

    if(name==''):
        objects	= S.objects.all()
    else:
        objects	= [S.objects.get(name=name),]

    return HttpResponse(serializers.serialize("json", objects))

###################################################
