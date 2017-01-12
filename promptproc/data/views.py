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
from .models import dataset, datatype

#########################################################
# Register data with the server:
@csrf_exempt
def registerdata(request):
    post	= request.POST
    
    d = dataset(
        uuid	= post['uuid'],
        name	= post['name'],
        state	= post['state'],
        comment	= post['comment'],
        datatype= post['datatype'],
        wf     	= post['wf'],
        wfuuid 	= post['wfuuid'],
    )

    d.save()

    return HttpResponse("DS %s" % d.name)

#########################################################
# Register datatype with the server:
@csrf_exempt
def registertype(request):
    post	= request.POST
    name	= post['name']
    ext		= post['ext']
    comment	= post['comment']
    
    d = datatype(
        name		= name,
        ext		= ext,
        comment		= comment,
    )

    d.save()

    
    return HttpResponse("DT %s" % ds_uuid)

#########################################################
# Adjust data on the server:
@csrf_exempt
def adjustdata(request):
    post	= request.POST
    d_uuid	= post['uuid']

    d = dataset.objects.get(uuid=d_uuid)

    for k in ('name', 'state', 'comment', 'datatype', 'wf', 'wfuuid'):
        if(k in post.keys()): d.__dict__[k]=post[k]
    d.save()

    return HttpResponse("DS %s" % d.name)

