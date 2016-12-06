from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^pilots',	views.pilots,		name='pilots'),
    url(r'^jobs',	views.jobs,		name='jobs'),
    url(r'^workflows',	views.workflows,	name='workflows'),
    url(r'^jobdetail',	views.jobdetail,	name='jobdetail'),
    url(r'^pilotdetail',views.pilotdetail,	name='pilotdetail'),
]
