from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^registerdata',	views.registerdata,	name='registerdata'),
    url(r'^registertype',	views.registertype,	name='registertype'),
    url(r'^deletetype',		views.deletetype,	name='deletetype'),
    url(r'^adjustdata',		views.adjustdata,	name='adjustdata'),
]
