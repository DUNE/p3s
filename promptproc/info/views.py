from django.shortcuts import render
from django.http import HttpResponse

#from .models import job


def index(request):
    return HttpResponse("Prompt Processing Information System")
