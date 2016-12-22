from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^jobs',	views.jobs,		name='jobs'),
    url(r'^data$',	views.data,		name='data'),
    url(r'^pilots',	views.pilots,		name='pilots'),
    url(r'^dags',	views.dags,		name='dags'),
    url(r'^workflows',	views.workflows,	name='workflows'),
    url(r'^jobdetail',	views.jobdetail,	name='jobdetail'),
    url(r'^datadetail',	views.datadetail,	name='datadetail'),
    url(r'^pilotdetail',views.pilotdetail,	name='pilotdetail'),
    url(r'^dagdetail',	views.dagdetail,	name='dagdetail'),
    url(r'^wfdetail',	views.wfdetail,		name='wfdetail'),
]
