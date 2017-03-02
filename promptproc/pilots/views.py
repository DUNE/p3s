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
from django.views.decorators.csrf import csrf_exempt

from django.shortcuts	import render
from django.http	import HttpResponse
from django.utils	import timezone
from django.core	import serializers
from django.conf	import settings
from django.db		import transaction


# Local models
from .models		import pilot
from jobs.models	import job, prioritypolicy
from workflows.models	import workflow
from logic.models	import manager


#########################################################
# pilot status can only take two values, 'OK' or 'FAIL' #
# while it's state can be more complex. This helps      #
# reflect different failure modes                       #
#########################################################



#########################################################
########## PART 1: REGISTRATION, DELETION ###############
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

    with transaction.atomic():
        p.save()

    # COMMENT/UNCOMMENT FOR TESTING ERROR CONDITIONS:
    # return HttpResponse(json.dumps({'status':'FAIL', 'state': 'failreg', 'error':'failed registration'}))
    
    return HttpResponse(json.dumps({'status':'OK', 'state':'active'}))

###################################################
@csrf_exempt
def delete(request):
    post	= request.POST
    p_uuid	= post['uuid']

    try:
        p = pilot.objects.get(uuid=p_uuid)
    except:
        return HttpResponse("%s not found" % p_uuid )

    p.delete()
    return HttpResponse("%s deleted" % p_uuid )

###################################################
def deleteall(request):# SHOULD ONLY BE USED BY EXPERTS, do not advertise
    try:
        p = pilot.objects.all().delete()
    except:
        return HttpResponse("DELETE ALL: FAILED")

    return HttpResponse("DELETE ALL: SUCCESS")




#########################################################
########## PART 2: JOB MANAGEMENT         ###############
#########################################################
def request(request): # Pilot's request for a job:

    p_uuid	= request.GET.get('uuid','')
    p = pilot.objects.get(uuid=p_uuid) # FIXME - handle unlikely error

    # COMMENT/UNCOMMENT FOR TESTING ERROR CONDITIONS: (will bail here)
    # return HttpResponse(json.dumps({'status':'FAIL', 'state': 'failbro', 'error':'failed brokerage'}))

    ordering = None
    priolist = []

    try:
        # Footnote (1)
        ordering = 'ts_def' # FIXME - HARDCODED FOR TESTING
        
    except: # catches error in fetching policy from DB, irrelevant if hardcoded
        p.state		= 'failed brokerage'
        p.status	= 'FAIL'
        p.ts_lhb	= timezone.now()
        with transaction.atomic():
            p.save()
        return HttpResponse(json.dumps({'status':'FAIL', 'state': p.state, 'error':'missing policy'}))

    # look at existing jobs priorities: FIXME - prohibitively expensice, need to change to async list
    try:
        jp = job.objects.values('priority').distinct()
        for item in jp: priolist.append(item['priority'])
    except: 	# return HttpResponse(json.dumps({'status':'OK', 'state': 'no jobs'}))
        pass	# let it bail below
    
    j = None # placeholder for the job
    
    priolist.sort(reverse=True) #  print(priolist)
    for prio in priolist:
        try:
            tjs = job.objects.filter(priority=prio, state='defined').order_by(ordering)
            j = tjs[0]
            break
        except:
            pass

    if(j==None):
        p.state		= 'no jobs'
        p.status	= 'OK'
        p.ts_lhb	= timezone.now()
        with transaction.atomic():
            p.save()
        return HttpResponse(json.dumps({'status': p.status, 'state': p.state}))

    ########  FOUND A JOB #########
    j.state	= 'dispatched'
    j.p_uuid	= p_uuid
    j.ts_dis	= timezone.now()
    with transaction.atomic():
        j.save()
    
    p.j_uuid	= j.uuid
    p.state	= 'dispatched'
    p.ts_lhb	= timezone.now()
    with transaction.atomic():
        p.save()

    # job information going back to the pilot in JSON format
    to_pilot = {'status':	'OK',
                'state':	'dispatched',
                'job':		j.uuid,
                'payload':	j.payload,
                'env':		j.env}
    
    return HttpResponse(json.dumps(to_pilot))

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
        p.status = 'OK'
        with transaction.atomic():
            p.save()
    
    if(state in ('running','finished')):
        p.status = 'OK' # reconfirm the status of the pilot
        with transaction.atomic():
            p.save()

        try:
            j = job.objects.get(uuid=p.j_uuid)
            j.state = state # that's where the job has its state set in normal running
            
            if(event=='jobstart'):
                j.ts_sta = timezone.now()
                with transaction.atomic():
                    j.save()
                if(j.wfuuid!=''):
                    wf = workflow.objects.get(uuid=j.wfuuid)
                    wf.state = "running"
                    with transaction.atomic():
                        wf.save()

            if(event=='jobstop'): # timestamp and toggle children
                j.ts_sto = timezone.now()
                manager.childrenStateToggle(j,'defined') # j.childrenStateToggle('defined')
                with transaction.atomic():
                    j.save()
                
                # Check the workflow (maybe it is completed)
                if(j.wfuuid!=''):
                    done	= True
                    jobsWF	= job.objects.filter(wfuuid=j.wfuuid)
                    for q in jobsWF:
                        if(q.state!='finished'): done = False

                    wf = workflow.objects.get(uuid=j.wfuuid)
                    if done: wf.state = "finished"
                    with transaction.atomic():
                        wf.save()
        except:
            return HttpResponse(json.dumps({'status':	'FAIL',
                                            'state':	state,
                                            'error':	'failed to update job state'}))

    # FIXME bring to top to simplify logic for normal cases
    # FIXME incorrect return message for failure reports
    if(state=='exception'): # FIXME add WF state
        p.status	= 'FAIL'
        with transaction.atomic():
            p.save()
        j = job.objects.get(uuid=p.j_uuid)
        j.state	= state
        if(event=='exception'):	j.ts_sto = timezone.now()
        with transaction.atomic():
            j.save()
        
    # COMMENT/UNCOMMENT FOR TESTING ERROR CONDITIONS:
    # return HttpResponse(json.dumps({'status':'FAIL', 'state': 'failreg', 'error':'failed registration'}))


    # this should work as a catch-all since all states are supposed to be picked up above
    #
    return HttpResponse(json.dumps({'status':'OK', 'state':state}))


########################  FOOTNOTES ##################################
# 1
# WORK IN PROGRESS:
# this could contain the name of the column by
# which to sort within same tier of priority, for example "ts_def".
# So it has to be consistent with the models. Look for "ordering" in the code.
#
# DB-based value, example:
# ordering = prioritypolicy.objects.get(name='order-within-priority').value
# For dev purposes, fixed value (to avoid missing values after fresh install):
################# DUSTY ATTIC ###########################
#    data = serializers.serialize('json', [ j, ])
#    return HttpResponse(data, mimetype='application/json')
