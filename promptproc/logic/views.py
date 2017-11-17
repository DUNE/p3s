#########################################################
#                 LOGIC VIEW                            #
# UTILITY FUNCTIONS FOR SERVER MAINTENANCE, E.G.        #
# KEEPING TRACKS OF TIME-OUTS ETC                       #
#########################################################

import logging

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
from utils.miscUtils import parseCommaDash

from .models import service


# Get an instance of a logger
logger = logging.getLogger('logic')



###################################################
@csrf_exempt
def purge(request):
    post	= request.POST
    
    # interval	= post['interval'] # measured in seconds
    state	= post['state']
    what	= post['what']

    # cutoff = timezone.now() - timedelta(seconds=interval)# prior use: dt(interval) 

    logger.info('purge request for %s, state %s', what, state)
    
    timestamp = None
    selection = None
    nDeleted  = 0

    if(what=='pilot'):
        timestamp='ts_lhb'

    # kwargs = {'{0}__{1}'.format(timestamp, 'lte'): str(cutoff),}

    obj = eval(what)
    #    selection = obj.objects.filter(**kwargs)
    selection = obj.objects.filter(state=state)

    if selection:
        # if(state and state!=''): selection = selection.filter(state=state)
        nDeleted = len(selection) # for o in selection: print(o.uuid)
        selection.delete()
    
    return HttpResponse(str(nDeleted))

###################################################
@csrf_exempt
def pilotTO(request):

    post	= request.POST
    TO		= int(post['to']) # time out, meausured in seconds
    host	= post['host']
    
    cutoff = timezone.now() - timedelta(seconds=TO)

    logger.info('pilotTO request received from %s', host)

    # select the timed-out pilots
    selection = pilot.objects.filter(ts_lhb__lte=cutoff).exclude(state='stopped').exclude(state='timeout')

    tLife = []
    nTO = len(selection)
    for p in selection:
        # print('TO pilot:', p.uuid, 'TO pilot job:', p.j_uuid)

        td = p.ts_lhb - p.ts_cre
        tLife.append(p.extra+'/'+str(td.total_seconds()).split('.')[0])

        #### FIXME - Improve the update of the state of wf and job
        try:
            j = job.objects.filter(uuid=p.j_uuid)
            j.update(state='pilotTO', ts_sto=timezone.now())
            if(j.wfuuid!=''):
                try:
                    wf = workflow.objects.get(uuid=j.wfuuid)
                    wf.state = "pilotTO"

                    j = job.objects.filter(wfuuid=wf.uuid)
                    j.update(state='pilotTO', ts_sto=timezone.now())
                except:
                    pass

        except:
            pass

    selection.update(state='timeout', status='TO')

    if(len(tLife)==0): return HttpResponse('')
    retMessage = 'Number of TO pilots: '+str(nTO)+'\n'
    for t in tLife:
        retMessage+=t+'\n'

    return HttpResponse(retMessage, content_type="text/plain")

###################################################
@csrf_exempt
def serviceReport(request):
    
    post	= request.POST

    message	= post.get('message', '')
    name	= post.get('name', '')

    
    t0		= timezone.now()
    print(name, message, t0)

    if(message==''):
        return HttpResponse("empty message")

    s = service(name=name, ts=t0, info=message)
    print(s)
    s.save()

    return HttpResponse("OK")

###################################################
@csrf_exempt
def serviceDelete(request):
    
    post	= request.POST
    s_pk	= post.get('pk', None)

    if(s_pk is None): return HttpResponse("No key for deletion")

    if(s_pk=='ALL'):
        try:
            service.objects.all().delete()
            return HttpResponse("Deleted all service entries")
        except:
            return HttpResponse("Deletion of all service entries failed")

    pklist = parseCommaDash(s_pk)
    pdeleted = []
    for pk in pklist:
        try:
            s = service.objects.get(pk=pk)
            s.delete()
            pdeleted.append(pk)
        except:
            pass
            
    return HttpResponse("Entries %s deleted" % pdeleted )


