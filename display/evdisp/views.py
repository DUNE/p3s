import django.db.models
from django.db.models	import Max

from django.shortcuts	import render
from django.http	import HttpResponse
from django.views.decorators.csrf import csrf_exempt

# from . import models
# from .models import evdisp

from utils.miscUtils import parseCommaDash


#########################################################    
def test(request):
    
    return HttpResponse("test")

#########################################################    
# count how many distinct runs there were
@csrf_exempt
def ind(request):
    maxnum = 0

    try:
        maxdict = evdisp.objects.all().aggregate(Max('run'))
        maxnum = maxdict['run__max'] + 1
    except:
        pass
    
    return HttpResponse(str(maxnum))

#########################################################    
@csrf_exempt
def add(request):
    post	= request.POST

    
    return HttpResponse('Adding evdisp')
