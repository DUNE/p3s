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

import logging

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



# Get an instance of a logger
logger = logging.getLogger('pilots')


# See Footnote 0

#########################################################
########## PART 1: REGISTRATION, DELETION ###############
#########################################################
@csrf_exempt
def register(request):
    
    post	= request.POST
    p_uuid	= post['uuid']
    t0		= timezone.now()

    p = pilot(
        state		= post['state'],
        site		= post['site'],
        host		= post['host'],
        uuid		= p_uuid,
        ts_cre		= post['ts'],
        ts_reg		= t0,
        ts_lhb		= t0,
        pid		= post['pid']
    )

    p.save()

    logger.info('pilot %s registered', p_uuid)

    # COMMENT/UNCOMMENT FOR TESTING ERROR CONDITIONS:
    # return HttpResponse(json.dumps({'status':'FAIL', 'state': 'failreg', 'error':'failed registration'}))
    
    return HttpResponse(json.dumps({'status':'OK', 'state':'active'}))

###################################################
@csrf_exempt
def delete(request):
    post	= request.POST
    p_uuid	= post['uuid']

    if(p_uuid=='ALL'):
        try:
            p = pilot.objects.all().delete()
        except:
            return HttpResponse("DELETE ALL: FAILED")

        return HttpResponse("DELETE ALL: SUCCESS")

    try:
        p = pilot.objects.get(uuid=p_uuid)
    except:
        return HttpResponse("%s not found" % p_uuid )

    p.delete()
    return HttpResponse("%s deleted" % p_uuid )

#########################################################
########## PART 2: JOB MANAGEMENT         ###############
#########################################################
@csrf_exempt
@transaction.atomic
def kill(request): # Pilot's request for a job:
    post	= request.POST

    kwargs = None

    try:
        kwargs	= {'uuid':post['uuid'],}
    except:
        pass

    try:
        kwargs	= {'host':post['host']}
    except:
        pass

    try:
        kwargs	= {'site':post['site'],}
    except:
        pass


    pilots = None
    plist = []

    try:
        pilots = pilot.objects.filter(**kwargs).exclude(state='stopped')
    except:
        return HttpResponse(json.dumps({'status':'FAIL', 'state': 'failkill', 'error':'pilot not found'}))

    try:
        with transaction.atomic():
            for p in pilots:
                p.state		= 'stopped'
                p.status	= 'KILL'
                p.save()
                plist.append(p.uuid)
            pids = ",".join(plist)
            return HttpResponse(json.dumps({'uuid':pids, 'state':'KILL'}))
    except:
        return HttpResponse(json.dumps({'status':'FAIL', 'state': 'failkill', 'error':'DB error'}))

#-----
@csrf_exempt
@transaction.atomic
def request(request): # Pilot's request for a job:
    post	= request.POST
    p_uuid	= post['uuid']

    p = None
    try:
        p = pilot.objects.get(uuid=p_uuid)
    except:
        return HttpResponse(json.dumps({'status':'FAIL', 'state': 'failbro', 'error':'pilot not found'}))

    # COMMENT/UNCOMMENT FOR TESTING ERROR CONDITIONS: (will bail here)
    # return HttpResponse(json.dumps({'status':'FAIL', 'state': 'failbro', 'error':'failed brokerage'}))


    if(p.status=='KILL'): return HttpResponse(json.dumps({'status':'KILL', 'state':'killed'}))

    ordering = 'ts_def'			# Please see Footnote (1)
    priolist = (10,9,8,7,6,5,4,3,2,1,0)	# Please see Footnote (2)
    
    j = None # placeholder for the job

    logger.info('pilot %s request', p_uuid)
    
    for prio in priolist:
        try:
            with transaction.atomic():
                tjs = job.objects.filter(priority=prio, state='defined') # save for later - .order_by(ordering)
                if(len(tjs)==0): continue
                
                ###  FOUND A JOB
                j_candidate = tjs[0]

                logger.info('pilot %s, candidate %s', p_uuid, j_candidate.uuid)

                j = job.objects.get(uuid=j_candidate.uuid)
                
                logger.info('%s selected', j.uuid)
                j.state		= 'dispatched'
                j.site		= p.site
                j.host		= p.host
                j.p_uuid	= p_uuid
                j.ts_dis	= timezone.now()
                j.save()
            
        except:
            p.state	= 'DB lock'
            p.status	= 'OK'
            p.ts_lhb	= timezone.now()
            p.save()
            return HttpResponse(json.dumps({'status': p.status, 'state': p.state}))

        p.j_uuid	= j.uuid
        p.state	= 'dispatched'
        p.ts_lhb	= timezone.now()
        p.save()
            
        to_pilot = {'status':	'OK', # job information in JSON format
                    'state':	'dispatched',	'job':	j.uuid,
                    'payload':	j.payload,	'env':	j.env}
        j = None # reset for next iteration
        return HttpResponse(json.dumps(to_pilot))

    if(j==None):
        p.state		= 'no jobs'
        p.status	= 'OK'
        p.ts_lhb	= timezone.now()

        tDiff = p.ts_lhb - p.ts_cre
        logger.info('tDiff %s', str(tDiff.total_seconds()))

        with transaction.atomic():
            p.save()
        return HttpResponse(json.dumps({'status': p.status, 'state': p.state}))

#########################################################
@csrf_exempt
def report(request):
    
    post	= request.POST
    p_uuid	= post['uuid']
    p		= pilot.objects.get(uuid=p_uuid)
    
    # Check if this pilot timed out (based on heartbeat)
    if(p.state=='timeout'):
        return HttpResponse(json.dumps({'status':	'FAIL',
                                        'state':	p.state,
                                        'error':	'timeout'}))

    
    state	= post['state']
    event	= post['event']
    jobcount	= post['jobcount']
    jpid	= post['jpid']
    errcode	= post['errcode']
    
    p.state	= state
    p.ts_lhb	= timezone.now()
    p.jobcount	= jobcount
    p.jpid	= jpid

    if(state in 'active','stopped'):
        p.status = 'OK'
        with transaction.atomic():
            p.save()
    
    if(state in ('running','finished')):
        p.status = 'OK' # reconfirm the status of the pilot
        try:
            j = job.objects.get(uuid=p.j_uuid)
            j.state = state # that's where the job has its state set in normal running
            j.pid	= jpid
            # print('--------------', j.pid, j.state)
            with transaction.atomic():
                j.save()
            
            if(event=='jobstart'):
                j.ts_sta= timezone.now()
                j.state = state
                with transaction.atomic():
                    j.save()
                if(j.wfuuid!=''):
                    wf = workflow.objects.get(uuid=j.wfuuid)
                    if(wf.state!='running'):
                        wf.ts_sta = timezone.now() #since noop does not really execute: if(wf.rootuuid==j.uuid):
                        wf.state = "running"
                        with transaction.atomic():
                            wf.save()

            if(event=='jobstop'): # timestamp and toggle children
                doneJobs = p.jobs_done
                if(doneJobs==''):
                    doneJobs = j.uuid
                else:
                    doneJobs+=','+j.uuid

                p.jobs_done = doneJobs
                
                j.ts_sto = timezone.now()
                j.errcode= errcode
                nd = manager.childrenStateToggle(j,'defined')
                with transaction.atomic():
                    j.save()
                
                if(j.wfuuid!=''): # Check the workflow - maybe it has completed
                    done	= True
                    jobsWF	= job.objects.filter(wfuuid=j.wfuuid)
                    for q in jobsWF:
                        if(q.state!='finished'): done = False

                    wf = workflow.objects.get(uuid=j.wfuuid)
                    wf.ndone = wf.ndone + nd + 1
                    if done:
                        wf.ts_sto = timezone.now()
                        wf.state = "finished"
                        
                    with transaction.atomic():
                        wf.save()
        except:
            return HttpResponse(json.dumps({'status':	'FAIL',
                                            'state':	state,
                                            'error':	'failed to update job state'}))

        with transaction.atomic():
            p.save()

    # FIXME bring to top to simplify logic for normal cases
    # FIXME incorrect return message for failure reports
    if(state in ('exception','nonstarter')): # FIXME add WF state
        p.status	= 'FAIL'
        with transaction.atomic():
            p.save()
        j = job.objects.get(uuid=p.j_uuid)
        j.state	= state
        if(event=='exception'):	j.ts_sto = timezone.now()
        with transaction.atomic():
            j.save()
            
        return HttpResponse(json.dumps({'status':'FAIL', 'state':state}))
        
    # COMMENT/UNCOMMENT FOR TESTING ERROR CONDITIONS:
    # return HttpResponse(json.dumps({'status':'FAIL', 'state': 'failreg', 'error':'failed registration'}))


    return HttpResponse(json.dumps({'status':'OK', 'state':state}))


########################  FOOTNOTES ##################################
#
# 0
#----
# pilot status can only take two values, 'OK' or 'FAIL' #
# while it's state can be more complex. This helps      #
# reflect different failure modes                       #


#
# 1
#----
# this could contain the name of the column by
# which to sort within same tier of priority, for example "ts_def".
# So it has to be consistent with the models. Look for "ordering" in the code.
#
# DB-based value, example:
# ordering = prioritypolicy.objects.get(name='order-within-priority').value
# For dev purposes, fixed value (to avoid missing values after fresh install):


    # try:
    #     ordering = 'ts_def' # FIXME - HARDCODED FOR TESTING
        
    # except: # catches error in fetching policy from DB, irrelevant if hardcoded
    #     p.state		= 'failed brokerage'
    #     p.status	= 'FAIL'
    #     p.ts_lhb	= timezone.now()
    #     with transaction.atomic():
    #         p.save()
    #     return HttpResponse(json.dumps({'status':'FAIL', 'state': p.state, 'error':'missing policy'}))

#
# 2
#----
    # # look at existing jobs priorities: FIXME - prohibitively expensive, need to change to async list
    # try:
    #     jp = job.objects.values('priority').distinct()
    #     for item in jp: priolist.append(item['priority'])
    # except: 	# return HttpResponse(json.dumps({'status':'OK', 'state': 'no jobs'}))
    #     pass	# let it bail below
    
    # j = None # placeholder for the job
    
    # priolist.sort(reverse=True) #  print(priolist)


    # for prio in priolist:
    #     try:
    #         tjs = job.objects.filter(priority=prio, state='defined').order_by(ordering)
    #         j = tjs[0]
    #         break
    #     except:
    #         pass


#
# 3
#----
# This has to do with locking the job object for update, unused for now:
    # j = job.objects.select_for_update().get(uuid=j_candidate.uuid) # print('~',j)
    #if(j.state!='defined'):
    #    j = None
    #    continue


    
################# DUSTY ATTIC ###########################
#    data = serializers.serialize('json', [ j, ])
#    return HttpResponse(data, mimetype='application/json')
