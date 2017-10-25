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
def register(request):
    post	= request.POST
    
    d = dataset(
        uuid	= post.get('uuid','1'),
        name	= post.get('name','foo'),
        state	= post.get('state','moo'),
        comment	= post.get('comment','+'),
        datatype= post.get('datatype','TXT'),
        wf     	= post.get('wf',''),
        wfuuid 	= post.get('wfuuid',''),
    )

    d.save()

    return HttpResponse("DS %s" % d.name)

###################################################
@csrf_exempt
def delete(request):
    post	= request.POST
    d_uuid	= post['uuid']
    
    d		= None
    
    if(d_uuid=='ALL'):
        try:
            dataset.objects.all().delete()
        except:
            return HttpResponse("DELETE ALL: FAILED")

        return HttpResponse("DELETE ALL: SUCCESS")

    try:
        print(d_uuid)
        d = dataset.objects.get(uuid=d_uuid)
    except:
        return HttpResponse("%s not found" % d_uuid )

    d.delete()
    return HttpResponse("%s deleted" % d_uuid )


#########################################################
# Adjust data on the server:
@csrf_exempt
def adjust(request):
    post	= request.POST
    d_uuid	= post['uuid']

    d = dataset.objects.get(uuid=d_uuid)

    for k in ('name', 'state', 'comment', 'datatype', 'wf', 'wfuuid'):
        if(k in post.keys()): d.__dict__[k]=post[k]
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

    
    return HttpResponse("Data Type %s" % name)
###################################################
@csrf_exempt
def deletetype(request):
    post	= request.POST
    name	= post['name']

    try:
        dt = datatype.objects.get(name=name)
    except:
        return HttpResponse("%s not found" % name )

    dt.delete()
    return HttpResponse("%s deleted" % name )


