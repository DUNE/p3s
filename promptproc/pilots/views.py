#########################################################
#                      PILOTS                           #
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
from .models				import pilot
from jobs.models			import job, prioritypolicy

#########################################################
def request(request):
    j = None
    p_uuid	= request.GET.get('uuid','')


    ordering = None
    priolist = []

    try:
        ordering = prioritypolicy.objects.get(name='order-within-priority').value
    except:
        return HttpResponse('no policy found for order-within-priority')
        
    try:
        jp = job.objects.values('priority').distinct()
        for item in jp: priolist.append(item['priority'])
    except:
        return HttpResponse('no policy found for order-within-priority')

    priolist.sort(reverse=True)
    print(priolist)
    for prio in priolist:
        print('Trying:'+str(prio))
        try:
            tjs = job.objects.filter(priority=prio, state='defined').order_by(ordering)
            print(tjs)
            j = tjs[0]
            break
        except:
            pass

    if(j==None): return HttpResponse('No matching jobs in defined state found')

    j.state	= 'dispatched'
    j.p_uuid	= p_uuid
    j.ts_dis	= timezone.now()
    j.save()
    
    p		= pilot.objects.get(uuid=p_uuid)
    p.j_uuid	= j.uuid
    p.state	= 'dispatched'
    p.ts_lhb	= timezone.now()
    p.save()
    
    return HttpResponse(json.dumps({'status':'OK', 'state':'dispatched', 'job':j.uuid}))

#    data = serializers.serialize('json', [ j, ])
#    return HttpResponse(data, mimetype='application/json')

#########################################################
@csrf_exempt
def addpilot(request):
    
    post	= request.POST
    p_uuid	= post['uuid']
    
    p = pilot(
        state		= post['state'],
        site		= post['site'],
        host		= post['host'],
        uuid		= p_uuid,
        ts_cre		= post['ts'],
        ts_reg		= timezone.now(),
        ts_lhb		= timezone.now()
    )

    p.save()

    return HttpResponse(json.dumps({'status':'OK', 'state':'active'}))


