import django.db.models
from django.db.models	import Max

from django.shortcuts	import render
from django.http	import HttpResponse
from django.views.decorators.csrf import csrf_exempt

# from . import models
# from .models import pur

from utils.miscUtils import parseCommaDash

# count how many distinct runs there were
@csrf_exempt
def evdisp(request):
    
    return HttpResponse("test")

