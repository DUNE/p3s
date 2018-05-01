import django.db.models
from django.db.models	import Max

from django.shortcuts	import render

from django.http	import HttpResponseRedirect
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

PAGECHOICES	= [('25','25'), ('50','50'), ('100','100'), ('200','200'),('400','400'),]

######################
class dropDownGeneric(forms.Form):
    def __init__(self, *args, **kwargs):
       self.label	= kwargs.pop('label')
       self.choices	= kwargs.pop('choices')
       self.tag		= kwargs.pop('tag')
       self.fieldname	= self.tag # 'choice'
       
       super(dropDownGeneric, self).__init__(*args, **kwargs)
       
       self.fields[self.fieldname] = forms.ChoiceField(choices = self.choices, label = self.label)

    def handleDropSelector(self):
        selection = self.cleaned_data[self.fieldname]
        if(selection=='All'):
            return ''
        else:
            return self.tag+'='+selection+'&'
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
def makeQuery(what, q=''):
    gUrl= '/monitor/purity'
    qUrl= '/monitor/purity?'

    if(q==''):
        return HttpResponseRedirect(gUrl)
    
    return HttpResponseRedirect(qUrl+q)

#########################################################    
# general request handler for summary type of a table
def data_handler2(request, what):
    domain	= request.get_host()

    q=''
    
    #-----------
    # for the charts

    purSeries = []
    for tpcNum in (1,2,5,6,9,10):
        purDict = {}
        forChart = pur.objects.order_by('-pk').filter(tpc=tpcNum)

        purStr=''
        for i in range(40):
            try: # template: [new Date(2014, 10, 15, 7, 30), 1],
                purStr += ('[new Date(%s), %s],') % (forChart[i].ts.strftime("%Y, %m-1, %d, %H, %M, %S"), forChart[i].lifetime)
#                purStr += ('[[%s], %s],') % (forChart[i].ts.strftime("%H, %M, %S"), forChart[i].lifetime)
            except:
                break
    
        purDict["panel"] = 'tpc'+str(tpcNum)
        purDict["timeseries"]=purStr
    
        purSeries.append(purDict)
        
    #-----------
    # for the table
    d = {}
    
    objs = pur.objects.order_by('-pk').all()
    t = PurityTable(objs)
    t.set_site(domain)
    RequestConfig(request).configure(t)

    d['table']	= t
    d['N']	= str(len(objs))
    d['domain']	= domain
    
    d['pageName']	= ': Purity Monitor'
    d['purS']		= purSeries
    

    if request.method == 'POST':
        perPageSelector	= dropDownGeneric(request.POST, initial={'perpage':25}, label='# per page', choices = PAGECHOICES, tag='perpage')
        if perPageSelector.is_valid(): q += perPageSelector.handleDropSelector()
        return makeQuery(what, q) # will go and get the query results...

    perPageSelector	= dropDownGeneric(initial={'perpage':25}, label='# per page', choices = PAGECHOICES, tag='perpage')
    
    selectors = []
    selectors.append(perPageSelector)
    d['selectors'] = selectors

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

