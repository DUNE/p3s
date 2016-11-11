import uuid

from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone

from .models import job


def index(request):
    return HttpResponse("Hello, world.")

def addjob(request):
    j_uuid = add()
    return HttpResponse(j_uuid)


def add():
    ts_def	= timezone.now()
    j_uuid	= uuid.uuid1()

    j = job(state='defined', uuid=j_uuid, stage='testing!', ts_def=ts_def)
    j.save()
    return j_uuid
    
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
