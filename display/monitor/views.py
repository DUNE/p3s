import django.db.models
from django.db.models	import Max

from django.shortcuts	import render
from django.http	import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import  django_tables2 as tables
from	django_tables2			import RequestConfig
from	django_tables2.utils		import A

from purity.models import pur

from django import forms

class EvdispForm(forms.Form):
    run		= forms.CharField(required=False, initial='')
    event	= forms.CharField(required=False, initial='')
    

#########################################################    
class MonitorTable(tables.Table):
    def set_site(self, site=''):
        self.site=site

    def makelink(self, what, key, value):
        return mark_safe('<a href="http://%s%s?%s=%s">%s</a>'
                         % (self.site, reverse(what), key, value, value))

    def renderDateTime(self, dt): # common format defined here.
        return timezone.localtime(dt).strftime(settings.TIMEFORMAT)

#########################################################    
   
class PurityTable(MonitorTable):
    run		= tables.Column(verbose_name='Run')
    tpc		= tables.Column(verbose_name='TPC')
    lifetime	= tables.Column(verbose_name='LifeTime')
    error	= tables.Column(verbose_name='Error')
    count	= tables.Column(verbose_name='Count')
    
    class Meta:
        model = pur
        attrs = {'class': 'paleblue'}


#########################################################    
# general request handler for summary type of a table
def data_handler(request, what):
    domain	= request.get_host()

    # testing only
    objs = pur.objects.order_by('-pk').all()

    d = {}
    
    t = PurityTable(objs)
    t.set_site(domain)
    RequestConfig(request).configure(t)

    d['table']	= t
    d['N']	= str(len(objs))
    d['domain']	= domain
    
    d['pageName']	= ': Purity Monitor'
    
    return render(request, 'unitable.html', d)

#########################################################    
# general request handler for summary type of a table
def data_handler2(request, what):
    domain	= request.get_host()

    forChart = pur.objects.order_by('-pk').filter(tpc=10)

    purStr=''
    for i in range(100):
        try:
            purStr += ("[[%s], %s],") % (forChart[i].ts.strftime("%H, %M, %S"), forChart[i].lifetime)
        except:
            break
            
    d = {}
    
    objs = pur.objects.order_by('-pk').all()
    t = PurityTable(objs)
    t.set_site(domain)
    RequestConfig(request).configure(t)

    d['table']	= t
    d['N']	= str(len(objs))
    d['domain']	= domain
    
    d['pageName']	= ': Purity Monitor'
    d['val']		= purStr
    
    
    return render(request, 'unitable2.html', d)


#########################################################    
@csrf_exempt
def evdisp(request):
#    if request.method == 'POST':
#        f = EvdispForm(request.POST)
#        return("!")
    
    domain	= request.get_host()
    run		= request.GET.get('run','')
    event	= request.GET.get('event','')


    d = {}

    d['display'] = (event!='' and run!='')
    d['chList'] = ('0-2559','2560-5119','5120-7679','7680-10239','10240-12799','12800-15359')

    d['domain']		= domain
    d['evdispURL']	= 'evdisp'
    d['run']		= run
    d['event']		= event
    
    d['pageName']	= ': Event Display'


    f = EvdispForm({'run':run, 'event':event})

    
    d['form'] = f.as_table()
    
    return render(request, 'evdisp.html', d)

