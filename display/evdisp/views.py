import django.db.models
from django.db.models	import Max

from django.shortcuts	import render
from django.http	import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import evdisp

from utils.miscUtils import parseCommaDash

import json

#########################################################    
def test(request):
    
    return HttpResponse("test")

#########################################################    
# count how many distinct runs there were
@csrf_exempt
def maxrun(request):
    maxnum = 0

    try:
        maxdict = evdisp.objects.all().aggregate(Max('run'))
        maxnum = maxdict['run__max'] + 1
    except:
        pass
    
    return HttpResponse(str(maxnum))

###################################################
# deletes either individual evdisp entry by key,
# or all entries
@csrf_exempt
def delete(request):
    post	= request.POST

    evd_pk	= post.get('pk','')
    run		= post.get('run','')
    j_uuid	= post.get('j_uuid','')
    
    if(evd_pk=='' and run=='' and j_uuid==''):
        return HttpResponse("Missing key(s) for deletion")

   
    if(evd_pk!=''):
        if(evd_pk=='ALL'):
            try:
                evdisp.objects.all().delete()
                return HttpResponse("Deleted all evdisp entries")
            except:
                return HttpResponse("Deletion of all evdisp entries failed")

        evdlist = parseCommaDash(evd_pk)
        e_deleted = []
        for pk in evdlist:
            try:
                evd = evdisp.objects.get(pk=pk)
                evd.delete()
                e_deleted.append(pk)
            except:
                pass
                #return HttpResponse("Entry %s not found or deletion failed" % pk )
            
        return HttpResponse("Entries %s deleted" % e_deleted )

    if(run!=''):
        runlist = parseCommaDash(run)
        rdeleted = []
        for r in runlist:
            try:
                p = evdisp.objects.filter(run=r)
                if(p is None or len(p)==0):
                    pass
                else:
                    p.delete()
                    rdeleted.append(r)
            except:
                pass

        return HttpResponse("Runs deleted: %s" % rdeleted )
    
    if(j_uuid!=''):
        evds = None
        try:
            evds = evdisp.objects.filter(j_uuid=j_uuid)
        except:
            pass
        
        if(evds is None or len(evds)==0):
            return HttpResponse("Displays for job %s: delete failed" % j_uuid )
        else:
            evds.delete()
            return HttpResponse("Displays for job %s deleted" % j_uuid )

#########################################################    
@csrf_exempt
def add(request):
    post	= request.POST
    json_data	= post.get('json', '')

    data = json.loads(json_data)
    print(data)

    for d in data:
        e=evdisp()
        for k in d.keys(): e.__dict__[k]=d[k]
        e.save()
        
    return HttpResponse('Adding evdisp')
