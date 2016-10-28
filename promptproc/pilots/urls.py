from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.detail, name='detail'),
#    url(r'^(?P<job_id>[0-9]+)/$', views.detail, name='detail'),
#    url(r'^$', views.index, name='index'),
]
