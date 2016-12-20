#########################################################
#                PILOTS VIEW                            #
#########################################################
# TZ-awarewness:					#
# The following is not TZ-aware: datetime.datetime.now()#
# so we are using timzone.now() where needed		#
#########################################################
# General Python:
import datetime
import uuid
import json

# Django
from django.shortcuts			import render
from django.http			import HttpResponse
from django.views.decorators.csrf	import csrf_exempt
from django.utils			import timezone
from django.core			import serializers
from django.conf			import settings

# Local models
from .models				import dataset

#########################################################
#
# Register data with the server:
@csrf_exempt
def register(request):
    post	= request.POST
    ds_uuid	= post['uuid']
    
    d = dataset(
        uuid		= ds_uuid,
    )

    d.save()

    
    return HttpResponse("DS %s" % ds_uuid)

