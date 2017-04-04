
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

###################################################
@csrf_exempt
def purge(request):
    post	= request.POST
    
    interval	= post['interval']
    timestamp	= post['timestamp']
    state	= post['state']

    # print(interval, timestamp)

    cutoff = timezone.now() - dt(interval) # print(cutoff)

    selection = None
    nDeleted  = 0
    
    if(timestamp=='ts_def'):
        jj = eval("job")
        selection = jj.filter(ts_def__lte=cutoff)
    if(timestamp=='ts_sto'):
        selection = job.objects.filter(ts_sto__lte=cutoff)
    else:
        pass

    if selection:
        if(state and state!=''):
            selection = selection.filter(state=state)
        print('objects:',len(selection))
        nDeleted = len(selection)
        for o in selection:
            print(o.uuid)
        selection.delete()
    
    return HttpResponse(str(nDeleted))
