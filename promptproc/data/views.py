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
    t0		= timezone.now()
    
    post	= request.POST
    
    d_uuid = post.get('uuid','')
    
    if(d_uuid==''):
        return HttpResponse("Missing uuid")
    
    d = dataset(
        uuid	= d_uuid,
        name	= post.get('name',''),
        dirpath	= post.get('dirpath','dummypath'), # designed to fail if not set
        state	= post.get('state',''),
        comment	= post.get('comment',''),
        datatype= post.get('datatype',''),
        wf     	= post.get('wf',''),
        wfuuid 	= post.get('wfuuid',''),
        targetuuid= post.get('targetuuid',''),
        ts_reg	= t0,
        ts_upd	= t0,
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
    d_uuid	= post.get('uuid','')
    d_name	= post.get('name','')
    d		= None

    if(d_uuid=='' and d_name==''):
        return HttpResponse("Missing identifyer")


    if(d_uuid!=''):
        try:
            d = dataset.objects.get(uuid=d_uuid)
        except:
            pass

    if(d is None):
        return HttpResponse("DS %s not found" % d_uuid)
    
    for k in ('name', 'state', 'comment', 'datatype', 'wf', 'wfuuid','targetuuid'):
        if(k in post.keys()): d.__dict__[k]=post[k]
        
    d.ts_upd = timezone.now()
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

###################################################
def getdata(request):
    name = request.GET.get('name','')

    return HttpResponse(serializers.serialize("json", dataset.objects.filter(name=name)))

