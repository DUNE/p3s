
# python utiility classes
import uuid
import datetime
from datetime				import timedelta

# core django
from django.shortcuts			import render
from django.utils			import timezone
from django.utils.timezone		import utc
from django.utils.timezone		import activate

from django.http			import HttpResponse
from django.http			import HttpResponseRedirect

from django.views.decorators.csrf	import csrf_exempt
from django.core			import serializers
from django.utils.safestring		import mark_safe
from django.forms.models		import model_to_dict
from django.conf			import settings

# Models used in the application:
from jobs.models			import job
from data.models			import dataset, datatype
from pilots.models			import pilot
from workflows.models			import dag, dagVertex, dagEdge
from workflows.models			import workflow

# tables2 machinery
import	django_tables2 as tables
from	django_tables2			import RequestConfig
from	django_tables2.utils		import A

from utils.timeUtils import dt

###################################################
@csrf_exempt
def purge(request):
    post	= request.POST
    
    interval	= post['interval']
    timestamp	= post['timestamp'] # print(interval, timestamp)
    state	= post['state']
    what	= post['what']

    cutoff = timezone.now() - dt(interval) #  print(str(timezone.now()), cutoff)

    selection = None
    nDeleted  = 0

    kwargs = {'{0}__{1}'.format(timestamp, 'lte'): str(cutoff),}

    obj = eval(what)
    selection = obj.objects.filter(**kwargs)

    if selection:
        if(state and state!=''): selection = selection.filter(state=state)
        nDeleted = len(selection) # for o in selection: print(o.uuid)
        selection.delete()
    
    return HttpResponse(str(nDeleted))

###################################################
def pilotTO(request):
    cutoff = timezone.now() - timedelta(minutes=2) #  improve later
    selection = pilot.objects.filter(ts_lhb__lte=cutoff).exclude(state='stopped')
    selection.update(state='timeout', status='FAIL')
    nTO = len(selection)
    return HttpResponse(str(nTO))
#### FIXME - state of wf and job needs to be updated
####    cutoff = timezone.now() - timedelta(seconds=5) #  for testing
