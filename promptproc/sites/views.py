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


from django.core			import serializers

from django.shortcuts			import render
from django.http			import HttpResponse
from django.views.decorators.csrf	import csrf_exempt
from django.utils			import timezone
from django.core			import serializers

from .models import site



from utils.timeUtils import dt

def index(request):
    return HttpResponse("Placeholder")


###################################################
@csrf_exempt
def wns(request):
    
    return HttpResponse("wns")

###################################################
@csrf_exempt
def sites(request):
    name	= request.GET.get('name','')

    if(name==''):
        objects	= site.objects.all()
    else:
        objects	= [site.objects.get(name=name),]

    return HttpResponse(serializers.serialize("json", objects))

###################################################
