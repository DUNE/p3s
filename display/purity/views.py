from django.utils			import timezone
import django.db.models
from django.db.models	import Max

from django.shortcuts	import render
from django.http	import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import pur

from utils.miscUtils import parseCommaDash

#########################################################    
# count how many distinct runs there were
@csrf_exempt
def index(request):
    maxnum = 0

    try:
        maxdict = pur.objects.all().aggregate(Max('run'))
        maxnum = maxdict['run__max'] + 1
    except:
        pass
    
    return HttpResponse(str(maxnum))

###################################################
# deletes either individual purity entry by key,
# or all entries
@csrf_exempt
def delete(request):
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
def add(request):
    post	= request.POST

    p=pur()
    p.run	= post['run']
    p.tpc	= post['tpc']
    p.lifetime	= post['lifetime']
    p.error	= post['error']
    p.count	= post['count']
    # p.ts	= post['ts']

    p.ts	= post.get('ts', timezone.now())
    
    # print('here')
    p.sn	= post.get('sn', 0.0)
    p.snclusters= post.get('snclusters',0)
    
    
    p.save()

    
    return HttpResponse('Adding run '+p.run+' time:'+p.ts.strftime('%x %X'))

#    return HttpResponse('Delete request:'+str(p_pk))
#    maxnum = pur.objects.latest('id').id


        
