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
    
    return render(request, 'monitor_base.html', d)


@csrf_exempt
def addpurity(request):
    maxnum = 0
    try:
        maxnum = pur.objects.latest('id').id
    except:
        pass

    post	= request.POST

    print()
    p=pur()
    p.run	= post['run']
    p.tpc	= post['tpc']
    p.lifetime	= post['lifetime']
    p.error	= post['error']
    p.count	= post['count']

    p.save()

    
    return HttpResponse(str(maxnum))
###################################################
@csrf_exempt
def delpurity(request):
    post	= request.POST
    p_pk	= None

    try:
        p_pk = post['pk']
    except:
        return HttpResponse("Missing key for deletion")

    p = None
    try:
        p = pur.objects.get(pk=p_pk)
    except:
        return HttpResponse("Entry %s not found" % p_pk )

    p.delete()
    return HttpResponse("%s deleted" % p_pk )

#    return HttpResponse('Delete request:'+str(p_pk))


        
