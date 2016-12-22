from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^detail$',	views.detail,	name='detail'),
    url(r'^addjob$',	views.addjob,	name='add'),
    url(r'^adj$',	views.adj,	name='adj'),
    url(r'^delete$',	views.delete,	name='delete'),
    url(r'^deleteall$', views.deleteall,name='deleteall'),
#    url(r'^(?P<job_id>[0-9]+)/$', views.detail, name='detail'),
#    url(r'^$', views.index, name='index'),
]
