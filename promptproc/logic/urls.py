from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^purge$',	views.purge,	name='purge'),
    url(r'^pilotTO$',	views.pilotTO,	name='pilotTO'),
    url(r'^service$',	views.serviceReport,	name='serviceReport'),
    url(r'^delete$',	views.serviceDelete,	name='serviceDelete'),
]
