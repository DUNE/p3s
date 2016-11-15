from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone

#from .models import job


def index(request):
    domain = request.get_host()
    print(domain)
    return render(request, 'index.html',
                  {
                      'domain':	domain,
                      'time':	str(timezone.now())
                  }
    )

#    return HttpResponse("Prompt Processing Information System")
