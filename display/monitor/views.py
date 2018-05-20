import django.db.models
from django.db.models	import Max

from django.conf	import settings
from django.utils.safestring		import mark_safe
from django_tables2 import A
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
    d_type = forms.CharField(required=False, initial='', label="Data Type")

    def job_identifier(self):
        return self.cleaned_data["j_uuid"]
    
    def data_type(self):
        return self.cleaned_data["d_type"]
#---
class RunForm(forms.Form):
    run		= forms.CharField(required=False, initial='', label="Run")
    event	= forms.CharField(required=False, initial='', label="Event")

    def getval(self, what):
        return self.cleaned_data[what]
   
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
    changroup = tables.Column(verbose_name='Grp')

    def render_changroup(self, value, record):
        # image_url = ('<a href="http://%s/%s/%s/%s">%s</a>'
        #                  % (self.site,
        #                     settings.SITE['dqm_evdisp_url'],
        #                     record.j_uuid,
        #                     evdisp.makename(record.evnum, record.datatype, value),
        #                     value
        #                  ))
        
        image_url = ('<a href="http://%s/monitor/display1?url=http://%s/%s/%s/%s&run=%s&event=%s&changroup=%s&datatype=%s">%s</a>'
                         % (self.site,
                            self.site, # this needs to point to the image, also below
                            settings.SITE['dqm_evdisp_url'],
                            record.j_uuid,
                            evdisp.makename(record.evnum, record.datatype, value),
                            record.run,
                            record.evnum,
                            record.changroup,
                            record.datatype,
                            value
                         ))


        return mark_safe(image_url)
    class Meta:
        model = evdisp
        attrs = {'class': 'paleblue'}
        exclude = ('path',)
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

        objs = pur.objects.order_by('-pk').filter(tpc=tpcNum)
        if(tsmin!=''):	objs = objs.filter(ts__gte=tsmin)
        if(tsmax!=''):	objs = objs.filter(ts__lte=tsmax)

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
    d_type	= request.GET.get('d_type','')
    run		= request.GET.get('run','')
    evnum	= request.GET.get('evnum','')


    q=''	# stub for a query that may be built
    if request.method == 'POST':
        perPageSelector	= dropDownGeneric(request.POST,
                                          initial={'perpage':perpage},
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

        if(what=='evdisp'):
            juuidSelector = JuuidForm(request.POST)
            if juuidSelector.is_valid():
                
                j_uuid=juuidSelector.job_identifier()
                if(j_uuid!=''): q+= 'j_uuid='+j_uuid+'&'
                
                d_type=juuidSelector.data_type()
                if(d_type!=''): q+= 'd_type='+d_type+'&'

            runSelector = RunForm(request.POST)
            if runSelector.is_valid():
                
                run=runSelector.getval("run")
                if(run!=''): q+= 'run='+run+'&'
                
                event=runSelector.getval("event")
                if(event!=''): q+= 'evnum='+event+'&'
                

        return makeQuery(url, q)
    # We built a query and come to same page with the query parameters
    # -------------------------------------------------------------------------


    
    d = {}	# stub for a dictionaty to feed the template

    objs = eval(what).objects.order_by('-pk').all()

    if(tsmin!=''):	objs = eval(what).objects.filter(ts__gte=tsmin).order_by('-pk')
    if(tsmax!=''):	objs = objs.filter(ts__lte=tsmax)	# .order_by('-pk')
    if(j_uuid!=''):	objs = objs.filter(j_uuid=j_uuid)
    if(d_type!=''):	objs = objs.filter(datatype=d_type)
    if(run!=''):	objs = objs.filter(run=run)
    if(evnum!=''):	objs = objs.filter(evnum=evnum)

    t = eval(tbl)(objs)
    t.set_site(domain)
    
    RequestConfig(request, paginate={'per_page': int(perpage)}).configure(t)

    d['table']	= t
    d['N']	= str(len(objs))
    d['domain']	= domain
    
    d['pageName']	= ': '+tbl
    d['message']	= eval(what).message()

    perPageSelector = dropDownGeneric(initial={'perpage':perpage},
                                      label='# per page',
                                      choices = PAGECHOICES,
                                      tag='perpage')
    
    
    selectors = []
    
    selectors.append(perPageSelector)
    
    tsSelector= TsForm(request.POST)
    selectors.append(tsSelector)

    if(what=='evdisp'):
        juuidSelector = JuuidForm(request.POST)
        selectors.append(juuidSelector)
        
        runSelector = RunForm(request.POST)
        selectors.append(runSelector)
    
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

    
    
    return render(request, 'display.html', d)

#########################################################    
@csrf_exempt
def display1(request):
    
    domain	= request.get_host()
    url		= request.GET.get('url','')
    run		= request.GET.get('run','')
    event	= request.GET.get('event','')
    changroup	= request.GET.get('changroup','')
    datatype	= request.GET.get('datatype','')

    d = {}
    d['domain']		= domain

    for item in ('url', 'run', 'event', 'changroup', 'datatype'):
        stuff = request.GET.get(item,'')
        if(item=='changroup'):
            d[item] = stuff+' ('+evdisp.group2string(int(stuff))+')'
        else:
            d[item]	= stuff
    
    d['pageName']	= ': Event Display'
    d['message']	= evdisp.message()
    
    return render(request, 'display1.html', d)

#########################################################    
#    d['form'] = f.as_table()
#
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

