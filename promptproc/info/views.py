import datetime

from django.shortcuts	import render
from django.http	import HttpResponse
from django.http	import HttpResponseRedirect
from django.utils	import timezone
from django.conf	import settings

# Provisional, for stats - don't forget to delete
# if this view is refactored:
from jobs.models			import job
from data.models			import dataset, datatype
from pilots.models			import pilot
from workflows.models			import dag, dagVertex, dagEdge
from workflows.models			import workflow
from monitor.monitorTables		import *



from utils.timeUtils import uptime
# TWEAK
from django import forms

class NameForm(forms.Form):
    FAVORITE_COLORS_CHOICES = (
    ('blue', 'Blue+'),
    ('green', 'Green+'),
    ('black', 'Black+'),
)
    
    favorite_colors = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=FAVORITE_COLORS_CHOICES,
    )
    
# END TWEAK

def index(request):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NameForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            print(form.cleaned_data)
            return HttpResponseRedirect('/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()
    
    domain	= request.get_host()
    hostname	= settings.HOSTNAME

    summaryData = []
    summaryData.append({'Object': 'Pilots',	'Number': 	pilot.N()})
    summaryData.append({'Object': 'Jobs',	'Number': 	job.N()})
    summaryData.append({'Object': 'Workflows',	'Number':	workflow.N()})
    summaryData.append({'Object': 'Datasets',	'Number':	dataset.N()})
    

    tSummary = SummaryTable(summaryData)

    timeString = datetime.datetime.now().strftime('%x %X')+' '+timezone.get_current_timezone_name()
    
    systemData = []
    systemData.append({'attribute': 'Current time',	'value': timeString})
    systemData.append({'attribute': 'Server',	'value': hostname})
    systemData.append({'attribute': 'Uptime',	'value': uptime()})
    systemData.append({'attribute': '>',	'value': '>'})

    
    tSystem = DetailTable(systemData)

    return render(request, 'index.html',
                  {
                      'domain':		domain,
                      'hostname':	hostname,
                      'uptime':		uptime(),
                      'time':		timeString,
                      'summary':	tSummary,
                      'system':		tSystem,
                      'form':		form,
                  }
    )
#
#
def test(request):
    return HttpResponse('test')
