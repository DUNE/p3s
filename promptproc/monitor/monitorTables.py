from django.shortcuts			import render
from django.utils.safestring		import mark_safe
from django.utils			import timezone
from django.utils.timezone		import utc
from django.conf			import settings

from django.db.models import F

import	django_tables2 as tables

from sites.models			import site
from jobs.models			import job, jobtype
from data.models			import dataset, datatype
from pilots.models			import pilot

from workflows.models			import dag,dagVertex,dagEdge,workflow

from logic.models			import service


# We need this to make links to this service itself.
try:
    from django.urls import reverse
except ImportError:
    print("FATAL IMPORT ERROR")
    exit(-3)

##### BASE CLASSES FOR MONITOR AND DETAIL TABLES ########
class MonitorTable(tables.Table):
    def set_site(self, site=''):
        self.site=site

    def makelink(self, what, key, value):
        return mark_safe('<a href="http://%s%s?%s=%s">%s</a>'
                         % (self.site, reverse(what), key, value, value))

    def renderDateTime(self, dt): # common format defined here.
        return timezone.localtime(dt).strftime(settings.TIMEFORMAT)
    
#--------------------------------------------------------

class DetailTable(tables.Table):
    attribute	= tables.Column()
    value	= tables.Column()
    
    def set_site(self, site=''):
        self.site=site
    class Meta:
        attrs	= {'class': 'paleblue'}

##### FOR THE DASHBOARD
#--------------------------------------------------------
class TimelineTable(tables.Table):
    State	= tables.Column(verbose_name='State')
    OneMin	= tables.Column(verbose_name='1min')
    TenMin	= tables.Column(verbose_name='10min')
    OneHour	= tables.Column(verbose_name='1hr')
    TwoHours	= tables.Column(verbose_name='2hrs')
    Day		= tables.Column(verbose_name='24hrs')
    
    def changeName(self, newName):
        self.base_columns['State'].verbose_name = newName

    def set_site(self, site=''):
        self.site=site
    class Meta:
        attrs	= {'class': 'paleblue'}
#--------------------------------------------------------
class ShortSummaryTable(tables.Table):
    State	= tables.Column(verbose_name='State')
    Count	= tables.Column(verbose_name='Count')
    class Meta:
        attrs	= {'class': 'paleblue'}
#--------------------------------------------------------
class JobTypeLimitTable(tables.Table):
    Type	= tables.Column()
    Limit	= tables.Column()
    class Meta:
        attrs	= {'class': 'paleblue'}
#--------------------------------------------------------
class SummaryTable(tables.Table):
    Object	= tables.Column()
    Number	= tables.Column()
    
    def set_site(self, site=''):
        self.site=site
    class Meta:
        attrs	= {'class': 'paleblue'}
#--------------------------------------------------------
class ServiceTable(MonitorTable):
    name	= tables.Column(verbose_name='Name')
    ts		= tables.Column(verbose_name='Time')
    info	= tables.Column(verbose_name='Info')
   

    class Meta:
        model = service
        attrs = {'class': 'paleblue'}

#--------------------------------------------------------
class ParamTable(tables.Table):
    parameter	= tables.Column(verbose_name='System Parameter')
    nominal	= tables.Column(verbose_name='Nominal')
    actual	= tables.Column(verbose_name='Actual')
    status	= tables.Column(verbose_name='Status')
    action	= tables.Column(verbose_name='Action')
    
    class Meta:
        attrs	= {'class': 'paleblue'}
        
#########################################################    
############### SUMMARY TABLES ##########################    
#########################################################    
# NOTE THAT WE INSTRUMENT SOME COLUMNS WHILE DECIDING   #
# TO NOT DISPLAY THEM. THIS IS TEMPORARY/HISTORICAL     #
#########################################################    
class JobTable(MonitorTable):

    ts_def	= tables.Column(verbose_name='defined')
    ts_dis	= tables.Column(verbose_name='dispatched')
    ts_sta	= tables.Column(verbose_name='started')
    ts_sto	= tables.Column(verbose_name='stopped')
    jobtype	= tables.Column(verbose_name='type')
    priority	= tables.Column(verbose_name='Pri.')
    timelimit	= tables.Column(verbose_name='maxSec')
    errcode	= tables.Column(verbose_name='err')
    exectime	= tables.Column(empty_values=(), verbose_name='exec.time')

    def render_id(self, value):		return self.makelink('jobdetail',	'pk',	value)
    def render_uuid(self, value):	return self.makelink('jobdetail',	'uuid',	value)
    def render_p_uuid(self, value):	return self.makelink('pilots',		'uuid',	value)
    def render_wfuuid(self, value):	return self.makelink('wfdetail',	'uuid',	value)
    
    def render_ts_def(self, value):	return self.renderDateTime(value)
    def render_ts_dis(self, value):	return self.renderDateTime(value)
    def render_ts_sta(self, value):	return self.renderDateTime(value)
    def render_ts_sto(self, value):	return self.renderDateTime(value)

    def render_exectime(self, record):

        if(record.ts_sto is None): return ''
        if(record.ts_sta is None): return ''
        
        duration = record.ts_sto - record.ts_sta
        return str(duration).split('.')[0]

    def render_payload(self, value):
        if '/' in value:
            bits = value.split('/')
            l = len(bits)-1
            return bits[l]
        else:
            return value
            
    def order_exectime(self, queryset, is_descending):
        queryset = queryset.annotate(l=F('ts_sto')-F('ts_sta')).order_by(('-' if is_descending else '') + 'l')
        return (queryset, True)
    
    class Meta:
        model = job
        attrs = {'class': 'paleblue'}
        exclude = ('p_uuid', 'params', 'env', 'ts_dis', 'directive', 'pid', 'host', 'wfuuid', 'site',)
#--------------------------------------------------------
class DataTable(MonitorTable):
    def render_uuid(self,value):	return self.makelink('datadetail',	'uuid',	value)
    #    def render_wfuuid(self,value):	return self.makelink('wfdetail',	'uuid',	value)
    def render_datatype(self,value):	return self.makelink('datatypes',	'',	value)
    def render_targetuuid(self,value):	return self.makelink('jobdetail',	'uuid',	value)

    class Meta:
        model = dataset
        attrs = {'class': 'paleblue'}
        exclude = ('wfuuid',)
#--------------------------------------------------------
class DataTypeTable(MonitorTable):

    class Meta:
        model = datatype
        attrs = {'class': 'paleblue'}
#--------------------------------------------------------
class SiteTable(MonitorTable):
    pilotcycles	= tables.Column(verbose_name='Pilot Cycles/Period')
    pilotstats	= tables.Column(accessor='name', verbose_name='Pilots Total/Running/Idle') # 
    jobstats	= tables.Column(accessor='name', verbose_name='Jobs Total/Running/Finished') # 

    def render_name(self,value):	return self.makelink('sitedetail', 'name', value)

    def render_pilotstats(self,record):
        nTotal	= pilot.N(site=record.name)
        nRun	= pilot.N(site=record.name, state='running')
        nIdle	= pilot.N(site=record.name, state='no jobs')
        
        return str(nTotal)+'/'+str(nRun)+'/'+str(nIdle)
    
    def render_jobstats(self,record):
        nTotal	= job.N(site=record.name)
        nRun	= job.N(site=record.name, state='running')
        nFin	= job.N(site=record.name, state='finished')
        
        return str(nTotal)+'/'+str(nRun)+'/'+str(nFin)
    
    def render_pilotcycles(self,value, record):
        return str(value)+'/'+str(record.pilotperiod)
    
    class Meta:
        model = site
        attrs = {'class': 'paleblue'}
        exclude	= ('env', 'pilotperiod',)
#--------------------------------------------------------
class PilotTable(MonitorTable):
    ts_cre	= tables.Column(verbose_name='created')
    ts_reg	= tables.Column(verbose_name='registered')
    ts_lhb	= tables.Column(verbose_name='last heartbeat')
    jobcount	= tables.Column(verbose_name='jobs')
    life	= tables.Column(empty_values=(), verbose_name='Life')
    
    def render_uuid(self,value):	return self.makelink('pilots',		'uuid',	value)
    def render_j_uuid(self,value):	return self.makelink('jobs',		'uuid',	value)
    def render_id(self,value):		return self.makelink('pilotdetail',	'pk', value)

    def render_ts_cre(self, value):	return self.renderDateTime(value)
    def render_ts_reg(self, value):	return self.renderDateTime(value)
    def render_ts_lhb(self, value):	return self.renderDateTime(value)

    def render_life(self, record):

        if(record.ts_lhb is None): return ''
        if(record.ts_reg is None): return ''
        
        duration = record.ts_lhb - record.ts_reg
        return str(duration).split('.')[0]

    def order_life(self, queryset, is_descending):
        queryset = queryset.annotate(l=F('ts_lhb')-F('ts_reg')).order_by(('-' if is_descending else '') + 'l')
        return (queryset, True)
    
    class Meta:
        model	= pilot
        attrs	= {'class': 'paleblue'}
        exclude	= ('j_uuid', 'jobs_done', 'site', 'host',)


#################### DAG
class DagTable(MonitorTable):
    # def render_id(self,value):	return self.makelink('dagdetail', 'pk', value)


    def render_ts_def(self, value):	return self.renderDateTime(value)
    
    ts_def	= tables.Column(verbose_name='defined')
    nvertices	= tables.Column(verbose_name='nvert')
    
    def render_name(self,value):return self.makelink('dagdetail', 'name', value)
        
    class Meta:
        model = dag
        attrs = {'class': 'paleblue'}


#--------------------------------------------------------
# Simpler inheritance (compared to jobs etc) is provisional
class DagEdgeTable(tables.Table):
#    def render_id(self,value):	return self.makelink('dagdetail', 'pk', value)
#    def render_name(self,value):return self.makelink('dags', 'name', value)
        
    class Meta:
        model = dagEdge
        exclude = ('dag',)
        attrs = {'class': 'paleblue'}

#--------------------------------------------------------
class DagVertexTable(tables.Table):
#    def render_id(self,value):	return self.makelink('dagdetail', 'pk', value)
#    def render_name(self,value):return self.makelink('dags', 'name', value)
        
    class Meta:
        model = dagVertex
        exclude = ('dag',)
        attrs = {'class': 'paleblue'}

#################### WORKFLOW
class WfTable(MonitorTable):
    # FIXME rendering later
    # def render_id(self,value):	return self.makelink('dagdetail', 'pk', value)


    def render_ts_def(self, value):	return self.renderDateTime(value)
    
    ts_def	= tables.Column(verbose_name='defined')
    dag		= tables.Column(verbose_name='DAG')
    
    def render_uuid(self,value):return self.makelink('wfdetail', 'uuid', value)
    def render_dag(self,value):return self.makelink('dagdetail', 'name', value)
        
    class Meta:
        model = workflow
        attrs = {'class': 'paleblue'}
        # we actually want that: exclude	= ('uuid', )


