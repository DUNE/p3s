import django.db.models
from django.db.models	import Max

from django.shortcuts	import render
from django.http	import HttpResponse
from django.views.decorators.csrf import csrf_exempt

# from . import models
from .models import pur

#########################################################    
@csrf_exempt
def indpurity(request):
    maxnum = 0

    try:
#        o = pur.objects.all()
#        maxnum = len(o)
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

        try:
            p = pur.objects.get(pk=p_pk)
            p.delete()
            return HttpResponse("Entry %s deleted" % p_pk )
        except:
            return HttpResponse("Entry %s not found or deletion failed" % p_pk )

    if(run):
        try:
            p = pur.objects.filter(run=run)
            if(p is None or len(p)==0): raise
            p.delete()
            return HttpResponse("Run %s deleted" % run )
        except:
            return HttpResponse("Run %s not found or deletion failed" % run )

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

    p.save()

    
    return HttpResponse('Adding run '+p.run)

#    return HttpResponse('Delete request:'+str(p_pk))
#    maxnum = pur.objects.latest('id').id


        
