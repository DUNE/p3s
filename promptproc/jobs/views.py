from django.shortcuts import render
from django.http import HttpResponse

from .models import job


def index(request):
    return HttpResponse("Hello, world.")

def detail(request, job_id):
    ts = job.objects.get(id=job_id).ts_def
    print(ts)
    return HttpResponse("You're looking at job %s." % job_id)
