from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^detail$',	views.detail,	name='detail'),
    url(r'^add$',	views.add,	name='add'),
    url(r'^adjust$',	views.adjust,	name='adjust'),
    url(r'^delete$',	views.delete,	name='delete'),
    url(r'^purge$',	views.purge,	name='purge'),
    url(r'^ltype$',	views.ltype,	name='ltype'),
    url(r'^limit$',	views.limit,	name='limit'),
    
#    url(r'^(?P<job_id>[0-9]+)/$', views.detail, name='detail'),
#    url(r'^$', views.index, name='index'),
]
