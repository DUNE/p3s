#########################################################
################# JOBS VIEW #############################
#########################################################
# TZ-awarewness:					#
# The following is not TZ-aware: datetime.datetime.now()#
# so we are using timezone.now() where needed		#
#########################################################

import uuid

from django.core			import serializers

from django.shortcuts			import render
from django.http			import HttpResponse
from django.views.decorators.csrf	import csrf_exempt
from django.utils			import timezone

from .models import job


def index(request):
    return HttpResponse("Placeholder")


###################################################
@csrf_exempt
def add(request):
    
    post	= request.POST
    
    j = job(
        uuid		= post['uuid'],
        user		= post['user'],
        jobtype		= post['jobtype'],
        payload		= post['payload'],
        env		= post['env'],
        priority	= post['priority'],
        state		= post['state'],
        ts_def		= post['ts'],
        timelimit	= post['timeout'],
        name		= post['name'],
    )

    j.save()
    
    return HttpResponse("%s" % post['uuid'] )

###################################################
@csrf_exempt
def adjust(request):
    # fixme - improve error handling such as for missing or screwy arguments

    post	= request.POST
    j_uuid	= post['uuid']

    try:
        priority = int(post['priority'])
    except:
        priority = -1
    try:
        state = post['state']
    except:
        state = ''

    #    print(j_uuid) print(priority) print(state)
    try:
        j = job.objects.get(uuid=j_uuid)
    except:
        return HttpResponse("%s not found" % j_uuid )
        

    if(priority!=-1):
        j.priority = priority
    if(state!=''):
        j.state = state

    j.save()
    
    return HttpResponse("%s updated" % j_uuid )

###################################################
@csrf_exempt
def delete(request):
    # fixme - improve error handling such as for missing or screwy arguments

    post		= request.POST
    j_uuid, j_pk	= None, None

    try:
        j_uuid = post['uuid']
    except:
        pass

    try:
        j_pk = post['pk']
    except:
        pass

    if(j_uuid is None and j_pk is None):
        return HttpResponse("Missing key for deletion")

    if(j_pk=='ALL' or j_uuid=='ALL'):
        try:
            j = job.objects.all().delete()
        except:
            return HttpResponse("DELETE ALL: FAILED")
        return HttpResponse("DELETE ALL: SUCCESS")

    if(j_uuid):
        try:
            j = job.objects.get(uuid=j_uuid)
        except:
            return HttpResponse("%s not found" % j_uuid )

        j.delete()
        return HttpResponse("%s deleted" % j_uuid )

    if(j_pk):
        try:
            j = job.objects.get(pk=j_pk)
        except:
            return HttpResponse("%s not found" % j_pk )

        j.delete()
        return HttpResponse("%s deleted" % j_pk )
    
    return HttpResponse("Inconsistent state in job deletion view")

###################################################
def detail(request):
    j_uuid = request.GET.get('uuid','')

    if(j_uuid == ''):
        return HttpResponse("Job not specified.")
    print(j_uuid)
    j = job.objects.get(uuid=j_uuid)

    data = serializers.serialize('json', [ j, ])
    return HttpResponse(data)
#    return HttpResponse("You're looking at job %s." % j_uuid)
