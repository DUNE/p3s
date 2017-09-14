from django.shortcuts	import render
from django.http	import HttpResponse

import  django_tables2 as tables
from	django_tables2			import RequestConfig
from	django_tables2.utils		import A

from purity.models import pur

#########################################################    
# general request handler for summary type of a table
def data_handler(request, what):
    # testing only
    objs = pur.objects.all()

    d = {}
    
    t = tables.Table(objs)
    RequestConfig(request).configure(t)

    d['table'] = t
    return render(request, 'monitor_base.html', d)

    #return HttpResponse('requested: '+str(len(objs)))

