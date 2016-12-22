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
from .models				import pilot
from jobs.models			import job, prioritypolicy



#########################################################
# pilot status can only take two values, 'OK' or 'FAIL' #
# while it's state can be more complex. This helps      #
# reflect different failure modes                       #
#########################################################
#
# This is request for a job:
def request(request):
    p_uuid	= request.GET.get('uuid','')
    # Fetch the pilot! FIXME - need to pritect the followling line:
    p = pilot.objects.get(uuid=p_uuid)

    # COMMENT/UNCOMMENT FOR TESTING ERROR CONDITIONS: (will bail here)
    # return HttpResponse(json.dumps({'status':'FAIL', 'state': 'failbro', 'error':'failed brokerage'}))

    ordering = None
    priolist = []

    try:
        # this contains (for example) the name of the column by which to sort within same tier of priority,
        # for example "ts_def". So it has to be consistent with the models. Look for "ordering" in the code.
        # DB-based value, example:
        # ordering = prioritypolicy.objects.get(name='order-within-priority').value
        # For dev purposes, fixed value (to avoid missing values after fresh install):
        ordering = 'ts_def'
    except:
        p.state		= 'failed brokerage'
        p.status	= 'FAIL'
        p.ts_lhb	= timezone.now()
        p.save()
        return HttpResponse(json.dumps({'status':'FAIL', 'state': p.state, 'error':'missing policy'}))
    try:
        jp = job.objects.values('priority').distinct()
        for item in jp: priolist.append(item['priority'])
    except: 	# return HttpResponse(json.dumps({'status':'OK', 'state': 'no jobs'}))
        pass	# let it bail below
    
    j = None # placeholder for the job
    
    priolist.sort(reverse=True) #  print(priolist)
    for prio in priolist: # should skip is list is empty and so the job stays None
        # print('Trying prio:'+str(prio))
        try:
            tjs = job.objects.filter(priority=prio, state='defined').order_by(ordering)
            # print(tjs)
            j = tjs[0]
            break
        except:
            pass

    if(j==None):
        p.state		= 'no jobs'
        p.status	= 'OK'
        p.ts_lhb	= timezone.now()
        p.save()
        return HttpResponse(json.dumps({'status': p.status, 'state': p.state}))

    j.state	= 'dispatched'
    j.p_uuid	= p_uuid
    j.ts_dis	= timezone.now()
    j.save()
    
    p.j_uuid	= j.uuid
    p.state	= 'dispatched'
    p.ts_lhb	= timezone.now()
    p.save()

    # Will redo this later - the format of the job infor going back to the pilot:
    to_pilot = {'status':	'OK',
                'state':	'dispatched',
                'job':		j.uuid,
                'payload':	j.payload}
    
    return HttpResponse(json.dumps(to_pilot))

#########################################################
#
# The pilot attempts to register with the server:
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
    event	= post['event']
    jobcount	= post['jobcount']
    
    p		= pilot.objects.get(uuid=p_uuid)
    p.state	= state
    p.ts_lhb	= timezone.now()
    p.jobcount	= jobcount

    if(state in 'active','stopped'):
        p.status	= 'OK'
        p.save()
    
    if(state in ('running','finished')):
        p.status	= 'OK'
        p.save()
        try:
            j		= job.objects.get(uuid=p.j_uuid)
            j.state	= state
            if(event=='jobstart'):	j.ts_sta = timezone.now()
            if(event=='jobstop'):	j.ts_sto = timezone.now()
            j.save()
        except:
            return HttpResponse(json.dumps({'status':	'FAIL',
                                            'state':	state,
                                            'error':	'failed to update job state'}))
    if(state=='exception'):
        p.status	= 'FAIL'
        p.save()
        j = job.objects.get(uuid=p.j_uuid)
        j.state	= state
        if(event=='exception'):	j.ts_sto = timezone.now()
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
    # print(p_uuid)
    try:
        p = pilot.objects.get(uuid=p_uuid)
    except:
        return HttpResponse("%s not found" % p_uuid )

    p.delete()
    return HttpResponse("%s deleted" % p_uuid )

###################################################
# SHOULD ONLY BE USED BY EXPERTS, do not advertise
def deleteall(request):
    try:
        p = pilot.objects.all().delete()
    except:
        return HttpResponse("DELETE ALL: FAILED")

    return HttpResponse("DELETE ALL: SUCCESS")

################# DUSTY ATTIC ###########################
#    data = serializers.serialize('json', [ j, ])
#    return HttpResponse(data, mimetype='application/json')
