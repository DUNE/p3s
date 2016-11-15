from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^addpilot',	views.addpilot,	name='addpilot'),
    url(r'^request',	views.req_work,	name='request'),

    #    url(r'^(?P<job_id>[0-9]+)/$', views.detail, name='detail'),
#    url(r'^$', views.index, name='index'),
]

# Moved to monitor:
# url(r'^$',		views.detail,	name='detail'),
