import django.db.models
from django.db.models	import Max

from django.shortcuts	import render
from django.http	import HttpResponse
from django.views.decorators.csrf import csrf_exempt

# from . import models
from .models import pur



#########################################################    
def parseCommaDash(inp):
    outlist = []
    if('-' in inp):
        left_right = inp.split('-')
        for x in range(int(left_right[0]), int(left_right[1])+1):
            outlist.append(x)
    elif(',' in inp):
        outlist=inp.split(',')
    else:
        outlist.append(int(inp))
        
    return outlist
#########################################################    
@csrf_exempt
def indpurity(request):
    maxnum = 0

    try:
        maxdict = pur.objects.all().aggregate(Max('run'))
        maxnum = maxdict['run__max'] + 1
    except:
        pass
    
    return HttpResponse(str(maxnum))

###################################################
@csrf_exempt
def delpurity(request):
    post	= request.POST
    p_pk	= None
    run		= None

    try:
        p_pk = post['pk']
    except:
        try:
            run = post['run']
        except:
            return HttpResponse("Missing key(s) for deletion")

   
    p = None
    if(p_pk):
        if(p_pk=='ALL'):
            try:
                pur.objects.all().delete()
                return HttpResponse("Deleted all purity entries")
            except:
                return HttpResponse("Deletion of all purity entries failed")

        pklist = parseCommaDash(p_pk)
        pdeleted = []
        for pk in pklist:
            try:
                p = pur.objects.get(pk=pk)
                p.delete()
                pdeleted.append(pk)
            except:
                pass
                #return HttpResponse("Entry %s not found or deletion failed" % pk )
            
        return HttpResponse("Entries %s deleted" % pdeleted )

    if(run):
        runlist = parseCommaDash(run)
        rdeleted = []
        for r in runlist:
            print('run', r)
            try:
                p = pur.objects.filter(run=r)
                if(p is None or len(p)==0):
                    pass
                else:
                    p.delete()
                    rdeleted.append(r)
            except:
                pass

        return HttpResponse("Runs deleted: %s" % rdeleted )
#########################################################    
@csrf_exempt
def addpurity(request):
    post	= request.POST

    print()
    p=pur()
    p.run	= post['run']
    p.tpc	= post['tpc']
    p.lifetime	= post['lifetime']
    p.error	= post['error']
    p.count	= post['count']
    p.ts	= post['ts']
    
    
    p.save()

    
    return HttpResponse('Adding run '+p.run+' time:'+p.ts)

#    return HttpResponse('Delete request:'+str(p_pk))
#    maxnum = pur.objects.latest('id').id


        
