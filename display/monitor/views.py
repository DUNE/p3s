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
from evdisp.models import evdisp

from django import forms

###################################################################
class EvdispForm(forms.Form):
    run		= forms.CharField(required=False, initial='')
    event	= forms.CharField(required=False, initial='')
#---
class TsForm(forms.Form):
    ts_min	= forms.CharField(required=False, initial='', label="min. (YYYY-MM-DD HH:MM:SS)")
    ts_max	= forms.CharField(required=False, initial='', label="max. (YYYY-MM-DD HH:MM:SS)")

    def tsmin(self):
        return self.cleaned_data["ts_min"]
    
    def tsmax(self):
        return self.cleaned_data["ts_max"]
#---
class JuuidForm(forms.Form):
    j_uuid = forms.CharField(required=False, initial='', label="Job UUID")

    def job_identifier(self):
        return self.cleaned_data["j_uuid"]
#---
PAGECHOICES	= [('25','25'), ('50','50'), ('100','100'), ('200','200'),('400','400'),]

#####################################################################

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
    class Meta:
        model = pur
        attrs = {'class': 'paleblue'}
#########################################################    
class EvdispTable(MonitorTable):
    class Meta:
        model = evdisp
        attrs = {'class': 'paleblue'}
#########################################################    
def makeQuery(page, q=''):
    gUrl= '/monitor/'+page
    qUrl= '/monitor/'+page+"?"

    if(q==''): return HttpResponseRedirect(gUrl)
    return HttpResponseRedirect(qUrl+q)
#########################################################    
# general request handler for summary type of a table
def puritychart(request, what):
    domain	= request.get_host()
    tsmin	= request.GET.get('tsmin','')
    tsmax	= request.GET.get('tsmax','')

    q=''

    if request.method == 'POST':
        tsSelector = TsForm(request.POST)
        if tsSelector.is_valid():
            tsmin=tsSelector.tsmin()
            tsmax=tsSelector.tsmax()
            if(tsmin!=''): q+= 'tsmin='+tsmin+'&'
            if(tsmax!=''): q+= 'tsmax='+tsmax+'&'

        return makeQuery('puritychart', q) # will go and get the query results...
    
    #-----------
    # for the charts

    purSeries = []
    for tpcNum in (1,2,5,6,9,10):
        purDict = {}

        # FIXME - improve and/or move the charts
        objs = pur.objects.order_by('-pk').filter(tpc=tpcNum)

        if(tsmin!=''):
            objs = objs.filter(ts__gte=tsmin)
            
        if(tsmax!=''):
            objs = objs.filter(ts__lte=tsmax)
        

        purStr=''

        for forChart in objs:
            try: # template: [new Date(2014, 10, 15, 7, 30), 1],
                purStr += ('[new Date(%s), %s],') % (forChart.ts.strftime("%Y, %m-1, %d, %H, %M, %S"), forChart.lifetime)
            except:
                break
    
        purDict["panel"] = 'tpc'+str(tpcNum)
        purDict["timeseries"]=purStr
    
        purSeries.append(purDict)

    d = {}
    d['purS']	= purSeries
    d['domain']	= domain
    
    tsSelector = TsForm(request.POST)
    
    selectors = []
    selectors.append(tsSelector)
    d['selectors'] = selectors
    d['pageName'] = ': purity timeline'

    return render(request, 'purity_chart.html', d)

#########################################################    
# general request handler for summary type of a table
def data_handler2(request, what, tbl, url):
    domain	= request.get_host()
    perpage	= request.GET.get('perpage','25')
    tsmin	= request.GET.get('tsmin','')
    tsmax	= request.GET.get('tsmax','')
    j_uuid	= request.GET.get('j_uuid','')


    q=''	# stub for a query that may be built
    if request.method == 'POST':
        perPageSelector	= dropDownGeneric(request.POST,
                                          initial={'perpage':25},
                                          label='# per page',
                                          choices = PAGECHOICES,
                                          tag='perpage')
        
        if perPageSelector.is_valid(): q += perPageSelector.handleDropSelector()

        tsSelector = TsForm(request.POST)
        if tsSelector.is_valid():
            tsmin=tsSelector.tsmin()
            tsmax=tsSelector.tsmax()
            
            if(tsmin!=''): q+= 'tsmin='+tsmin+'&'
            if(tsmax!=''): q+= 'tsmax='+tsmax+'&'

        juuidSelector = JuuidForm(request.POST)
        if juuidSelector.is_valid():
            j_uuid=juuidSelector.job_identifier()
            
            if(j_uuid!=''): q+= 'j_uuid='+j_uuid+'&'

        return makeQuery(url, q)
    # We built a query and come to same page with the query parameters
    # -------------------------------------------------------------------------


    
    d = {}	# stub for a dictionaty to feed the template

    objs = eval(what).objects.order_by('-pk').all()

    if(tsmin!=''): objs = eval(what).objects.filter(ts__gte=tsmin).order_by('-pk')
    if(tsmax!=''): objs = objs.filter(ts__lte=tsmax)# .order_by('-pk')
    if(j_uuid!=''):objs = objs.filter(j_uuid=j_uuid)# .order_by('-pk')

    t = eval(tbl)(objs)
    t.set_site(domain)
    
    RequestConfig(request, paginate={'per_page': int(perpage)}).configure(t)

    d['table']	= t
    d['N']	= str(len(objs))
    d['domain']	= domain
    
    d['pageName']	= ': '+tbl


    perPageSelector = dropDownGeneric(initial={'perpage':25},
                                      label='# per page',
                                      choices = PAGECHOICES,
                                      tag='perpage')
    
    tsSelector		= TsForm(request.POST)
    juuidSelector	= JuuidForm(request.POST)
    
    selectors = []
    selectors.append(perPageSelector)
    selectors.append(tsSelector)
    selectors.append(juuidSelector)
    
    d['selectors'] = selectors


    return render(request, 'unitable2.html', d)

#########################################################    
@csrf_exempt
def eventdisplay(request):
    
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
    
    return render(request, 'display.html', d)

#########################################################    
# general request handler for summary type of a table
# def data_handler(request, what):
#     domain	= request.get_host()

#     # testing only
#     objs = pur.objects.order_by('-pk').all()

#     d = {}
    
#     t = PurityTable(objs)
#     t.set_site(domain)
#     RequestConfig(request).configure(t)

#     d['table']	= t
#     d['N']	= str(len(objs))
#     d['domain']	= domain
    
#     d['pageName']	= ': Purity Monitor'
    
#     return render(request, 'unitable.html', d)


# ------------------------------------
# Table classes -  just an example:
# error = tables.Column(verbose_name='Error')


# for future development:
#    def __init__(self, *args, **kwargs):
#       self.obj	= kwargs.pop('obj')
#       print(self.obj)

#       setattr(PurityTable.Meta, 'model', eval(self.obj))
#       setattr(PurityTable.Meta, 'attrs', {'class': 'paleblue'})

#       super(PurityTable, self).__init__(*args, **kwargs)

