import django.db.models
from django.db.models	import Max

from django.shortcuts	import render
from django.http	import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import  django_tables2 as tables
from	django_tables2			import RequestConfig
from	django_tables2.utils		import A

from purity.models import pur



class MonitorTable(tables.Table):
    def set_site(self, site=''):
        self.site=site

    def makelink(self, what, key, value):
        return mark_safe('<a href="http://%s%s?%s=%s">%s</a>'
                         % (self.site, reverse(what), key, value, value))

    def renderDateTime(self, dt): # common format defined here.
        return timezone.localtime(dt).strftime(settings.TIMEFORMAT)

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
    objs = pur.objects.all()

    d = {}
    
    t = PurityTable(objs)
    t.set_site(domain)
    RequestConfig(request).configure(t)

    d['table']	= t
    d['N']	= str(len(objs))
    d['domain']	= domain
    
    return render(request, 'unitable.html', d)


#########################################################    
@csrf_exempt
def evdisp(request):
    domain	= request.get_host()
    run		= request.GET.get('run','')
    event	= request.GET.get('event','')
    
    d = {}
    d['domain']		= domain
    d['directory']	= 'evdisp'
    d['event']		= event
    
    # d['image'] = '<img src="'+'{% static '+"'images/dune_logo.png %}'"+'">'
    return render(request, 'evdisp.html', d)

