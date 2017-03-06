from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^register',	views.register,	name='register'),
    url(r'^request',	views.request,	name='request'),
    url(r'^report',	views.report,	name='report'),
    url(r'^delete$',	views.delete,	name='delete'),

    #    url(r'^(?P<job_id>[0-9]+)/$', views.detail, name='detail'),
#    url(r'^$', views.index, name='index'),
]

# Moved to monitor:
# url(r'^$',		views.detail,	name='detail'),
