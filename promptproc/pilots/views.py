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

    # COMMENT/UNCOMMENT FOR TESTING ERROR CONDITIONS:
    # return HttpResponse(json.dumps({'status':'FAIL', 'state': 'failbro', 'error':'failed brokerage'}))

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

    if(j==None): return HttpResponse(json.dumps({'status':'OK', 'state': 'waiting'}))

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

#########################################################
@csrf_exempt
def register(request):
    
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

    # COMMENT/UNCOMMENT FOR TESTING ERROR CONDITIONS:
    # return HttpResponse(json.dumps({'status':'FAIL', 'state': 'failreg', 'error':'failed registration'}))
    
    return HttpResponse(json.dumps({'status':'OK', 'state':'active'}))

#########################################################
@csrf_exempt
def report(request):
    
    post	= request.POST
    p_uuid	= post['uuid']
    state	= post['state']
    
    p		= pilot.objects.get(uuid=p_uuid)
    p.state	= state
    p.ts_lhb	= timezone.now()
    p.save()

    if(state in ('running','finished')):
        j = job.objects.get(uuid=p.j_uuid)
        j.state=state
        j.save()

    # COMMENT/UNCOMMENT FOR TESTING ERROR CONDITIONS:
    # return HttpResponse(json.dumps({'status':'FAIL', 'state': 'failreg', 'error':'failed registration'}))
    
    return HttpResponse(json.dumps({'status':'OK', 'state':state}))

###################################################
@csrf_exempt
def delete(request):
    # fixme - improve error handling such as for missing or screwy arguments

    post	= request.POST
    p_uuid	= post['uuid']
    print(p_uuid)
    try:
        p = pilot.objects.get(uuid=p_uuid)
    except:
        return HttpResponse("%s not found" % p_uuid )

    p.delete()
    return HttpResponse("%s deleted" % p_uuid )

###################################################
# SHOULD ONLY BE USED BY EXPRERTS, do not advertise
def deleteall(request):
    try:
        p = pilot.objects.all().delete()
    except:
        return HttpResponse("DELETE ALL: FAILED")

    return HttpResponse("DELETE ALL: SUCCESS")

################# DUSTY ATTIC ###########################
#    data = serializers.serialize('json', [ j, ])
#    return HttpResponse(data, mimetype='application/json')
