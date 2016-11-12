import uuid

from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf	import csrf_exempt
from django.utils import timezone

from .models import job


def index(request):
    return HttpResponse("Placeholder")


###################################################
@csrf_exempt
def addjob(request):
    
    post	= request.POST
    j_uuid	= post['uuid']
    
    j = job(
        uuid		= j_uuid,
        stage		= post['stage'],
        priority	= post['priority'],
        state		= post['state'],
        ts_def		= post['ts'],
    )

    j.save()
    
    return HttpResponse("%s" % j_uuid )

###################################################
@csrf_exempt
def set(request):
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

    post	= request.POST
    j_uuid	= post['uuid']
    
    try:
        j = job.objects.get(uuid=j_uuid)
    except:
        return HttpResponse("%s not found" % j_uuid )

    j.delete()
    return HttpResponse("%s deleted" % j_uuid )

###################################################
def add():
    ts_def	= timezone.now()
    j_uuid	= uuid.uuid1()

    j = job(state='defined', uuid=j_uuid, stage='testing!', ts_def=ts_def)
    j.save()
    return j_uuid
    
###################################################
def detail(request):
    job_id = request.GET.get('job','')
    latest = request.GET.get('latest','')
    if(latest!=''):
        add()
        j = job.objects.latest(latest)
        return HttpResponse("Job %s" % j.uuid)

    if(job_id == ''):
        return HttpResponse("Job not specified.")
    print(job_id)
    ts = job.objects.get(id=job_id).ts_def
    print(ts)
    return HttpResponse("You're looking at job %s." % job_id)
