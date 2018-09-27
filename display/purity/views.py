import django.db.models
from django.utils	import timezone
from django.db.models	import Max
from django.conf			import settings

from django.shortcuts	import render
from django.http	import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import pur
from utils.miscUtils import parseCommaDash

#########################################################    
# count how many distinct runs there were
# this is mainly to generate serial numbers until we
# properly propagate the real run number

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
    p_pk	= post.get('pk','')
    run		= post.get('run','')
    infile	= post.get('infile','')


    if(p_pk=='' and run=='' and infile==''):
        return HttpResponse("Missing key(s) for deletion")

   
    p = None

    if(infile!=''):
        try:
            p = pur.objects.filter(infile=infile)
            p.delete()
        except:
            return HttpResponse("Entries for input file %s were not found or deletion failed" % infile )
            
        return HttpResponse("Entries for input file %s deleted" % infile )
    
    if(p_pk!=''):
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

    if(run!=''):
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
    
    p.run	= post.get('run',	0)
    p.tpc	= post.get('tpc',	0)
    p.lifetime	= post.get('lifetime',	0.0)
    p.error	= post.get('error',	0.0)
    p.count	= post.get('count',	0.0)
    p.ts	= post.get('ts',	timezone.now()) # p.ts	= post['ts']
    p.sn	= post.get('sn',	0.0)
    p.snclusters= post.get('snclusters',0)
    p.drifttime	= post.get('drifttime',	0.0)
    p.infile	= post.get('infile',	'')
    
    p.save()

    if settings.LIMITS['purity']['alarm']:
        if p.lifetime < settings.LIMITS['purity']['min']:
            print('Alarm!')

    
    return HttpResponse('Adding run '+p.run+' time:'+p.ts.strftime('%x %X'))

#    return HttpResponse('Delete request:'+str(p_pk))
#    maxnum = pur.objects.latest('id').id


        
