from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^register$',		views.register,		name='register'),
    url(r'^delete$',		views.delete,		name='delete'),
    url(r'^adjust',		views.adjust,		name='adjust'),
    url(r'^registertype',	views.registertype,	name='registertype'),
    url(r'^deletetype',		views.deletetype,	name='deletetype'),
    url(r'^getdata',		views.getdata,		name='getdata'),
]
